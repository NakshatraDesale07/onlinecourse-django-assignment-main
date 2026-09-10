from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Choice, Course, Enrollment, Lesson, Question, Submission


def course_list(request):
    courses = Course.objects.all()
    return render(request, "course_list.html", {"courses": courses})


def course_details_bootstrap(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)
    if not questions.exists():
        questions = Question.objects.filter(lesson__course=course)
    return render(
        request,
        "course_details_bootstrap.html",
        {"course": course, "questions": questions},
    )


@login_required
def exam(request, lesson_id):
    # Support accessing exam by lesson or course
    lesson = Lesson.objects.filter(id=lesson_id).first()
    if lesson:
        course = lesson.course
        questions = Question.objects.filter(lesson=lesson).prefetch_related("choices")
        if not questions.exists():
            questions = Question.objects.filter(course=course).prefetch_related("choices")
    else:
        course = get_object_or_404(Course, id=lesson_id)
        lesson = course.lessons.first()
        questions = Question.objects.filter(course=course).prefetch_related("choices")

    return render(
        request,
        "exam.html",
        {"lesson": lesson, "course": course, "questions": questions},
    )


@login_required
def submit(request, course_id=None):
    if course_id is None:
        return redirect("course_list")

    # Try finding course directly or via lesson
    course = Course.objects.filter(id=course_id).first()
    if not course:
        lesson = get_object_or_404(Lesson, id=course_id)
        course = lesson.course

    if request.method != "POST":
        return redirect("course_details", course_id=course.id)

    # Get or create enrollment for the user and course
    enrollment, _ = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={"mode": "honor"},
    )

    # Create submission record
    submission = Submission.objects.create(
        enrollment=enrollment,
        user=request.user,
    )

    # Extract selected choices from POST request
    selected_choice_ids = []
    for key, values in request.POST.lists():
        if key.startswith("choice") or key.startswith("question"):
            for val in values:
                try:
                    selected_choice_ids.append(int(val))
                except (ValueError, TypeError):
                    continue

    if selected_choice_ids:
        submission.choices.set(selected_choice_ids)

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


@login_required
def show_exam_result(request, course_id, submission_id=None):
    course = Course.objects.filter(id=course_id).first()
    if not course:
        lesson = get_object_or_404(Lesson, id=course_id)
        course = lesson.course

    if submission_id:
        submission = get_object_or_404(Submission, id=submission_id)
    else:
        submission = (
            Submission.objects.filter(enrollment__course=course, enrollment__user=request.user)
            .order_by("-submitted_at")
            .first()
        )
        if not submission:
            submission = Submission.objects.filter(user=request.user).order_by("-submitted_at").first()

    selected_choices = submission.choices.all() if submission else Choice.objects.none()
    selected_ids = list(selected_choices.values_list("id", flat=True))

    # Retrieve all questions for the course
    questions = Question.objects.filter(course=course).prefetch_related("choices")
    if not questions.exists():
        questions = Question.objects.filter(lesson__course=course).prefetch_related("choices")

    total_score = 0
    possible_score = 0
    question_results = []

    for question in questions:
        possible_score += question.grade
        is_correct = question.is_get_score(selected_ids)
        if is_correct:
            total_score += question.grade

        question_results.append({
            "question": question,
            "is_correct": is_correct,
            "choices": question.choices.all(),
        })

    grade = int((total_score / possible_score) * 100) if possible_score > 0 else 0
    passed = grade >= 80 or (possible_score > 0 and total_score == possible_score)

    context = {
        "course": course,
        "submission": submission,
        "total_score": total_score,
        "possible_score": possible_score,
        "grade": grade,
        "score": total_score,
        "total": possible_score,
        "choices": selected_choices,
        "questions": questions,
        "question_results": question_results,
        "passed": passed,
    }

    return render(request, "exam_result_bootstrap.html", context)
