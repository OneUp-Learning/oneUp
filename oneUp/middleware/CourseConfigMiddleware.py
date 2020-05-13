from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import redirect

from Badges.models import CourseConfigParams
from Instructors.models import Courses
from Students.models import Student, StudentConfigParams


class CourseConfigMiddleware:
    ''' This middleware will prevent students (and instructors) from being able to access pages by url 
        that should only be available if certain config settings are enabled

        The paths dictionary is a collection of url paths and course config/student config variables that 
        should have a certain value. If the current config setting for a user doesn't match any of the
        values for that url, the user will be sent back to the course home page.
    '''
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.paths = {
            '/oneUp/students/Announcements':
                {
                    'announcementsUsed': True,
                },
            '/oneUp/students/Leaderboard': 
                {
                    'leaderboardUsed': True, 
                    'skillLeaderboardDisplayed': True,
                    'gamificationUsed': True,
                },
            '/oneUp/students/LeaderboardInfo': 
                {
                    'leaderboardUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/badges/CourseBadges': 
                {
                    'badgesUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/VirtualCurrencyRules': 
                {
                    'virtualCurrencyUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/ChallengesWarmUpList': 
                {
                    'warmupsUsed': True, 
                },
            '/oneUp/students/ChallengesList': 
                {
                    'seriousChallengesUsed': True, 
                },
            '/oneUp/students/ActivityList': 
                {
                    'activitiesUsed': True, 
                },
            '/oneUp/students/CoursePerformance': 
                {
                    'gradebookUsed': True, 
                },
            '/oneUp/students/achievements': 
                {
                    'displayAchievementPage': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/avatar': 
                {
                    'avatarUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/goalslist': 
                {
                    'goalsUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/chat/api': 
                {
                    'chatUsed': True, 
                },
            '/oneUp/students/VirtualCurrencyShop': 
                {
                    'virtualCurrencyUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/Transactions': 
                {
                    'virtualCurrencyUsed': True, 
                    'gamificationUsed': True,
                },
            '/oneUp/students/Callouts': 
                {
                    'classmatesChallenges': True, 
                    'gamificationUsed': True,
                },
            # TODO: Add links for instructors?
            '/oneUp/instructors/preferences':
                {
                    'gamificationUsed': True,
                }
        }
        self.reset_course_paths = ['/oneUp/students/StudentHome', '/oneUp/instructors/instructorHome']

        # not sure about caching these as we can have many users requesting at once
        self.course_config_params = None
        self.student_config_params = None
        self.current_course = None
        self.current_user = None

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # print(f'PATH {request.path}')
        
        # Check if we are trying to go to a page that should have no course selected and delete the course session 
        if request.path in self.reset_course_paths:
            self.course_config_params = None
            self.current_course = None
            if 'currentCourseID' in request.session:
                del request.session['currentCourseID']

        if request.user == AnonymousUser:
            self.student_config_params = None
            self.current_user = None
            self.course_config_params = None
            self.current_course = None

        # If request in paths to check and user is not fully logged out..
        if request.path in self.paths and not request.user == AnonymousUser:
            # Get current course
            if 'currentCourseID' in request.session:
                course = Courses.objects.get(pk=int(request.session['currentCourseID']))
            else:
                course = None

            # Get current student
            if 'userID' in request.GET:    
                # This is a teacher viewing as a student
                stud = User.objects.get(username=request.GET['userID'])
                student = Student.objects.filter(user=stud).first()
            else:
                # This will also get the teacher student object (test student)
                student = Student.objects.filter(user=request.user).first()

            # Get the latest course and student config parameters
            self.update_params(course, student)
            # ccparams, scparams = self.update_params_constant(course, student)
            # print(self.course_config_params, self.student_config_params)
            # We check the configs fields to see if this request is valid
            if self.validate_request(request.path, ccparams=self.course_config_params, scparams=self.student_config_params) is False:
                if course:
                    if student and student.user.groups.filter(name='Teachers').exists() or not student:
                        return redirect('/oneUp/instructors/instructorCourseHome')
                    else:
                        return redirect('/oneUp/students/StudentCourseHome')
                else:
                    if student and student.user.groups.filter(name='Teachers').exists() or not student:
                        return redirect('/oneUp/instructors/instructorHome')
                    else:
                        return redirect('/oneUp/students/StudentHome')

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    def update_params(self, course, student):
        if course:
            self.course_config_params = CourseConfigParams.objects.get(courseID=course)
            self.current_course = course
        if course and student:
            self.student_config_params = StudentConfigParams.objects.get(courseID=course, studentID=student)
            self.current_user = student

        # print(self.__dict__)
    
    def validate_request(self, path, ccparams=None, scparams=None):
        ''' Check corresponding configuration fields for a path that 
            should have a specific value
        '''
        fields_to_check = self.paths[path]

        for field, value in fields_to_check.items():
            if ccparams and hasattr(ccparams, field):
                if getattr(ccparams, field) is not value:
                    return False
            elif scparams and hasattr(scparams, field):
                if getattr(scparams, field) is not value:
                    return False
            else:
                return False

        return True
    
    def update_params_constant(self, course, student):
        ccparams = None
        scparams = None
        if course:
            ccparams = CourseConfigParams.objects.get(courseID=course)
            if student:
                scparams = StudentConfigParams.objects.get(courseID=course, studentID=student)

        return ccparams, scparams
