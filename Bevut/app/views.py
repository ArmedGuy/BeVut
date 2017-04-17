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
    courses = Course.objects.filter(applied=True)
    return render(request, "app/index.html", {"courses": courses})


def course(request, *args, **kwargs):
    course = get_object_or_404(Course, pk=kwargs['id'])
    return render(request, "app/course.html", {"course": course})