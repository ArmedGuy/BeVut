"""
Definition of views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from app.models import Course, StudentForm, FormAnswer


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.user.is_authenticated:
        return redirect(reverse("courses"))
    return redirect(reverse("login"))


@login_required
def courses(request):
    courses = Course.objects.all()
    return render(request, "app/index.html", {"courses": courses})


@login_required
def course(request, *args, **kwargs):
    course = get_object_or_404(Course, pk=kwargs['id'])
    student_forms = course.student_forms.all()
    students = []
    if len(student_forms) == 0:
        students = course.students.all()
    else:
        students = [x.student for x in student_forms]
    return render(request, "app/course.html", {"course": course, "student_forms": student_forms, "students": students})


@login_required
def student_form(request, *args, **kwargs):
    ctx = {}
    form = get_object_or_404(StudentForm, pk=kwargs['id'])
    ctx['student_form'] = form
    ctx['midterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=True):
        ctx['midterm_answers'][a.option.id] = a.result
    ctx['fullterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=False):
        ctx['fullterm_answers'][a.option.id] = a.result
    ctx['midterm_in_progress'] = (
            "midterm" in [
                request.POST.get("term"),
                request.GET.get("term")]
            or len(ctx['midterm_answers']) != 0) and not form.midterm_signed

    ctx['fullterm_in_progress'] = (
            "fullterm" in [
                request.POST.get("term"),
                request.GET.get("term")]
            or len(ctx['fullterm_answers']) != 0) and not form.fullterm_signed and not ctx['midterm_in_progress']
    if request.method == "GET":
        return render(request, "app/form.html", ctx)
    elif request.method == "POST":
        if form.locked:
            return render(request, "app/form.html", ctx)
        for opt in form.template.formoption_set.all():
            if not request.POST.get(str(opt.id), False):
                print(request.POST.get(opt.id))
                continue
            res = request.POST.get(str(opt.id))
            if ctx['midterm_in_progress']:
                print("midterm in progress")
                answer = form.formanswer_set.filter(option=opt, is_midterm=True).first()
                if answer is None:
                    answer = FormAnswer(option=opt, form=form, is_midterm=True)
                answer.result = res
                ctx['midterm_answers'][opt.id] = res
                answer.save()
            elif ctx['fullterm_in_progress']:
                answer = form.formanswer_set.filter(option=opt, is_midterm=False).first()
                if answer is None:
                    answer = FormAnswer(option=opt, form=form, is_midterm=False)
                answer.result = res
                ctx['fullterm_answers'][opt.id] = res
                answer.save()
        if request.POST.get("sign"):
            if ctx['midterm_in_progress']:
                form.midterm_signed = True
            if ctx['fullterm_in_progress']:
                form.fullterm_signed = True
            form.save()
        ctx['midterm_in_progress'] = (
                "midterm" in [
                    request.POST.get("term"),
                    request.GET.get("term")]
                or len(ctx['midterm_answers']) != 0) and not form.midterm_signed
        ctx['fullterm_in_progress'] = (
                "fullterm" in [
                    request.POST.get("term"),
                    request.GET.get("term")]
                or len(ctx['fullterm_answers']) != 0) and not form.fullterm_signed and not ctx['midterm_in_progress']
        return render(request, "app/form.html", ctx)

# vi: ts=4 expandtab
