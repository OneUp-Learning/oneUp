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
        StudentChallengeQuestions, StudentLeaderboardHistory, StudentActions, StudentActionsLoop, DuelChallenges, CalloutStats, Callouts

    from Badges.enums import Event
    from Badges.systemVariables import getNumberOfDuelsWon, getNumberOfDuelsLost

    from Badges.periodicVariables import periodic_task, TimePeriods
    from django_celery_beat.models import PeriodicTask, PeriodicTasks
    from Instructors.views.utils import utcDate
    from django.core.exceptions import ObjectDoesNotExist
    import json
    from datetime import timedelta
    from django.utils import timezone

    last_ran = PeriodicTask.objects.get(name='student_data_mine_actions').last_run_at
    print("RUNNING THESIS")
    print("LAST RAN AT {}".format(last_ran))

    ''' "Student", "Course", "Problems Correct", "Problems Incorrect", "Gamification", 
            "Badges Earned", "VC Earned", "Max Possible VC", "VC%", "Leaderboard Appearances", 
            "Duels Won", "Duels Lost", "Unique Warmups Taken", "Warmups Attempted", 
            "Warmups Low", "Warmups Mid", "Warmups High"
    '''

    # courses = Courses.objects.all()
    courses_to_look_at = [37, 30, 28]
    courses = Courses.objects.filter(courseID__in=courses_to_look_at)

    actions = [Event.endChallenge, Event.duelSent, Event.calloutSent, Event.duelAccepted]
    feedbacks = [Event.virtualCurrencyEarned, Event.badgeEarned, Event.duelWon, Event.calloutWon, Event.duelLost, Event.calloutLost]

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
                vc_earnings = vc_earnings.filter(timestamp__gt=last_ran)

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
            
            # Create new student actions entry
            student_actions_data = StudentActions()
            student_actions_data.courseID = course
            student_actions_data.studentID = student
            student_actions_data.save()

            json_data['Student'] = student.user.first_name + " " + student.user.last_name
            json_data['Course'] = course.courseName
            json_data['Gamification'] = course_config.gamificationUsed

            student_actions_all = None
            if last_ran:
                student_actions_all = StudentEventLog.objects.filter(student=student, course=course, event__in=actions, timestamp__gt=last_ran).order_by('timestamp')
            else:
                student_actions_all = StudentEventLog.objects.filter(student=student, course=course, event__in=actions, timestamp__gt=timezone.now() - timedelta(weeks=12)).order_by('timestamp')
            
            if student_actions_all:
                start_timestamp = student_actions_all[0].timestamp
                end_timestamp = start_timestamp + timedelta(hours=1)
                current_time = timezone.now()

                while end_timestamp <= current_time:
                student_actions_subset = student_actions_all.filter(timestamp__gte=start_timestamp, timestamp__lt=end_timestamp)

                if student_actions_subset:
                    save = False
                    action_loop = StudentActionsLoop()
                    action_loop.studentActionsID = student_actions_data
                    for student_action in student_actions_subset:
                        event = student_action.event
                        if event == Event.endChallenge:
                            challenge_id = student_action.objectID
                            if not challenge_id:
                                continue
                            student_challenge = StudentChallenges.objects.filter(pk=challenge_id)
                            if student_challenge:
                                if hasattr(student_challenge, 'challengeID'):
                                    if student_challenge.challengeID.isGraded:
                                        save = True
                                        action_loop.serious_attempted += 1
                                    else:
                                        save = True
                                        action_loop.warmups_attempted += 1
                        elif event == Event.duelSent:
                            save = True
                            action_loop.duels_sent += 1
                        elif event == Event.duelAccepted:
                            save = True
                            action_loop.duels_accepted += 1
                        elif event == Event.calloutSent:
                            save = True
                            action_loop.callouts_sent += 1
                    
                    callouts_participated = len(CalloutStats.objects.filter(studentID=student, courseID=course, submitTime__gte=start_timestamp, submitTime__lt=end_timestamp))
                    if callouts_participated > 0:
                        save = True
                        action_loop.callouts_participated += callouts_participated

                    # Find feedback
                    student_feedbacks = StudentEventLog.objects.filter(student=student, course=course, event__in=feedbacks, timestamp__gte=start_timestamp, timestamp__lt=end_timestamp)
                    for student_feedback in student_feedbacks:
                        event = student_action.event
                        if event == Event.virtualCurrencyEarned:
                            save = True
                            action_loop.vc_earned += 1
                        elif event == Event.badgeEarned:
                            save = True
                            action_loop.badges_earned += 1
                        elif event == Event.duelWon:
                            save = True
                            action_loop.duels_won += 1
                        elif event == Event.calloutWon:
                            save = True
                            action_loop.callouts_won += 1
                        elif event == Event.duelLost:
                            save = True
                            action_loop.duels_lost += 1
                        elif event == Event.calloutLost:
                            save = True
                            action_loop.callouts_lost += 1

                    leaderboards = StudentLeaderboardHistory.objects.filter(studentID=student, courseID=course, startTimestamp__gte=start_timestamp, startTimestamp__lt=end_timestamp)
                    if leaderboards:
                        save = True
                        action_loop.on_leaderboard = True

                    for warmup_challenge in course_challenges.filter(isGraded=False):
                        student_challenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=warmup_challenge, endTimestamp__gte=start_timestamp, endTimestamp__lt=end_timestamp).exclude(endTimestamp__isnull=True)

                        if student_challenges.exists():
                            gradeID  = []
                            for student_challenge in student_challenges:
                                gradeID.append(student_challenge.testScore)
                            
                            #Calculation for ranking score by 3 levels (hight, mid, low)
                            tTotal=(warmup_challenge.totalScore/3)
                            
                            if (max(gradeID) >= (2*tTotal)): # High
                                save = True
                                action_loop.high_score_challenges += 1
                            # elif (max(gradeID) > tTotal) and (max(gradeID) < (2*tTotal)): # Mid
                            #     warmup_challenge_mids += 1
                            elif max(gradeID) < tTotal: # Low
                                save = True
                                action_loop.low_score_challenges += 1
                    if save:
                        action_loop.save()

                start_timestamp = end_timestamp
                end_timestamp = end_timestamp + timedelta(hours=1)

            # Problems Correct / Incorrect
            problems_correct = 0
            problems_incorrect = 0
            for challenge in course_challenges:
                student_challenges = StudentChallenges.objects.filter(courseID=course, challengeID=challenge, studentID=student).exclude(endTimestamp__isnull=True)

                # Get problems correct / incorrect for past hour
                if last_ran:
                    student_challenges = student_challenges.filter(endTimestamp__gt=last_ran)

                for student_challenge in student_challenges:
                    problem_answers = StudentChallengeQuestions.objects.filter(studentChallengeID=student_challenge)
                    for problem_answer in problem_answers:
                        if problem_answer.questionScore == problem_answer.questionTotal:
                            problems_correct += 1
                        else:
                            problems_incorrect += 1

            json_data['Problems Correct'] = problems_correct
            json_data['Problems Incorrect'] = problems_incorrect


            json_data['Max Possible VC'] = max_vc
           

            # Warmup Challenges
            unique_warmups = 0
            warmup_challenge_mids = 0

            for warmup_challenge in course_challenges.filter(isGraded=False):
                student_challenges = StudentChallenges.objects.filter(courseID=course, studentID=student, challengeID=warmup_challenge).exclude(endTimestamp__isnull=True)
                
                # Warmup challenges taken for past hour
                if last_ran:
                    student_challenges = student_challenges.filter(endTimestamp__gt=last_ran)

                if student_challenges.exists():
                    unique_warmups += 1

                    gradeID  = []
                    for student_challenge in student_challenges:
                        gradeID.append(student_challenge.testScore)
                    
                    #Calculation for ranking score by 3 levels (hight, mid, low)
                    tTotal=(warmup_challenge.totalScore/3)
                    
                    
                    if (max(gradeID) > tTotal) and (max(gradeID) < (2*tTotal)): # Mid
                        warmup_challenge_mids += 1
                
            json_data['Unique Warmups Taken'] = unique_warmups


            if unique_warmups == 0:
                json_data['Warmups Mid'] = 0
            else:
                json_data['Warmups Mid'] = (warmup_challenge_mids / unique_warmups) * 100
                

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
        crontab=get_or_create_schedule(minute='59', hour='23', day_of_week='6'),
    )
            
if settings.CELERY_ENABLED:
    schedule_celery_task_data_mine()

