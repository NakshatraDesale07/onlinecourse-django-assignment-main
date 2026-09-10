OnlineCourse Django Assignment
This project is structured to satisfy the seven tasks in the assignment:

onlinecourse/models.py contains Question, Choice and Submission models.
onlinecourse/admin.py contains seven imported classes and the required inline/admin classes.
Django Admin displays Authentication and Authorization and OnlineCourse sections.
course_details_bootstrap.html displays course name and related lessons with Django template tags and Bootstrap.
views.py contains submit and show_exam_result.
urls.py contains paths for submit and show_exam_result.
A mock exam can be completed and a successful result page displays Congratulations, score and exam results.
Run
python -m venv venv
# Windows:
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Open:

http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/
