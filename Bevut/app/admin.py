import csv
import codecs
import re

from xlrd import open_workbook

from django.contrib import admin
from django.conf.urls import url
from django.urls import reverse
from django import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.html import format_html
from django.forms import Textarea
from django.contrib.messages import ERROR
from django.db import IntegrityError, models
from django.core.exceptions import ValidationError
from django.http import HttpResponse

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

    exclude = ('identity',)

    def get_urls(self):
        urls = super(StudentAdmin, self).get_urls()
        student_urls = [
            url(r"^add-multiple", self.admin_site.admin_view(self.add_multiple_students), name="add_multiple_students"),
        ]
        return urls + student_urls

    def add_multiple_students(self, request, *args, **kwargs):
        course_id = request.POST.get('course_id', '') if request.method == 'POST' else request.GET.get('course', '')
        course = Course.objects.filter(id=course_id).first() if re.match('^[0-9]+$', course_id) else None
        if request.method == "POST":
            form = MultipleStudentForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["csv_file"]
                data = []
                if file.name.endswith('.csv'):
                    file.open()
                    data = csv.reader(codecs.interdecode(file, 'utf-8'))
                elif True in [file.name.endswith(d) for d in [".xls", ".xlsx"]]:
                    file.open()
                    books = open_workbook(file_contents=file.read())
                    if books.nsheets <= 0:
                        self.message_user(request, 'Hittade ej någon sida i ditt excel dokument.')
                        return redirect(reverse('admin:add_multiple_students'))

                    sheet = books.sheet_by_index(0)
                    for r in range(sheet.nrows):
                        row = sheet.row(r)
                        if len(row) < 3:
                            continue
                        data.append([d.value for d in row])
                else:
                    self.message_user(request, "Filen är ej en csv fil", ERROR)
                    return redirect(reverse('admin:add_multiple_students'))

                added = 0
                already_existed = []
                for row in data:
                    s = Student()
                    s.ssn = row[0].replace('-', '')
                    s.name = row[1]
                    s.email = row[2]
                    s.populate_hash()
                    try:
                        s.clean_fields()
                        s.clean()
                        s.save()
                        added += 1
                        if course is not None:
                            course.students.add(s)
                    except IntegrityError:
                        if course is not None:
                            existing = Student.objects.get(ssn=s.ssn)
                            course.students.add(existing)
                        already_existed.append(s.ssn)
                    except ValidationError as ve:
                        self.message_user(request, "{}: {}".format(s.ssn, ", ".join(ve.messages)), ERROR)

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

                if course is None:
                    return redirect(reverse("admin:app_student_changelist"))

                return redirect(reverse("admin:app_course_change", args=(course.id,)))
            else:
                self.message_user(request, "Formuläret är ej giltigt.", ERROR)

        context = dict(
                self.admin_site.each_context(request),
                title="Lägg till studenter från csv fil",
                course=course)

        return render(request, "app/admin/add_multiple_students.html", context)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    save_as = True
    radio_fields = {'term': admin.HORIZONTAL}
    filter_horizontal = ['students']
    list_display = ["__str__", "import_students_str"]

    def import_students_str(self, obj):
        return format_html(
                '<a href="{}?course={}">Importera studenter till kursen</a>',
                # reverse("admin:course_import_students", kwargs=dict(course_id=obj.id)))
                reverse("admin:add_multiple_students"),
                obj.id)

    import_students_str.short_description = "Importera"

    def get_urls(self):
        urls = super(CourseAdmin, self).get_urls()
        template_urls = [
            url(
                r'^(?P<course_id>[0-9]+)/import/$',
                self.admin_site.admin_view(self.import_students),
                name="course_import_students"),
        ]
        return template_urls + urls

    def import_students(self, request, *args, **kwargs):
        return HttpResponse('swag')


admin.site.disable_action('delete_selected')

# vi: ts=4 expandtab
