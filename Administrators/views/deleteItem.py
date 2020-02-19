
from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Instructors, InstructorRegisteredCourses, Courses, ChallengesTopics, Challenges, Universities
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import adminsCheck


@login_required
@user_passes_test(adminsCheck, login_url='/oneUp/home', redirect_field_name='')
def deleteItemView(request):
    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
    context_dict["username"] = user.username

    if 'courseToDelete' in request.POST:
        # Delete periodic tasks related to this course
        PeriodicTask.objects.filter(
            kwargs__contains='"course_id": '+request.POST["courseToDelete"]).delete()
        course = Courses.objects.get(pk=int(request.POST['courseToDelete']))

        # logic to delete all the objects that exist from unspecified topics
        challengeTopicsList = ChallengesTopics.objects.filter(challengeID__courseID=int(
            request.POST['courseToDelete']), topicID__topicName="Unspecified")
        for challengeTopic in challengeTopicsList:
            challengeTopic.challengeID.delete()

        course.delete()

    if 'universityToDelete' in request.POST:
        university = Universities.objects.get(
            universityID=int(request.POST['universityToDelete']))
        university.delete()

    if 'instructorToDelete' in request.POST:
        instructor = User.objects.get(
            username=request.POST['instructorToDelete'])
        print("Deleted:", instructor)
        instructor.delete()

    return redirect('/oneUp/administrators/adminHome.html')
