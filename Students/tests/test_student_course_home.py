from django.test import TestCase, tag
from oneUp.tests.common import CommonTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from Students.views.studentCourseHomeView import StudentCourseHome

import random
import time
from decimal import Decimal
from django.utils import timezone

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from Instructors.models import InstructorRegisteredCourses, Courses, Universities, UniversityCourses, Challenges, Topics, CoursesTopics, ActivitiesCategory, ChallengesTopics
from Badges.models import CourseConfigParams, VirtualCurrencyCustomRuleInfo
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams

from Instructors.views.utils import localizedDate
from Instructors.constants import anonymous_avatar, default_time_str, unassigned_problems_challenge_name, uncategorized_activity, unspecified_topic_name, unspecified_vc_manual_rule_description, unspecified_vc_manual_rule_name, unlimited_constant


from Instructors.questionTypes import QuestionTypes
from Instructors.models import StaticQuestions, Answers, CorrectAnswers, ChallengesQuestions
from Students.models import StudentChallengeAnswers, StudentChallengeQuestions, StudentChallenges

@tag("views")
class StudentCourseHomeTest(TestCase, CommonTestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase. Model instances created here should not be modified
        super(StudentCourseHomeTest, cls).init_common()

    def setUp(self):
        # Set up data for each test method (model instances that may be modified by the tests)
        self.printb("---------- Creating Courses, Instructors, Students, etc ---------")
        self.create_admins()
        self.create_universities()
        self.create_instructors()
        self.create_courses()
        self.create_students(amount=100)     
    
    def create_admins(self):
        admin = User.objects.create_superuser("banana-admin", "admin@oneup.com", "admin")
        admin.first_name = "Cranky"
        admin.last_name = "Kong"
        admin.save()

    def create_universities(self):
        university = Universities()
        university.universityName = "Banana U"
        university.save()

    def create_instructors(self):
        instructor = User.objects.create_user("banana-instructor", "banana@wssu.edu", "B@Nan*S?")
        instructor.first_name = "Donkey"
        instructor.last_name = "Kong"
        instructor.groups.add(self.teacher_group)
        instructor.save()

        student = Student()
        student.user = instructor
        student.universityID = "rams.wssu.edu"
        student.isTestStudent = True
        student.save()  

    def create_courses(self):
        # Create course
        course = Courses()
        course.courseName = "Test Course"
        course.courseDescription = "Used for django testing"
        course.save()
        
        instructor = User.objects.get(username="banana-instructor", groups__name="Teachers")
        student_instructor = Student.objects.get(user=instructor)

        # Link instructor to course
        irc = InstructorRegisteredCourses()
        irc.instructorID = instructor
        irc.courseID = course
        irc.save()

        # Link university to course
        uC = UniversityCourses()
        uC.universityID = Universities.objects.get(universityName="Banana U")
        uC.courseID = course
        uC.save()

        # Link student instructor to course
        student_registered_course = StudentRegisteredCourses()
        student_registered_course.studentID = student_instructor
        student_registered_course.courseID = course
        student_registered_course.avatarImage = anonymous_avatar
        student_registered_course.virtualCurrencyAmount = 100
        student_registered_course.save()

        # Create student config parameters for student instructor
        scparams = StudentConfigParams()
        scparams.studentID = student_instructor
        scparams.courseID = course
        scparams.save()

        # Create course config parameters
        ccparams = CourseConfigParams()
        ccparams.courseID = course
        ccparams.courseStartDate = timezone.now()
        ccparams.courseEndDate = localizedDate(None, default_time_str, "%m/%d/%Y %I:%M %p", timezone="utc")
        ccparams.gamificationUsed = True
        ccparams.progressBarUsed = True
        ccparams.progressBarGroupUsed = True
        ccparams.progressBarTotalPoints = 9000
        ccparams.xpWeightSChallenge = 50
        ccparams.xpWeightWChallenge = 50
        ccparams.xpCalculateSeriousByMaxScore = True
        ccparams.xpCalculateWarmupByMaxScore = True
        ccparams.save()

        # Add a default unassigned problem for this course
        default_unassigned_problem_challenge = Challenges()
        default_unassigned_problem_challenge.challengeName = unassigned_problems_challenge_name
        default_unassigned_problem_challenge.courseID = course
        default_unassigned_problem_challenge.numberAttempts = 0
        default_unassigned_problem_challenge.timeLimit = 0
        default_unassigned_problem_challenge.save()

        # Add a default topic for this course
        default_topic = Topics()
        default_topic.topicName = unspecified_topic_name
        default_topic.save()

        default_course_topic = CoursesTopics()
        default_course_topic.topicID = default_topic
        default_course_topic.courseID = course
        default_course_topic.save()

        # Add a default category
        default_activity_category = ActivitiesCategory()
        default_activity_category.name = uncategorized_activity
        default_activity_category.courseID = course
        default_activity_category.save()

        # Add a default manual earning VC rule
        default_manual_earning_rule = VirtualCurrencyCustomRuleInfo()
        default_manual_earning_rule.courseID = course
        default_manual_earning_rule.vcRuleName = unspecified_vc_manual_rule_name
        default_manual_earning_rule.vcRuleType = True
        default_manual_earning_rule.vcRuleDescription = unspecified_vc_manual_rule_description
        default_manual_earning_rule.vcRuleAmount = -1
        default_manual_earning_rule.vcAmountVaries = True
        default_manual_earning_rule.save()

    def create_students(self, amount=1):
        for i in range(1, amount+1):
            # Create user
            user = User.objects.create_user(f"banana-student-{i}", f"bstudent{i}@rams.wssu.edu", "b@naN&s")
            user.first_name = f"Diddy {i}"
            user.last_name = "Kong"
            user.save()
            
            # Create student with user
            student = Student()
            student.user = user
            student.universityID = "rams.wssu.edu"
            student.save()
            
            course = Courses.objects.get(courseName = "Test Course")

            # Link student to course
            student_registered_course = StudentRegisteredCourses()
            student_registered_course.studentID = student
            student_registered_course.courseID = course
            student_registered_course.avatarImage = anonymous_avatar
            student_registered_course.virtualCurrencyAmount = 100
            student_registered_course.save()

            # Create new student config parameters
            scparams = StudentConfigParams()
            scparams.courseID = course
            scparams.studentID = student
            scparams.save()

    @tag('performance')
    def test_class_progressbar_performance(self):
        self.printb(f"---------- [TEST] test_class_progressbar_performance ----------")

        student = Student.objects.get(user__first_name="Diddy 1")
        self.assertEqual(student.user.last_name, 'Kong')

        def create_challenges(for_course, graded=True, amount=10):

            def create_problem(for_challenge, amount=10):
                for i in range(1, amount+1):
                    question = StaticQuestions()
                    question.preview = f"Test TF Problem {i}"
                    question.type = QuestionTypes.trueFalse
                    question.instructorNotes = ""
                    question.questionText = ""
                    question.save()

                    points = for_challenge.totalScore // amount

                    answers = ['true', 'false']
                    random.shuffle(answers)

                    answer = Answers()
                    answer.questionID = question
                    answer.answerText = answers[0]
                    answer.save()

                    answer = Answers()
                    answer.questionID = question
                    answer.answerText = answers[1]
                    answer.save()

                    correctAnswerObject = CorrectAnswers()
                    correctAnswerObject.questionID = question
                    correctAnswerObject.answerID = answer
                    correctAnswerObject.save()

                    cq = ChallengesQuestions()
                    cq.challengeID = for_challenge
                    cq.questionID = question
                    cq.points = Decimal(points)
                    cq.questionPosition = 0
                    cq.save()

            unspecified_topic = CoursesTopics.objects.get(courseID=for_course, topicID__topicName=unspecified_topic_name).topicID
            for i in range(1, amount+1):
                self.printb(i)
                challenge = Challenges()
                challenge.challengeName = f"Test Challenge {i} {graded}"
                challenge.courseID = for_course
                challenge.isGraded = graded
                challenge.totalScore = amount*10
                challenge.manuallyGradedScore = 0
                challenge.numberAttempts = unlimited_constant
                challenge.timeLimit = unlimited_constant
                challenge.challengeAuthor = ""
                challenge.save()

                challTopic = ChallengesTopics()
                challTopic.challengeID = challenge
                challTopic.topicID = unspecified_topic
                challTopic.save()

                create_problem(challenge, amount=10)

        def take_challenges(for_course):
            students = StudentRegisteredCourses.objects.filter(studentID__isTestStudent=False)
            for student in students:
                challenges = Challenges.objects.all().exclude(challengeName=unassigned_problems_challenge_name)
                challenges = random.choices(challenges, k=random.choice(range(1, challenges.count())))
                for challenge in challenges:
                    studentChallenge = StudentChallenges()
                    studentChallenge.studentID = student.studentID
                    studentChallenge.courseID = for_course
                    studentChallenge.challengeID = challenge
                    studentChallenge.startTimestamp = timezone.now()
                    studentChallenge.endTimestamp = timezone.now()
                    # initially its zero and updated after calculation at the end
                    studentChallenge.testScore = 0
                    studentChallenge.save()

                    total_score = 0
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)
                    for challenge_question in challenge_questions:
                        score = random.choice(range(1, int(challenge_question.points)))
                        total_score += score

                        studentChallengeQuestion = StudentChallengeQuestions()
                        studentChallengeQuestion.studentChallengeID = studentChallenge
                        studentChallengeQuestion.questionID = challenge_question.questionID
                        studentChallengeQuestion.challengeQuestionID = challenge_question
                        studentChallengeQuestion.questionScore = score
                        studentChallengeQuestion.questionTotal = challenge_question.points
                        studentChallengeQuestion.usedHint = "False"
                        studentChallengeQuestion.seed = 0
                        studentChallengeQuestion.save()

                        studentChallengeAnswers = StudentChallengeAnswers()
                        studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                        studentChallengeAnswers.studentAnswer = "true"
                        studentChallengeAnswers.save()
                    
                    studentChallenge.testScore = total_score
                    studentChallenge.save()
                    self.printb(f"Student: {student.studentID.user.first_name} ", "scored ", f"{total_score} / {challenge.totalScore}", " for challenge ", f"{challenge.challengeName}", split=True)

        course = Courses.objects.get(courseName = "Test Course")
        create_challenges(course, amount=30)
        create_challenges(course, graded=False, amount=30)
        take_challenges(course)

        self.printb(f"Challenges Count {Challenges.objects.all().count()-1}")
        self.printb(f"Student Challenges Count {StudentChallenges.objects.all().count()}")
        # print(f"Student Challenges Scores {StudentChallenges.objects.all().values('testScore')}")

        
        # Login as instructor
        self.client.login(username=f'banana-student-{1}', password='b@naN&s')

        # Set course in session
        session = self.client.session
        session['currentCourseID'] = course.pk
        session.save()

        # Create an instance of a GET request.
        elapsed = time.perf_counter()
        self.printb(f"--------- Start Elapsed Time ----------")
        response = self.client.get('/oneUp/students/StudentCourseHome')

        context_dict = response.context
        eelapsed = time.perf_counter()
        self.printb(f"---------- End Elapsed Time ---------")

        self.printb(f"\ncurrentEarnedPoints {context_dict['currentEarnedPoints']}")
        self.printb(f"missedPoints {context_dict['missedPoints']}")
        self.printb(f"projectedEarnedPoints {context_dict['projectedEarnedPoints']}")
        self.printb(f"progressBarTotalPoints {context_dict['progressBarTotalPoints']}")
        self.printb(f"remainingPointsToEarn {context_dict['remainingPointsToEarn']}")
        self.printb(f"studentXP_range {context_dict['studentXP_range']}")
        self.printb(f"totalWCEarnedPoints {context_dict['totalWCEarnedPoints']}")
        self.printb(f"totalWCPossiblePoints {context_dict['totalWCPossiblePoints']}")
        

        self.assertEqual(response.status_code, 200)

    def test_other(self):
        self.printb(f"---------- [TEST] test_other ----------")
        student = Student.objects.get(user__first_name="Diddy 1")
        self.assertEqual(student.user.last_name, 'Kong')

@tag('browser')
class StudentCourseHomeBrowserTest(StaticLiveServerTestCase, CommonTestCase):

    # Database JSON dump useful for tests that needs a lot of data created
    # Use manage.py dumpdata to create e.g ./manage.py dumpdata Badges.Model1 Students.Model2 --indent=4 > dump.json
    # fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        super(StudentCourseHomeBrowserTest, cls).setUpClass()
        cls.printb("---------- Launching Chrome ---------")
        cls.selenium = WebDriver()
        cls.selenium.maximize_window()    
        cls.selenium.implicitly_wait(10)
        
    
    def setUp(self):
        # Set up data for each test method (model instances that may be modified by the tests)
        super(StudentCourseHomeBrowserTest, self).init_common()
        
        self.printb("---------- Creating Courses, Instructors, Students, etc ---------")
        self.create_admins()
        self.create_universities()
        self.create_instructors()
        self.create_courses()
        self.create_students(amount=100)    

    def create_admins(self):
        admin = User.objects.create_superuser("banana-admin", "admin@oneup.com", "admin")
        admin.first_name = "Cranky"
        admin.last_name = "Kong"
        admin.save() 
    
    def create_universities(self):
        university = Universities()
        university.universityName = "Banana U"
        university.save()

    def create_instructors(self):
        instructor = User.objects.create_user("banana-instructor", "banana@wssu.edu", "B@Nan*S?")
        instructor.first_name = "Donkey"
        instructor.last_name = "Kong"
        instructor.groups.add(self.teacher_group)
        instructor.save()

        student = Student()
        student.user = instructor
        student.universityID = "rams.wssu.edu"
        student.isTestStudent = True
        student.save()  

    def create_courses(self):
        # Create course
        course = Courses()
        course.courseName = "Test Course"
        course.courseDescription = "Used for django testing"
        course.save()
        
        instructor = User.objects.get(username="banana-instructor", groups__name="Teachers")
        student_instructor = Student.objects.get(user=instructor)

        # Link instructor to course
        irc = InstructorRegisteredCourses()
        irc.instructorID = instructor
        irc.courseID = course
        irc.save()

        # Link university to course
        uC = UniversityCourses()
        uC.universityID = Universities.objects.get(universityName="Banana U")
        uC.courseID = course
        uC.save()

        # Link student instructor to course
        student_registered_course = StudentRegisteredCourses()
        student_registered_course.studentID = student_instructor
        student_registered_course.courseID = course
        student_registered_course.avatarImage = anonymous_avatar
        student_registered_course.virtualCurrencyAmount = 100
        student_registered_course.save()

        # Create student config parameters for student instructor
        scparams = StudentConfigParams()
        scparams.studentID = student_instructor
        scparams.courseID = course
        scparams.save()

        # Create course config parameters
        ccparams = CourseConfigParams()
        ccparams.courseID = course
        ccparams.courseStartDate = timezone.now()
        ccparams.courseEndDate = localizedDate(None, default_time_str, "%m/%d/%Y %I:%M %p", timezone="utc")
        ccparams.gamificationUsed = True
        ccparams.progressBarUsed = True
        ccparams.progressBarGroupUsed = True
        ccparams.progressBarTotalPoints = 9000
        ccparams.xpWeightSChallenge = 50
        ccparams.xpWeightWChallenge = 50
        ccparams.xpCalculateSeriousByMaxScore = True
        ccparams.xpCalculateWarmupByMaxScore = True
        ccparams.save()

        # Add a default unassigned problem for this course
        default_unassigned_problem_challenge = Challenges()
        default_unassigned_problem_challenge.challengeName = unassigned_problems_challenge_name
        default_unassigned_problem_challenge.courseID = course
        default_unassigned_problem_challenge.numberAttempts = 0
        default_unassigned_problem_challenge.timeLimit = 0
        default_unassigned_problem_challenge.save()

        # Add a default topic for this course
        default_topic = Topics()
        default_topic.topicName = unspecified_topic_name
        default_topic.save()

        default_course_topic = CoursesTopics()
        default_course_topic.topicID = default_topic
        default_course_topic.courseID = course
        default_course_topic.save()

        # Add a default category
        default_activity_category = ActivitiesCategory()
        default_activity_category.name = uncategorized_activity
        default_activity_category.courseID = course
        default_activity_category.save()

        # Add a default manual earning VC rule
        default_manual_earning_rule = VirtualCurrencyCustomRuleInfo()
        default_manual_earning_rule.courseID = course
        default_manual_earning_rule.vcRuleName = unspecified_vc_manual_rule_name
        default_manual_earning_rule.vcRuleType = True
        default_manual_earning_rule.vcRuleDescription = unspecified_vc_manual_rule_description
        default_manual_earning_rule.vcRuleAmount = -1
        default_manual_earning_rule.vcAmountVaries = True
        default_manual_earning_rule.save()

    def create_students(self, amount=1):
        for i in range(1, amount+1):
            # Create user
            user = User.objects.create_user(f"banana-student-{i}", f"bstudent{i}@rams.wssu.edu", "b@naN&s")
            user.first_name = f"Diddy {i}"
            user.last_name = "Kong"
            user.save()
            
            # Create student with user
            student = Student()
            student.user = user
            student.universityID = "rams.wssu.edu"
            student.save()
            
            course = Courses.objects.get(courseName = "Test Course")

            # Link student to course
            student_registered_course = StudentRegisteredCourses()
            student_registered_course.studentID = student
            student_registered_course.courseID = course
            student_registered_course.avatarImage = anonymous_avatar
            student_registered_course.virtualCurrencyAmount = 100
            student_registered_course.save()

            # Create new student config parameters
            scparams = StudentConfigParams()
            scparams.courseID = course
            scparams.studentID = student
            scparams.save()
        

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_challenges_created(self):
        self.printb(f"---------- [TEST] test_challenges_created ----------")

        def create_challenges(for_course, graded=True, amount=10):

            def create_problem(for_challenge, amount=10):
                for i in range(1, amount+1):
                    question = StaticQuestions()
                    question.preview = f"Test TF Problem {i}"
                    question.type = QuestionTypes.trueFalse
                    question.instructorNotes = ""
                    question.questionText = ""
                    question.save()

                    points = for_challenge.totalScore // amount

                    answers = ['true', 'false']
                    random.shuffle(answers)

                    answer = Answers()
                    answer.questionID = question
                    answer.answerText = answers[0]
                    answer.save()

                    answer = Answers()
                    answer.questionID = question
                    answer.answerText = answers[1]
                    answer.save()

                    correctAnswerObject = CorrectAnswers()
                    correctAnswerObject.questionID = question
                    correctAnswerObject.answerID = answer
                    correctAnswerObject.save()

                    cq = ChallengesQuestions()
                    cq.challengeID = for_challenge
                    cq.questionID = question
                    cq.points = Decimal(points)
                    cq.questionPosition = 0
                    cq.save()
            
            unspecified_topic = CoursesTopics.objects.get(courseID=for_course, topicID__topicName=unspecified_topic_name).topicID
            for i in range(1, amount+1):
                challenge = Challenges()
                challenge.challengeName = f"Test Challenge {i} {graded}"
                challenge.courseID = for_course
                challenge.isGraded = graded
                challenge.totalScore = amount*10
                challenge.manuallyGradedScore = 0
                challenge.numberAttempts = unlimited_constant
                challenge.timeLimit = unlimited_constant
                challenge.challengeAuthor = ""
                challenge.save()

                challTopic = ChallengesTopics()
                challTopic.challengeID = challenge
                challTopic.topicID = unspecified_topic
                challTopic.save()

                create_problem(challenge, amount=10)

        def take_challenges(for_course):
            students = StudentRegisteredCourses.objects.filter(studentID__isTestStudent=False)
            for student in students:
                challenges = Challenges.objects.all().exclude(challengeName=unassigned_problems_challenge_name)
                challenges = random.choices(challenges, k=random.choice(range(1, challenges.count())))
                for challenge in challenges:
                    studentChallenge = StudentChallenges()
                    studentChallenge.studentID = student.studentID
                    studentChallenge.courseID = for_course
                    studentChallenge.challengeID = challenge
                    studentChallenge.startTimestamp = timezone.now()
                    studentChallenge.endTimestamp = timezone.now()
                    # initially its zero and updated after calculation at the end
                    studentChallenge.testScore = 0
                    studentChallenge.save()

                    total_score = 0
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)
                    for challenge_question in challenge_questions:
                        score = random.choice(range(1, int(challenge_question.points)))
                        total_score += score

                        studentChallengeQuestion = StudentChallengeQuestions()
                        studentChallengeQuestion.studentChallengeID = studentChallenge
                        studentChallengeQuestion.questionID = challenge_question.questionID
                        studentChallengeQuestion.challengeQuestionID = challenge_question
                        studentChallengeQuestion.questionScore = score
                        studentChallengeQuestion.questionTotal = challenge_question.points
                        studentChallengeQuestion.usedHint = "False"
                        studentChallengeQuestion.seed = 0
                        studentChallengeQuestion.save()

                        studentChallengeAnswers = StudentChallengeAnswers()
                        studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                        studentChallengeAnswers.studentAnswer = "true"
                        studentChallengeAnswers.save()
                    
                    studentChallenge.testScore = total_score
                    studentChallenge.save()
                    # self.printb(f"Student: {student.studentID.user.first_name} ", "scored ", f"{total_score} / {challenge.totalScore}", " for challenge ", f"{challenge.challengeName}", split=True)

        course = Courses.objects.get(courseName = "Test Course")
        self.printb("---------- Creating Challenges ---------")
        create_challenges(course, amount=30)
        create_challenges(course, graded=False, amount=30)
        self.printb("---------- Taking Those Challenges ---------")
        take_challenges(course)

        self.printb("---------- Browsing ---------")
        
        self.selenium.get('%s%s' % (self.live_server_url, '/oneUp/home/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('banana-instructor')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('B@Nan*S?')
        self.selenium.find_element_by_name('login').click()

        WebDriverWait(self.selenium, 10).until(lambda driver: driver.find_element_by_tag_name('main'))
        
        courses_buttons = self.selenium.find_elements_by_name('submit')
        self.printb(courses_buttons[0].text)
        courses_buttons[0].click()
        
        nav_buttons = self.selenium.find_elements_by_link_text("Course Content")
        nav_buttons[0].click()

        warmup_buttons = self.selenium.find_elements_by_link_text("Warm-Up Challenges")
        warmup_buttons[0].click()

        WebDriverWait(self.selenium, 10).until(lambda driver: driver.find_elements_by_xpath("//li[@class='ui-sortable-handle']")[0])
        
        header = self.selenium.find_elements_by_xpath("//li[@class='ui-sortable-handle']")[0]
        action = ActionChains(self.selenium)
        action.move_to_element(header)
        action.click()
        action.perform()

        element_text = self.selenium.find_element_by_xpath("//div[@class='no-padding' and contains(., 'Test Challenge 1 False')]").get_attribute('textContent')
        self.printb(element_text)

        self.assertTrue('Test Challenge 1 False' in element_text, msg="There is no warmup challenge called 'Test Challenge 1 False'")
        # WebDriverWait(self.selenium, 600).until(lambda driver: driver.find_element_by_tag_name('man'))

    def test_loading_student_course_page(self):
        self.printb(f"---------- [TEST] test_loading_student_course_page ----------")

        self.printb("---------- Browsing ---------")
        student = Student.objects.get(user__first_name="Diddy 1")
    
        self.selenium.get('%s%s' % (self.live_server_url, '/oneUp/home/'))
        username_input = self.selenium.find_element_by_name("username").send_keys(student.user.username)
        password_input = self.selenium.find_element_by_name("password").send_keys("b@naN&s")
        self.selenium.find_element_by_name('login').click()

        WebDriverWait(self.selenium, 10).until(lambda driver: driver.find_element_by_tag_name('main'))
        
        courses_buttons = self.selenium.find_elements_by_name('submit')
        self.printb(courses_buttons[0].text)
        courses_buttons[0].click()
        WebDriverWait(self.selenium, 600).until(lambda driver: driver.find_element_by_tag_name('man'))



