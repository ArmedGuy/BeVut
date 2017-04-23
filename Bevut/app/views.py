"""
Definition of views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.contrib.auth.decorators import login_required
from app.models import Course

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.user.is_authenticated:
        return redirect("/app")
    return redirect("/login")

@login_required
def courses(request):
    courses = Course.objects.filter()
    return render(request, "app/index.html", {"courses": courses})


def course(request, *args, **kwargs):
    course = get_object_or_404(Course, pk=kwargs['id'])
    student_forms = course.student_forms.all()
    students = []
    if len(student_forms) == 0:
        students = course.students.all()
    else:
        students = [x.student for x in student_forms]
    return render(request, "app/course.html", {"course": course, "student_forms": student_forms, "students": students })