from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return f"Enrollment: {self.user.username} - {self.course.name}"


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions", null=True, blank=True)
    question_text = models.CharField(max_length=500)
    grade = models.IntegerField(default=50)

    @property
    def content(self):
        return self.question_text

    @content.setter
    def content(self, value):
        self.question_text = value

    def __str__(self):
        return self.question_text

    # Method to calculate if the learner gets the score of the question
    def is_get_score(self, selected_ids=None):
        if selected_ids is None:
            selected_ids = []
        choices_mgr = getattr(self, 'choices', None) or getattr(self, 'choice_set', None)
        all_answers = choices_mgr.filter(is_correct=True).count()
        selected_correct = choices_mgr.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers > 0 and all_answers == selected_correct:
            return True
        return False


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    @property
    def content(self):
        return self.choice_text

    @content.setter
    def content(self, value):
        self.choice_text = value

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True, blank=True)
    choices = models.ManyToManyField(Choice, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.enrollment:
            return f"{self.enrollment.user.username} - Course: {self.enrollment.course.name}"
        if self.user and self.question:
            return f"{self.user.username} - {self.question}"
        return f"Submission #{self.id}"
