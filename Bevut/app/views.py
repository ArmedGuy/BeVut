"""
Definition of views.
"""

from uuid import UUID
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
import django.contrib.messages as messages

from app.models import Course, StudentForm, FormAnswer, FormSigningAttendance


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
    return render(request, "app/course.html",
                  {"course": course, "student_forms": student_forms, "students": students})


@login_required
def course_action_plan(request, *args, **kwargs):
    course = get_object_or_404(Course, pk=kwargs['id'])
    student_forms = course.student_forms.filter(midterm_action_plan__in=['yes', 'started'])
    students = []
    if len(student_forms) == 0:
        students = course.students.all()
    else:
        students = [x.student for x in student_forms]
    return render(request, "app/course_action_plan.html",
                  {"course": course, "student_forms": student_forms, "students": students})


@login_required
def student_form(request, *args, **kwargs):
    ctx = {}
    form = get_object_or_404(StudentForm, pk=kwargs['id'])
    ctx['todays_date'] = datetime.today().strftime('%Y-%m-%d')
    ctx['student_form'] = form
    ctx['current_answers'] = {}
    ctx['midterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=True):
        ctx['midterm_answers'][a.option.id] = a.result
        ctx['current_answers'][a.option.id] = a.result
    ctx['fullterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=False):
        ctx['fullterm_answers'][a.option.id] = a.result
        ctx['current_answers'][a.option.id] = a.result

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
    ctx['show_midterm_answer'] = not ctx['midterm_in_progress'] and (
            ctx['fullterm_in_progress'] and not form.fullterm_signed
            ) or request.GET.get("show_midterm")

    if request.method == "GET":
        return render(request, "app/form.html", ctx)
    elif request.method == "POST":
        if form.locked:
            return render(request, "app/form.html", ctx)
        action_plan = 'no'
        missing_value = False
        for opt in form.template.formoption_set.all():
            if not request.POST.get(str(opt.id), False):
                missing_value = True
                continue
            res = request.POST.get(str(opt.id))
            if ctx['midterm_in_progress']:
                answer = form.formanswer_set.filter(option=opt, is_midterm=True).first()
                if answer is None:
                    answer = FormAnswer(option=opt, form=form, is_midterm=True)
                answer.result = res
                ctx['midterm_answers'][opt.id] = res
                if res == 'V':
                    action_plan = 'yes'
                ctx['current_answers'][opt.id] = res
                answer.save()
            elif ctx['fullterm_in_progress']:
                answer = form.formanswer_set.filter(option=opt, is_midterm=False).first()
                if answer is None:
                    answer = FormAnswer(option=opt, form=form, is_midterm=False)
                answer.result = res
                ctx['fullterm_answers'][opt.id] = res
                ctx['current_answers'][opt.id] = res
                answer.save()
        if request.POST.get("sign"):
            if missing_value:
                messages.error(request,
                               "Alla delar av formuläret är inte ifyllt.", extra_tags="red darken-2 white-text")
                return render(request, "app/form.html", ctx)
            elif ctx['midterm_in_progress']:
                form.midterm_signed = True
                form.midterm_signed_date = datetime.today()
                names = request.POST.getlist("signer_name")
                form.midterm_action_plan = action_plan
                positions = request.POST.getlist("signer_position")
                for i in range(len(names)):
                    attendee = FormSigningAttendance(title=positions[i], name=names[i], midterm_sign=form)
                    attendee.save()

            elif ctx['fullterm_in_progress']:
                form.fullterm_signed = True
                form.fullterm_signed_date = datetime.today()
                names = request.POST.getlist("signer_name")
                positions = request.POST.getlist("signer_position")
                for i in range(len(names)):
                    print("creating %s" % names[i])
                    attendee = FormSigningAttendance(title=positions[i], name=names[i], fullterm_sign=form)
                    attendee.save()

        if ctx['midterm_in_progress']:
            form.midterm_comments = request.POST.get("comments", "")
            form.midterm_absence = request.POST.get("absence", "")
        if ctx['fullterm_in_progress']:
            form.fullterm_comments = request.POST.get("comments", "")
            form.fullterm_absence = request.POST.get("absence", "")
            form.fullterm_ok_absence = request.POST.get("ok_absence", "")
        form.midterm_action_plan = request.POST.get("action_plan", form.midterm_action_plan)
        form.handler = request.POST.get("handler")
        form.location = request.POST.get("location")
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
        ctx['show_midterm_answer'] = not ctx['midterm_in_progress'] and (
                ctx['fullterm_in_progress'] and not form.fullterm_signed
                ) or request.GET.get("show_midterm")
        messages.info(request, "Formuläret har blivit uppdaterat", extra_tags="light-green white-text")
        return render(request, "app/form.html", ctx)


@require_GET
def readonly_studentform(request, *args, **kwargs):
    form = None
    try:
        uuid = UUID(kwargs["uuid"])
        form = StudentForm.objects.filter(link_uuid=uuid).first()
    except:
        pass

    if form is None:
        raise Http404()
    ctx = {}
    ctx['todays_date'] = datetime.today().strftime('%Y-%m-%d')
    ctx['logged_in'] = not request.user.is_anonymous
    ctx['student_form'] = form
    ctx['current_answers'] = {}
    ctx['midterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=True):
        ctx['midterm_answers'][a.option.id] = a.result
        ctx['current_answers'][a.option.id] = a.result
    ctx['fullterm_answers'] = {}
    for a in form.formanswer_set.filter(is_midterm=False):
        ctx['fullterm_answers'][a.option.id] = a.result
        ctx['current_answers'][a.option.id] = a.result

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
    ctx['show_midterm_answer'] = ctx['logged_in']
    return render(request, 'app/form_readonly.html', ctx)

# vi: ts=4 expandtab
