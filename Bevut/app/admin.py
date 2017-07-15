import csv
import codecs

from django.contrib import admin
from django.conf.urls import url
from django.urls import reverse
from django import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.html import format_html
from django.forms import Textarea
from django.contrib.messages import ERROR
from django.db import IntegrityError, models

from app.models import Student, Course, FormTemplate, FormOption, StudentForm


class OptionInline(admin.TabularInline):
    model = FormOption
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 14, 'cols': 30})}
    }

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.applied:
            return False
        return super(OptionInline, self).has_delete_permission(request, obj)


@admin.register(FormTemplate)
class TemplateAdmin(admin.ModelAdmin):
    save_as = True
    fields = ['name', 'has_well_done']
    list_display = ["__str__", "apply_template_link"]
    inlines = (OptionInline,)

    def apply_template_link(self, obj):
        if not obj.applied:
            return format_html(
                    '<a href="{}">Applicera formulär på kurs</a>',
                    reverse("admin:apply_form", args=(obj.id,)))
        else:
            return 'Formuläret är redan applicerat'

    apply_template_link.short_description = "Applicera"

    def has_delete_permission(self, request, obj=None):
        return obj is None or not obj.applied or request.user.is_superuser

    def get_urls(self):
        urls = super(TemplateAdmin, self).get_urls()
        template_urls = [
            url(
                r'^(?P<template_id>[0-9]+)/apply/$',
                self.admin_site.admin_view(self.apply_template),
                name="apply_form"),
        ]
        return template_urls + urls

    def apply_template(self, request, *args, **kwargs):
        template = get_object_or_404(FormTemplate, pk=kwargs['template_id'])
        if request.method == "POST":
            course_id = request.POST.get("course_id")
            course = get_object_or_404(Course, pk=course_id)
            template.course = course
            template.applied = True
            template.save()

            # TODO: get app name and template name for dynamic assignment
            form_url = reverse("admin:app_formtemplate_changelist")

            if course.students.count() == 0:
                self.message_user(request, "Kan ej applicera mall på kurs utan studenter", ERROR)
                return redirect(form_url)
            for student in course.students.all():
                sf = StudentForm(
                        student=student,
                        course=course,
                        template=template,
                        midterm_signed=False,
                        fullterm_signed=False,
                        locked=False)

                sf.save()
            self.message_user(request, "Applicerade formulär på kursen %s" % course.name)
            return redirect(form_url)
        else:
            courses = Course.objects.filter(form_templates=None)
            context = dict(
                    self.admin_site.each_context(request),
                    title="Applicera mall på kurs",
                    form_template=template,
                    courses=courses
            )
            return render(request, "app/admin/apply_template.html", context)

    def save_model(self, request, obj, form, change):
        if obj.applied and '_saveasnew' not in request.POST:
            self.message_user(request, "Formuläret sparades inte då det redan har applicerats på en kurs", ERROR)
            return False
        return super(TemplateAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.template.applied and '_saveasnew' not in request.POST:
                return
        return super(TemplateAdmin, self).save_formset(request, form, formset, change)


class MultipleStudentForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(StudentAdmin, self).get_urls()
        student_urls = [
            url(r"^add-multiple", self.admin_site.admin_view(self.add_multiple_students), name="add_multiple_students"),
        ]
        return urls + student_urls

    def add_multiple_students(self, request, *args, **kwargs):
        if request.method == "POST":
            form = MultipleStudentForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["csv_file"]
                if True in [file.name.endswith(d) for d in [".csv", ".xls", ".xlsx"]]:
                    file.open()
                    added = 0
                    already_existed = []
                    for row in csv.reader(codecs.iterdecode(file, 'utf-8')):
                        if len(row) < 3:
                            continue

                        ssn = row[0]
                        name = row[1]
                        email = row[2]
                        s = Student()
                        s.name = name
                        s.ssn = ssn
                        s.email = email

                        try:
                            s.save()
                            added += 1
                        except IntegrityError:
                            already_existed.append(ssn)

                    if added == 0:
                        self.message_user(request, "Inga studenter lades till.", ERROR)
                    else:
                        self.message_user(request, "La till {} student(er).".format(added))

                    if len(already_existed) > 0:
                        self.message_user(
                                request,
                                "{} student(er) fanns redan ({})".format(
                                    len(already_existed),
                                    ", ".join(already_existed)), ERROR)

                    return redirect(reverse("admin:app_student_changelist"))
                else:
                    self.message_user(request, "Filen är ej en csv fil", ERROR)
            else:
                self.message_user(request, "Formuläret är ej giltigt.", ERROR)

        context = dict(
                self.admin_site.each_context(request),
                title="Lägg till studenter från csv fil",
                )
        return render(request, "app/admin/add_multiple_students.html", context)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    save_as = True
    radio_fields = {'term': admin.HORIZONTAL}
    filter_horizontal = ['students']


admin.site.disable_action('delete_selected')

# vi: ts=4 expandtab
