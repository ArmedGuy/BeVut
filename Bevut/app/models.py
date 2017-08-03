"""
Definition of models.
"""

from hashlib import sha256
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

# Create your models here.

User.__str__ = lambda self: "%s %s" % (self.first_name, self.last_name)


class Student(models.Model):
    name = models.CharField("Namn", max_length=256)
    ssn = models.CharField("Personnummer", unique=True, max_length=12, validators=[
        RegexValidator(
            regex='^[0-9]{12}$',
            message='Personnumret måste vara tolv siffror utan bindesstreck (Ex. 197001010000)',
            code='nomatch')])
    email = models.EmailField("Email", unique=True)
    deleted = models.BooleanField("Borttagen", default=False)
    identity = models.CharField("Identitet", unique=True, max_length=64)

    def __str__(self):
        return self.name

    def populate_hash(self):
        h = sha256()
        h.update(self.ssn.encode('utf-8'))
        self.identity = h.hexdigest()

    class Meta:
        verbose_name = "student"
        verbose_name_plural = "studenter"


# Could probaby override save function but this is more cool
@receiver(pre_save, sender=Student)
def student_ssn_hash(sender, instance, *args, **kwargs):
    if instance.identity is None:
        instance.populate_hash()


TERM_CHOICES = (
    ("VT", "Vårtermin"),
    ("HT", "Hösttermin")
)


class Course(models.Model):
    name = models.CharField("Kursnummer", max_length=32)
    year = models.CharField("År", max_length=32)
    term = models.CharField("Termin", choices=TERM_CHOICES, max_length=2)
    weeks = models.CharField("Antal veckor VFU", max_length=32)
    students = models.ManyToManyField(Student, verbose_name="studenter", blank=True)

    def __str__(self):
        return "%s (%s %s)" % (self.name, self.year, self.term)

    class Meta:
        verbose_name = "kurs"
        verbose_name_plural = "kurser"


class FormTemplate(models.Model):
    name = models.CharField("Namn", max_length=64)
    has_well_done = models.BooleanField(
            "Kan betyget väl godkänt ges?",
            help_text="Kryssa i det här om du vill att betygskriterier för väl godkänt ska synas och bedömas")
    applied = models.BooleanField("Har formuläret applicerats på en kurs?", default=False)
    course = models.ForeignKey(
            Course,
            related_name="form_templates",
            verbose_name="Applicerad på kurs",
            null=True,
            default=None)

    def __str__(self):
        if self.applied:
            return "(LÅST) %s applicerat på kurs %s" % (self.name, self.course)
        return self.name

    class Meta:
        verbose_name = "formulärsmall"
        verbose_name_plural = "formulärsmallar"


class FormOption(models.Model):
    nr = models.IntegerField(
            "Nummer",
            help_text="Siffra på fråga, används för sortering och för att lätt kunna referera")
    description = models.TextField("Lärandeaspekter")
    done_description = models.TextField("Kriterier för godkänt")
    well_done_description = models.TextField(
            "Kriterier för väl godkänt",
            help_text="Behövs endast om formuläret har Väl Godkänt",
            blank=True)
    not_done_description = models.TextField("Kriterier för icke godkänt")
    template = models.ForeignKey(FormTemplate)

    def __str__(self):
        return "Formulärsfråga: %s ..." % self.description[0:30]

    class Meta:
        verbose_name = "formulärsfråga"
        verbose_name_plural = "formulärsfrågor"


class StudentForm(models.Model):
    student = models.ForeignKey(Student)
    course = models.ForeignKey(Course, related_name="student_forms", null=True)
    template = models.ForeignKey(FormTemplate)
    handler = models.CharField("Handledare/ansvarig", max_length=256, blank=True)
    location = models.CharField("VFU-placering", max_length=256, blank=True)
    midterm_signed = models.BooleanField("Halvtidsbedömning gjord", default=False)
    fullterm_signed = models.BooleanField("Heltidsbedömning gjord", default=False)
    midterm_signed_date = models.DateTimeField("Datum för halvtidsbedömining", null=True)
    fullterm_signed_date = models.DateTimeField("Datum för heltidsbedömning", null=True)
    midterm_comments = models.TextField("Kommentarer vid halvtidsbedömning", blank=True)
    fullterm_comments = models.TextField("Kommentarer vid heltidbedömning", blank=True)
    midterm_absence = models.CharField("Frånvaro vid halvtidsbedömning", max_length=10, blank=True)
    fullterm_absence = models.CharField("Frånvaro vid heltidsbedömning", max_length=10, blank=True)
    fullterm_ok_absence = models.CharField("OK Frånvaro vid heltidsbedömning", max_length=10, blank=True)
    locked = models.BooleanField("Låst", default=False)
    link_uuid = models.UUIDField('Read only länk id', default=uuid4, editable=True)

    def __str__(self):
        return "%s - %s" % (self.student.name, self.course)

    class Meta:
        verbose_name = "studentformulär"
        verbose_name_plural = "studentformulär"


class FormSigningAttendance(models.Model):
    title = models.CharField("Titel/befattning", max_length=256)
    name = models.CharField("Namn", max_length=256)
    midterm_sign = models.ForeignKey(StudentForm, related_name="midterm_user_signed", null=True)
    fullterm_sign = models.ForeignKey(StudentForm, related_name="fullterm_user_signed", null=True)

    class Meta:
        verbose_name = "signerat namn"
        verbose_name_plural = "signerade namn"


FORM_RESULTS = (
    ("V", "Risk för icke godkänt"),
    ("OK", "Bra"),
    ("G", "Godkänt"),
    ("VG", "Väl godkänt"),
    ("U", "Icke godkänt")
)


class FormAnswer(models.Model):
    form = models.ForeignKey(StudentForm)
    option = models.ForeignKey(FormOption)
    is_midterm = models.BooleanField("Halvtidssamtal")
    result = models.CharField("Resultat", max_length=3, choices=FORM_RESULTS)

    class Meta:
        verbose_name = "formulärssvar"
        verbose_name_plural = "formulärssvar"


# vi: ts=4 expandtab
