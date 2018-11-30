from django.contrib.auth.decorators import user_passes_test
from Instructors.models import Instructors

# Used to check if the user is a Instructor if not takes the student to the Student home Page
def instructorsCheck(user):
    #instruct = Instructors.objects.filter(user=user)
    return user.groups.filter(name='Teachers').exists()
    # if instruct:
    #     print("We are a teacher")
    #     return True

    # return False
    
#from django.contrib.auth.decorators import login_required, user_passes_test
#from oneUp.decorators import instructorsCheck     
#@login_required
#@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   

  