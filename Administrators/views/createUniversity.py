from django.shortcuts import render
from django.contrib.auth.models import User
from oneUp.decorators import adminsCheck
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Universities, UniversityCourses, Courses


@login_required
@user_passes_test(adminsCheck, login_url='/oneUp/home', redirect_field_name='')
def courseUniversityView(request):

    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"] = user.username

    if request.method == 'POST':
        name = request.POST['universityName']

        if 'universityID' in request.GET:  # Editing course
            university = Universities.objects.get(
                universityID=int(request.GET['universityID']))
            university.universityName = name
            university.save()
        else:
            universtiyExist = Universities.objects.filter(universityName=name)
            if universtiyExist:
                context_dict['errorMessage'] = "University name taken."
            else:
                university = Universities()
                university.universityName = name
                university.save()

    if 'universityID' in request.GET:
        university = Universities.objects.get(
            universityID=int(request.GET['universityID']))
        context_dict["universityName"] = university.universityName
        context_dict['universtyCourses'] = UniversityCourses.objects.filter(
            universityID=university)
        context_dict["editing"] = True

    # Get all universities
    context_dict['universities'] = Universities.objects.all()

    courses = Courses.objects.all()
    context_dict['qualified_courses'] = [
        course for course in courses if not UniversityCourses.objects.filter(courseID=course)]

    return render(request, 'Administrators/createUniversity.html', context_dict)
