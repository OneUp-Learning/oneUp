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
        courses = []
        universityTimezone = None
        if 'universityCourses' in request.POST:
            universityCoursesList = request.POST.getlist("universityCourses")
            print("fdjlsjfklds")
            print(universityCoursesList)
            courses = [Courses.objects.get(
                courseName=courseName) for courseName in universityCoursesList]
        
        if 'universityTimezone' in request.POST:
            universityTimezone = request.POST.get("universityTimezone")


        if 'universityID' in request.GET:  # Editing course
            university = Universities.objects.get(
                universityID=int(request.GET['universityID']))
            university.universityName = name
            if universityTimezone:
                university.universityTimezone = universityTimezone
            university.save()

            # Add selected courses to university
            if 'universityCourses' in request.POST:
                for course in courses:
                    if not UniversityCourses.objects.filter(courseID=course):
                        uC = UniversityCourses()
                        uC.universityID = university
                        uC.courseID = course
                        uC.save()

            coursesToRemove = UniversityCourses.objects.filter(
                universityID=university).exclude(courseID__in=courses)
            for course in coursesToRemove:
                course.delete()
        else:
            universtiyExist = Universities.objects.filter(universityName=name)
            if universtiyExist:
                context_dict['errorMessage'] = "University name taken."
            else:
                university = Universities()
                university.universityName = name
                if universityTimezone:
                    university.universityTimezone = universityTimezone
                university.save()

                # Add selected courses to university
                if 'universityCourses' in request.POST:
                    for course in courses:
                        if not UniversityCourses.objects.filter(courseID=course):
                            uC = UniversityCourses()
                            uC.universityID = university
                            uC.courseID = course
                            uC.save()

    # Get all universities
    context_dict['universities'] = Universities.objects.all()
    nonQualifiedCourses = [
        universityCourse.courseID for universityCourse in UniversityCourses.objects.all()]
    context_dict['qualified_courses'] = [
        course for course in Courses.objects.all() if not course in nonQualifiedCourses]

    timezones = [{"value": "America/New_York", "name": "Eastern (EST)"}, {"value": "America/Chicago", "name": "Central (CST)"},
                {"value": "America/Denver", "name": "Mountain (MST)"}, {"value": "America/Los_Angeles", "name": "Pacific (PST)"}]
    context_dict['supported_timezones'] = timezones

    if 'universityID' in request.GET:
        university = Universities.objects.get(
            universityID=int(request.GET['universityID']))
        context_dict["universityName"] = university.universityName
        context_dict['universityTimezone'] = university.universityTimezone
        universityCourses = UniversityCourses.objects.filter(
            universityID=university)
        
        context_dict['universityCourses'] = [
            universityCourse.courseID.courseName for universityCourse in universityCourses]
        context_dict["editing"] = True
        nonQualifiedCourses = []
        for universityCourse in UniversityCourses.objects.all():
            if not universityCourse.courseID.courseName in context_dict['universityCourses']:
                nonQualifiedCourses.append(universityCourse.courseID)
        print("non qualified")
        print(nonQualifiedCourses)
        context_dict['qualified_courses'] = [
            course for course in Courses.objects.all() if not course in nonQualifiedCourses]
        

    return render(request, 'Administrators/createUniversity.html', context_dict)
