from django.conf import settings
from Badges.celeryApp import app

@app.task(ignore_result=True)
def student_data_mine_actions():
    ''' This will go run through for every student in courses and calculate their actions and related data to be used for thesis work.

        This celery task will run every hour.

    '''
    from Instructors.models import Challenges, Courses
    from Badges.models import Badges, CourseConfigParams, BadgesInfo
    from Students.models import StudentRegisteredCourses, StudentVirtualCurrency, StudentBadges, StudentChallenges, StudentEventLog, \
        StudentChallengeQuestions, StudentLeaderboardHistory, StudentActions, DuelChallenges, CalloutStats, Callouts

    from Badges.enums import Event
    from Badges.systemVariables import getNumberOfDuelsWon, getNumberOfDuelsLost

    from Badges.periodicVariables import periodic_task, TimePeriods
    from django_celery_beat.models import PeriodicTask, PeriodicTasks
    from Instructors.views.utils import utcDate
    from django.core.exceptions import ObjectDoesNotExist
    import json

    last_ran = PeriodicTask.objects.get(name='student_data_mine_actions').last_run_at

    ''' "Student", "Course", "Problems Correct", "Problems Incorrect", "Gamification", 
            "Badges Earned", "VC Earned", "Max Possible VC", "VC%", "Leaderboard Appearances", 
            "Duels Won", "Duels Lost", "Unique Warmups Taken", "Warmups Attempted", 
            "Warmups Low", "Warmups Mid", "Warmups High", "Avg Score Serious Challenges"
    '''

    # courses = Courses.objects.all()
    courses_to_look_at = [37, 30, 28]
    courses = Courses.objects.filter(courseID__in=courses_to_look_at)

    for course in courses:
        print("Courses: {}".format(course.courseName))
        students_registered_courses = StudentRegisteredCourses.objects.filter(courseID=course).exclude(studentID__isTestStudent=True)
        course_challenges = Challenges.objects.filter(courseID=course)
        course_config = CourseConfigParams.objects.get(courseID=course)
        course_badges = BadgesInfo.objects.filter(courseID=course)
        
        max_vc = 0
        for students_registered_course in students_registered_courses:
            student = students_registered_course.studentID
            vc_earnings = StudentVirtualCurrency.objects.filter(studentID = student, courseID = course)
            # Find Max earnings for the past hour
            if last_ran:
                vc_earnings = vc_earnings.filter(timestamp__gte=last_ran)

            if vc_earnings:
                earnings = [int(earn.value) for earn in vc_earnings if earn.value > 0]
                if earnings:
                    vc = max(earnings)
                    if vc > max_vc:
                        max_vc = vc
        
        for students_registered_course in students_registered_courses:
            json_data = {}
            
            student = students_registered_course.studentID
            print("Students: {}".format(student.user.first_name))

            # Get the latest student actions entry
            # try:
            #     prev_student_actions_data = StudentActions.objects.filter(courseID=course, studentID=student).latest('timestamp')
            # except ObjectDoesNotExist:
            #     prev_student_actions_data = None
            
            # Create new student actions entry
            student_actions_data = StudentActions()
            student_actions_data.courseID = course
            student_actions_data.studentID = student

            json_data['Student'] = student.user.first_name + " " + student.user.last_name
            json_data['Course'] = course.courseName
            json_data['Gamification'] = course_config.gamificationUsed

            # Problems Correct / Incorrect
            problems_correct = 0
            problems_incorrect = 0
            for challenge in course_challenges:
                student_challenges = StudentChallenges.objects.filter(courseID=course, challengeID=challenge, studentID=student).exclude(endTimestamp__isnull=True)

                # Get problems correct / incorrect for past hour
                if last_ran:
                    student_challenges = student_challenges.filter(endTimestamp__gte=last_ran)

                for student_challenge in student_challenges:
                    problem_answers = StudentChallengeQuestions.objects.filter(studentChallengeID=student_challenge)
                    for problem_answer in problem_answers:
                        if problem_answer.questionScore == problem_answer.questionTotal:
                            problems_correct += 1
                        else:
                            problems_incorrect += 1

            json_data['Problems Correct'] = problems_correct
            json_data['Problems Incorrect'] = problems_incorrect

            # Badges
            badges_total = 0
            for course_badge in course_badges:
                student_badges = StudentBadges.objects.filter(badgeID=course_badge, studentID=student)
                # Get badges earned for past hour
                if last_ran:
                    student_badges = student_badges.filter(timestamp__gte=last_ran)

                badges_total += student_badges.count()
            json_data['Badges Earned'] = badges_total

            # Virtual Currency
            total = 0
            vc_earnings = StudentVirtualCurrency.objects.filter(studentID=student, courseID=course)
            # Get VC earned in past hour
            if last_ran:
                vc_earnings = vc_earnings.filter(timestamp__gte=last_ran)
            if vc_earnings:
                earnings = [int(earn.value) for earn in vc_earnings if earn.value > 0]
                if earnings:
                    total = sum(earnings)

            json_data['VC Earned'] = total
            json_data['Max Possible VC'] = max_vc

            if max_vc == 0:
                json_data['VC%'] = 0
            else:
                json_data['VC%'] = (total / max_vc) * 100

            # leaderboards = StudentLeaderboardHistory.objects.filter(studentID=student, courseID=course).order_by('-startTimestamp')
            # if leaderboards:
            #     if len(leaderboards) > 1:
            #         prev_leaderboard = leaderboards[1]
            #         current_leaderboard = leaderboards[0]
            #         if current_leaderboard.startTimestamp >= last_ran:

            #         else:
            #             leaderboard_appearances.append(False)
            #     else:
            #         leaderboard_appearances.append(True)
            # else:
            #     leaderboard_appearances.append(False)

            # Leaderboards

            leaderboards = StudentLeaderboardHistory.objects.filter(studentID=student, courseID=course)
            if last_ran:
                leaderboards = leaderboards.filter(startTimestamp__gte=last_ran)
                
            if leaderboards:
                leaderboards = leaderboards.latest('startTimestamp')
                json_data['Leaderboard Appearances'] = True
            else:
                json_data['Leaderboard Appearances'] = False

            # Duels
            duels_w = getNumberOfDuelsWon(course, student)
            json_data['Duels Won'] = duels_w

            duels_l = getNumberOfDuelsLost(course, student)
            json_data['Duels Lost'] = duels_l

            # Duels Sent
            duel_challenges = DuelChallenges.objects.filter(challenger=student, courseID=course)
            # Duels sent & accepted for past hour
            if last_ran:
                duel_challenges = duel_challenges.filter(sendTime__gte=last_ran)

            student_actions_data.duels_sent = len(duel_challenges)

            # Duels Accepted
            duel_challenges = duel_challenges.filter(status=2)
            student_actions_data.duels_accepted = len(duel_challenges)

            # Callouts Sent & Accepted
            callouts_sent = Callouts.objects.filter(sender=student, courseID=course)
            callouts_accepted = CalloutStats.objects.filter(studentID=student, courseID=course)
            # Callouts sent & accepted for past hour
            if last_ran:
                callouts_sent = callouts_sent.filter(sendTime__gte=last_ran)
                callouts_accepted = callouts_accepted.filter(submitTime__gte=last_ran)
            
            student_actions_data.callouts_sent = len(callouts_sent)
            student_actions_data.callouts_accepted = len(callouts_accepted)

            
            # Serious Challenges Attempted
            serious_attempted = 0
            for serious_challenge in course_challenges.filter(isGraded=True):
                student_challenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=serious_challenge).exclude(endTimestamp__isnull=True)
                
                if last_ran:
                    student_challenges = student_challenges.filter(endTimestamp__gte=last_ran)

                if student_challenges.exists():
                    serious_attempted += student_challenges.count()

            student_actions_data.serious_attempted = serious_attempted

            # Warmup Challenges
            unique_warmups = 0
            warmups_attempted = 0
            warmup_challenge_lows = 0
            warmup_challenge_mids = 0
            warmup_challenge_highs = 0

            for warmup_challenge in course_challenges.filter(isGraded=False):
                student_challenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=warmup_challenge).exclude(endTimestamp__isnull=True)
                
                # Warmup challenges taken for past hour
                if last_ran:
                    student_challenges = student_challenges.filter(endTimestamp__gte=last_ran)

                if student_challenges.exists():
                    unique_warmups += 1
                    warmups_attempted += student_challenges.count()

                    gradeID  = []
                    for student_challenge in student_challenges:
                        gradeID.append(student_challenge.testScore)
                    
                    #Calculation for ranking score by 3 levels (hight, mid, low)
                    tTotal=(student_challenge.challengeID.totalScore/3)
                    
                    if (max(gradeID) >= (2*tTotal)): # High
                        warmup_challenge_highs += 1
                    elif (max(gradeID) > tTotal) and (max(gradeID) < (2*tTotal)): # Mid
                        warmup_challenge_mids += 1
                    else: # Low
                        warmup_challenge_lows += 1
                
            json_data['Unique Warmups Taken'] = unique_warmups
            json_data['Warmups Attempted'] = warmups_attempted

            student_actions_data.warmups_attempted = warmups_attempted

            if unique_warmups == 0:
                json_data['Warmups Low'] = 0
                json_data['Warmups Mid'] = 0
                json_data['Warmups High'] = 0
            else:
                json_data['Warmups Low'] = (warmup_challenge_lows / unique_warmups) * 100
                json_data['Warmups Mid'] = (warmup_challenge_mids / unique_warmups) * 100
                json_data['Warmups High'] = (warmup_challenge_highs / unique_warmups) * 100
                

            json_data['Avg Score Serious Challenges'] = 0

            # Save student data as json too
            student_actions_data.json_data = json.dumps(json_data)
            print("Data: {}".format(json_data))
            print("Saving")
            # Save the student actions data
            student_actions_data.save()

    task = PeriodicTask.objects.get(name='student_data_mine_actions')
    task.last_run_at = utcDate()
    task.save()
    PeriodicTasks.changed(task)

def schedule_celery_task_data_mine():
    ''' This will create the celery task (student_data_mine_actions) if it doesn't 
        exist and will schedule it to run every 1 hour '''
    
    from django_celery_beat.models import PeriodicTask
    from Badges.periodicVariables import get_or_create_schedule
    tasks = PeriodicTask.objects.filter(name='student_data_mine_actions')
    if tasks:
        tasks.delete()
    periodic_task, _ = PeriodicTask.objects.get_or_create(
        name='student_data_mine_actions',
        task='Badges.datamine_tasks.student_data_mine_actions',
        crontab=get_or_create_schedule(minute='0', hour='*'),
    )
            
if settings.CELERY_ENABLED:
    schedule_celery_task_data_mine()

