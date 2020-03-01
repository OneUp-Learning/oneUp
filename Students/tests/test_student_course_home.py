from django.test import TestCase, Client, override_settings, tag
from Students.views.studentCourseHomeView import StudentCourseHome

import random
import time
from decimal import Decimal

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from Instructors.models import InstructorRegisteredCourses, Courses, Universities, UniversityCourses, Challenges, Topics, CoursesTopics, ActivitiesCategory
from Badges.models import CourseConfigParams, VirtualCurrencyCustomRuleInfo
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams

from Instructors.views.utils import utcDate
from Instructors.constants import anonymous_avatar, default_time_str, unassigned_problems_challenge_name, uncategorized_activity, unspecified_topic_name, unspecified_vc_manual_rule_description, unspecified_vc_manual_rule_name, unlimited_constant


from Instructors.questionTypes import QuestionTypes
from Instructors.models import StaticQuestions, Answers, CorrectAnswers, ChallengesQuestions
from Students.models import StudentChallengeAnswers, StudentChallengeQuestions, StudentChallenges

class StudentCourseHomeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase. Model instances created cannot be modified
        cls.create_permissions()

    @classmethod
    def create_permissions(cls):
        user_content_type = ContentType.objects.get_for_model(User)

        cls.create_teachers_permission, created = Permission.objects.get_or_create(name='Create Teachers', codename='cr_teacher', content_type=user_content_type)
        cls.create_students_permission, created = Permission.objects.get_or_create(name='Create Students', codename='cr_student', content_type=user_content_type)
        cls.create_admins_permission, created = Permission.objects.get_or_create(name='Create Admins', codename='cr_admin', content_type=user_content_type)

        cls.admin_group, created = Group.objects.get_or_create(name='Admins')
        cls.admin_group.permissions.add(cls.create_teachers_permission, cls.create_students_permission, cls.create_admins_permission)

        cls.teacher_group, created = Group.objects.get_or_create(name='Teachers')
        cls.teacher_group.permissions.add(cls.create_students_permission)

    def setUp(self):
        # Set up data for each test method (model instances that may be modified by the tests)
        self.create_universities()
        self.create_instructors()
        self.create_courses()
        self.create_students(amount=100)        
    

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
        course = Courses()
        course.courseName = "Test Course"
        course.courseDescription = "Used for django testing"
        course.save()
        
        instructor = User.objects.get(username="banana-instructor", groups__name="Teachers")
        student_instructor = Student.objects.get(user=instructor)

        irc = InstructorRegisteredCourses()
        irc.instructorID = instructor
        irc.courseID = course
        irc.save()

        student_registered_course = StudentRegisteredCourses()
        student_registered_course.studentID = student_instructor
        student_registered_course.courseID = course
        student_registered_course.avatarImage = anonymous_avatar
        student_registered_course.virtualCurrencyAmount = 100
        student_registered_course.save()

        scparams = StudentConfigParams()
        scparams.studentID = student_instructor
        scparams.courseID = course
        scparams.save()

        ccparams = CourseConfigParams()
        ccparams.courseID = course
        ccparams.courseStartDate = utcDate()
        ccparams.courseEndDate = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
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
            user = User.objects.create_user(f"banana-student-{i}", f"bstudent{i}@rams.wssu.edu", "b@naN&s")
            user.first_name = f"Diddy {i}"
            user.last_name = "Kong"
            user.save()
            
            student = Student()
            student.user = user
            student.universityID = "rams.wssu.edu"
            student.save()
            
            course = Courses.objects.get(courseName = "Test Course")

            student_registered_course = StudentRegisteredCourses()
            student_registered_course.studentID = student
            student_registered_course.courseID = course
            student_registered_course.avatarImage = anonymous_avatar
            student_registered_course.virtualCurrencyAmount = 100
            student_registered_course.save()

            # Create new Config Parameters
            scparams = StudentConfigParams()
            scparams.courseID = course
            scparams.studentID = student
            scparams.save()

    @tag('performance')
    def test_class_progressbar_performance(self):

        def printb(*text, split=False):
            print("".join(list(map(lambda x: f"\033[1m{x}\033[0m" if text.index(x) % 2 == 0 or split == False else f"{x}", text))))

        # Some test using self.foo
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
            
            for i in range(1, amount+1):
                printb(i)
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
                    studentChallenge.startTimestamp = utcDate()
                    studentChallenge.endTimestamp = utcDate()
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
                    printb(f"Student: {student.studentID.user.first_name} ", "scored ", f"{total_score} / {challenge.totalScore}", " for challenge ", f"{challenge.challengeName}", split=True)

        course = Courses.objects.get(courseName = "Test Course")
        create_challenges(course, amount=30)
        create_challenges(course, graded=False, amount=30)
        take_challenges(course)

        printb(f"Challenges Count {Challenges.objects.all().count()-1}")
        printb(f"Student Challenges Count {StudentChallenges.objects.all().count()}")
        # print(f"Student Challenges Scores {StudentChallenges.objects.all().values('testScore')}")

        
        self.client.login(username=f'banana-student-{1}', password='b@naN&s')

        session = self.client.session
        session['currentCourseID'] = course.pk
        session.save()

        # Create an instance of a GET request.
        elapsed = time.perf_counter()
        printb(f"Start Elapsed Time {elapsed}s")
        response = self.client.get('/oneUp/students/StudentCourseHome')

        context_dict = response.context
        eelapsed = time.perf_counter()
        printb(f"End Elapsed Time {eelapsed}s (diff {eelapsed - elapsed}s)\n")

        printb(f"currentEarnedPoints {context_dict['currentEarnedPoints']}")
        printb(f"missedPoints {context_dict['missedPoints']}")
        printb(f"projectedEarnedPoints {context_dict['projectedEarnedPoints']}")
        printb(f"progressBarTotalPoints {context_dict['progressBarTotalPoints']}")
        printb(f"remainingPointsToEarn {context_dict['remainingPointsToEarn']}")
        printb(f"studentXP_range {context_dict['studentXP_range']}")
        printb(f"totalWCEarnedPoints {context_dict['totalWCEarnedPoints']}")
        printb(f"totalWCPossiblePoints {context_dict['totalWCPossiblePoints']}")

        self.assertEqual(response.status_code, 200)






