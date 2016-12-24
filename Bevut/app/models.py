"""
Definition of models.
"""

from django.db import models
from django.contrib import admin
import Bevut.admin
from django.contrib.auth.models import User
from django.forms import TextInput, Textarea
# Create your models here.

User.__str__ = lambda self: "%s %s" % (self.first_name, self.last_name)

class FormTemplate(models.Model):
    name = models.CharField(max_length=64)
    has_well_done = models.BooleanField("Kan betyget väl godkänt ges?")
    
    def __str__(self):
        return self.name

class TemplateOption(models.Model):
    description = models.TextField("Lärandeaspekter")
    done_description = models.TextField("Kriterier för godkänt")
    well_done_description = models.TextField("Kriterier för väl godkänt", help_text = "Behövs endast om formuläret har Väl Godkänt")
    not_done_description = models.TextField("Kriterier för icke godkänt")
    template = models.ForeignKey(FormTemplate)


class Course(models.Model):
    name = models.CharField("Kursnummer", max_length=32)
    year = models.CharField("År", max_length=32)
    weeks = models.CharField("Antal veckor", max_length=32)
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.year)

class Student(models.Model):
    name = models.CharField("Namn", max_length=256)
    ssn = models.CharField("Personnummer", max_length=18)
    course = models.ForeignKey(Course)

    def __str__(self):
        return self.name

class StudentForm(models.Model):
    student = models.ForeignKey(Student)
    template = models.ForeignKey(FormTemplate)
    
    def __str__(self):
        return "%s (%s)" % (self.student.name, self.student.course.name)

FORM_RESULTS = (
    ("G", "Godkänt"),
    ("VG", "Väl godkänt"),
    ("U", "Icke godkänt")
)

class FormAnswer(models.Model):
    form = models.ForeignKey(StudentForm)
    option = models.ForeignKey(TemplateOption)
    is_midterm = models.BooleanField("Halvtidssamtal")
    result = models.CharField("Resultat", max_length=3, choices=FORM_RESULTS)

class CourseGroup(models.Model):
    course = models.ForeignKey(Course)
    supervisor = models.ForeignKey(User)
    location = models.CharField("Vårdavdelning", max_length=256)
    students = models.ManyToManyField(Student)

class OptionInline(admin.TabularInline):
    model = TemplateOption
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':14,'cols':30}) }
    }

@admin.register(FormTemplate)
class TemplateAdmin(admin.ModelAdmin):
    inlines = (OptionInline,)


@admin.register(StudentForm)
class FormAdmin(admin.ModelAdmin):
    pass

class CourseGroupInline(admin.TabularInline):
    extra = 1
    model = CourseGroup
    filter_horizontal = ['students']

class StudentInline(admin.TabularInline):
    extra = 1
    model = Student

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = (StudentInline, CourseGroupInline)