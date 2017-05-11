from django.contrib import admin
from django.conf.urls import url
import Bevut.admin
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.html import format_html
from django.forms import TextInput, Textarea
from django.contrib.messages import ERROR, SUCCESS, INFO
from app.models import *
class OptionInline(admin.TabularInline):
    model = FormOption
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':14,'cols':30}) }
    }

    def has_delete_permission(self, request, obj=None):
        if obj != None and obj.applied:
            return False
        return super(OptionInline, self).has_delete_permission(request, obj)
    #fields = [("description", "done_description", "well_done_description", "not_done_description")]
    #def get_fields(self, request, obj=None):
    #    gf = super(OptionInline, self).get_fields(request, obj)
        

@admin.register(FormTemplate)
class TemplateAdmin(admin.ModelAdmin):
    save_as = True
    fields = ['name', 'has_well_done']
    list_display = ["__str__", "apply_template_link"]
    inlines = (OptionInline,)

    def apply_template_link(self, obj):
        if(obj.applied != True):
            return format_html('<a href="/admin/app/formtemplate/{}/apply/">Applicera formulär på kurs</a>', obj.id)
        else:
            return 'Formuläret är redan applicerat'

    apply_template_link.short_description = "Applicera"

    def has_delete_permission(self, request, obj=None):
        return obj == None or not obj.applied or request.user.is_superuser

    def get_urls(self):
        urls = super(TemplateAdmin, self).get_urls()
        template_urls = [
            url(r'^(?P<template_id>[0-9]+)/apply/$', self.admin_site.admin_view(self.apply_template)),
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
            for student in course.students.all():
                sf = StudentForm(student=student, course=course, template=template, midterm_signed=False, fullterm_signed=False, locked=False)
                sf.save()
            self.message_user(request, "Applicerade formulär på kursen %s" % course.name)
            return redirect("/admin/app/formtemplate")
        else:
            
            courses = Course.objects.filter(form_templates=None)
            context = dict(
                    self.admin_site.each_context(request),
                    title = "Applicera mall på kurs",
                    form_template = template,
                    courses = courses
            )
            return render(request, "app/admin/apply_template.html", context)

    def save_model(self, request, obj, form, change):
        if obj.applied and not '_saveasnew' in request.POST:
            self.message_user(request, "Formuläret sparades inte då det redan har applicerats på en kurs", ERROR)
            return False
        return super(TemplateAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.template.applied and not '_saveasnew' in request.POST:
                return
        return super(TemplateAdmin, self).save_formset(request, form, formset, change)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    save_as = True
    radio_fields = {'term': admin.HORIZONTAL }
    filter_horizontal = ['students']


admin.site.disable_action('delete_selected')