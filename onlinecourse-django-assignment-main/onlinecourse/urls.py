from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("course/<int:course_id>/", views.course_details_bootstrap, name="course_details"),
    path("exam/<int:lesson_id>/", views.exam, name="exam"),
    path("course/<int:course_id>/submit/", views.submit, name="submit"),
    path("course/<int:course_id>/submission/<int:submission_id>/result/", views.show_exam_result, name="show_exam_result"),
    # Backwards compatibility and alternative name aliases
    path("course/<int:course_id>/submission/<int:submission_id>/result/", views.show_exam_result, name="exam_result"),
    path("submit/<int:course_id>/", views.submit, name="submit_alias"),
    path("exam-result/<int:course_id>/", views.show_exam_result, name="show_exam_result_alias"),
]
