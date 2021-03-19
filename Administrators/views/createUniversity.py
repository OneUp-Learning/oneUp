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
      
        
        if 'universityTimezone' in request.POST:
            universityTimezone = request.POST.get("universityTimezone")

        if 'universityPostfix' in request.POST:
            universityPostfix = request.POST.get("universityPostfix")
        if 'universityID' in request.GET:  # Editing course
            university = Universities.objects.get(
                universityID=int(request.GET['universityID']))
            university.universityName = name
            if universityTimezone:
                university.universityTimezone = universityTimezone
            #remove @ symbol and whitespace if present
            if universityPostfix:
                if universityPostfix[0] == '@':
                    universityPostfix = universityPostfix[1:]
                universityPostfix=universityPostfix.replace(" ", "")
                university.universityPostfix = universityPostfix
            university.save()


            
        else:
            universtiyExist = Universities.objects.filter(universityName=name)
            if universtiyExist:
                context_dict['errorMessage'] = "University name taken."
            else:
                university = Universities()
                university.universityName = name
                if universityTimezone:
                    university.universityTimezone = universityTimezone
                if universityPostfix:
                    university.universityPostfix = universityPostfix
                university.save()

                
    # Get all universities
    context_dict['universities'] = Universities.objects.all()
   
    timezones = [{"value": "America/New_York", "name": "Eastern (EST)"}, {"value": "America/Chicago", "name": "Central (CST)"},
                {"value": "America/Denver", "name": "Mountain (MST)"}, {"value": "America/Los_Angeles", "name": "Pacific (PST)"}]
    context_dict['supported_timezones'] = timezones

    if 'universityID' in request.GET:
        university = Universities.objects.get(
            universityID=int(request.GET['universityID']))
        context_dict["universityName"] = university.universityName
        context_dict['universityTimezone'] = university.universityTimezone
        context_dict['universityPostfix'] = university.universityPostfix
        
  
        context_dict["editing"] = True
 
       

    return render(request, 'Administrators/createUniversity.html', context_dict)
