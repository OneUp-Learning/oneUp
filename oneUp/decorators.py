from django.contrib.auth.decorators import user_passes_test
from Instructors.models import Instructors

# Used to check if the user is a Instructor if not takes the student to the Student home Page
def instructorsCheck(user):
    instruct = Instructors.objects.filter(user=user)
    if instruct:
        return True

    return False
    
        