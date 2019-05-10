'''
Created on Nov 2, 2018
@author: omar
'''
#from Students.models import DuelChallenges
from django.shortcuts import render, redirect
from Students.views.utils import studentInitialContextDict
from Instructors.views.utils import utcDate
from Badges.models import CourseConfigParams
from Students.models import StudentRegisteredCourses, DuelChallenges, StudentChallenges, Winners, StudentConfigParams, StudentVirtualCurrency
from Instructors.models import CoursesTopics, Topics, Challenges, ChallengesTopics, Courses, ChallengesQuestions
from random import randint
from notify.signals import notify
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from celery import Celery
import json
from Instructors.views.courseInfoView import courseInformation
from Students.views.calloutsView import call_out_list

from Badges.enums import Event
from Badges.events import register_event, register_event_simple


app = Celery('Students', broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')

@app.task
def start_duel_challenge(duel_id, course_id):
    ''' This function starts a duel called automatically'''

    course = Courses.objects.get(courseID=course_id)
    duel_challenge = DuelChallenges.objects.get(duelChallengeID=duel_id, courseID=course)
    duel_challenge.hasStarted = True
    duel_challenge.save()

@app.task
def automatic_evaluator(duel_id, course_id):
        ''' This function evalutes winner(s) automatically '''

        current_course = Courses.objects.get(courseID=course_id)
        duel_challenge = DuelChallenges.objects.get(duelChallengeID=duel_id, courseID=current_course)
        
        ccparams = CourseConfigParams.objects.get(courseID = current_course)
        duel_vc_const = ccparams.vcDuel
        duel_vc_participants_const = ccparams.vcDuelParticipants

        # if duel has ended, it has already been evaluated and no further evaluation needed 
        if duel_challenge.hasEnded:
            return
        
        if not StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course) and not StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course):
            # both parties failed to submit duel on time
            
            # Notify parties
            notify.send(None, recipient=duel_challenge.challenger.user, actor=duel_challenge.challengee.user,
                                    verb= "Both you and your oppenent have failed to submit the duel, " +duel_challenge.duelChallengeName+", on time. The duel has already expired and cannot be taken.", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
            
            notify.send(None, recipient=duel_challenge.challengee.user, actor=duel_challenge.challenger.user,
                                    verb= "Both you and your oppenent have failed to submit the duel, " +duel_challenge.duelChallengeName+", on time. The duel has already expired and cannot be taken.", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
         
        elif StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course) and StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course):
            challenger_challenge = StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
            challengee_challenge = StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
       
            if challenger_challenge.testScore > challengee_challenge.testScore:
                winner_s = challenger_challenge.studentID
                vc_winner = StudentRegisteredCourses.objects.get(studentID=winner_s, courseID=current_course)
                # Winner gets the total virtual currency and an amount of virtual currency set by teacher
                virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
                vc_winner.save()
                winner = Winners()
                winner.DuelChallengeID = duel_challenge
                winner.studentID = winner_s
                winner.courseID = current_course
                winner.save()
                
                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = duel_challenge.courseID
                w_student_vc.studentID = winner_s
                w_student_vc.objectID = 0
                w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                w_student_vc.vcName = duel_challenge.duelChallengeName
                w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
                w_student_vc.save()
                
                # Notify winner
                notify.send(None, recipient=winner.studentID.user, actor=challengee_challenge.studentID.user,
                                        verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
                
                # Register event that the student has won the duel
                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': winner.studentID.user.username,
                }
                register_event_simple(Event.duelWon, mini_req, winner.studentID, objectId=duel_id)
                
                if duel_vc_participants_const > 0:
                        
                        vc_loser = StudentRegisteredCourses.objects.get(studentID=challengee_challenge.studentID, courseID=duel_challenge.courseID)
                        # participants gets an amount of virtual currency set by teacher
                        virtualCurrencyAmount = duel_vc_participants_const
                        vc_loser.virtualCurrencyAmount = virtualCurrencyAmount
                        vc_loser.save()
                
                        # save earning transaction
                        l_student_vc = StudentVirtualCurrency()
                        l_student_vc.courseID = duel_challenge.courseID
                        l_student_vc.studentID = challengee_challenge.studentID
                        l_student_vc.objectID = 0
                        l_student_vc.value = virtualCurrencyAmount
                        l_student_vc.vcName = duel_challenge.duelChallengeName
                        l_student_vc.vcDescription = "You have participated in the duel, " + duel_challenge.duelChallengeName
                        l_student_vc.save()
                # Notify student about their lost
                notify.send(None, recipient=challengee_challenge.studentID.user, actor=winner.studentID.user,
                                        verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+".", nf_type='Lost Annoucement', extra=json.dumps({"course": str(course_id)}))
                
                # Register event that the student has lost the duel
                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': challengee_challenge.studentID.user.username,
                }
                register_event_simple(Event.duelLost, mini_req, challengee_challenge.studentID, objectId=duel_id)

            elif challengee_challenge.testScore > challenger_challenge.testScore:
                winner_s = challengee_challenge.studentID
                vc_winner = StudentRegisteredCourses.objects.get(studentID=winner_s, courseID=current_course)
                # Winner gets the total virtual currency and an amount of virtual currency set by teacher
                virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
                vc_winner.save()
                winner = Winners()
                winner.DuelChallengeID = duel_challenge
                winner.studentID = winner_s
                winner.courseID = current_course
                winner.save()
                
                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = duel_challenge.courseID
                w_student_vc.studentID = winner_s
                w_student_vc.objectID = 0
                w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                w_student_vc.vcName = duel_challenge.duelChallengeName
                w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
                w_student_vc.save()

                # Notify winner
                notify.send(None, recipient=winner.studentID.user, actor=challenger_challenge.studentID.user,
                                        verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
                
                # Register event that the student has won the duel
                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': winner.studentID.user.username,
                }
                register_event_simple(Event.duelWon, mini_req, winner.studentID, objectId=duel_id)

                if duel_vc_participants_const > 0:
                        
                        vc_loser = StudentRegisteredCourses.objects.get(studentID=challenger_challenge.studentID, courseID=duel_challenge.courseID)
                        # participants gets an amount of virtual currency set by teacher
                        virtualCurrencyAmount = duel_vc_participants_const
                        vc_loser.virtualCurrencyAmount = virtualCurrencyAmount
                        vc_loser.save()
                
                        # save earning transaction
                        l_student_vc = StudentVirtualCurrency()
                        l_student_vc.courseID = duel_challenge.courseID
                        l_student_vc.studentID = challenger_challenge.studentID
                        l_student_vc.objectID = 0
                        l_student_vc.value = virtualCurrencyAmount
                        l_student_vc.vcName = duel_challenge.duelChallengeName
                        l_student_vc.vcDescription = "You have participated in the duel, " + duel_challenge.duelChallengeName
                        l_student_vc.save()
                        
                # Notify student about their lost
                notify.send(None, recipient=challenger_challenge.studentID.user, actor=winner.user,
                                        verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+".", nf_type='Lost Annoucement', extra=json.dumps({"course": str(course_id)}))

                # Register event that the student has lost the duel
                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': challenger_challenge.studentID.user.username,
                }
                register_event_simple(Event.duelLost, mini_req, challenger_challenge.studentID, objectId=duel_id)

            else:
                winner1 = challengee_challenge.studentID
                vc_winner1 = StudentRegisteredCourses.objects.get(studentID=winner1, courseID=current_course)
                virtualCurrencyAmount1 = vc_winner1.virtualCurrencyAmount + duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                vc_winner1.virtualCurrencyAmount = virtualCurrencyAmount1
                vc_winner1.save()
                
                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = duel_challenge.courseID
                w_student_vc.studentID = vc_winner1
                w_student_vc.objectID = 0
                w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                w_student_vc.vcName = duel_challenge.duelChallengeName
                w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
                w_student_vc.save()
                
                winner2 = challenger_challenge.studentID
                vc_winner2 = StudentRegisteredCourses.objects.get(studentID=winner2, courseID=current_course)
                virtualCurrencyAmount2 = vc_winner2.virtualCurrencyAmount + duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                vc_winner2.virtualCurrencyAmount = virtualCurrencyAmount2
                vc_winner2.save()
                
                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = duel_challenge.courseID
                w_student_vc.studentID = vc_winner2
                w_student_vc.objectID = 0
                w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                w_student_vc.vcName = duel_challenge.duelChallengeName
                w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
                w_student_vc.save()
                
                winner = Winners()
                winner.DuelChallengeID = duel_challenge
                winner.studentID = winner1
                winner.courseID = current_course
                winner.save()
                winner = Winners()
                winner.DuelChallengeID = duel_challenge
                winner.studentID = winner2
                winner.courseID = current_course
                winner.save()

                # Notify winners
                notify.send(None, recipient=winner1.user, actor=winner2.user,
                                        verb= "Congratulations! Both you and your opponent are winners of the duel, " +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
        
                notify.send(None, recipient=winner2.user, actor=winner1.user,
                                        verb= "Congratulations! Both you and your opponent are winners of the duel, " +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))

                # Register event that the students has won the duel
                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': winner1.user.username,
                }
                register_event_simple(Event.duelWon, mini_req, winner1, objectId=duel_id)

                mini_req = {
                    'currentCourseID': duel_challenge.courseID.pk,
                    'user': winner2.user.username,
                }
                register_event_simple(Event.duelWon, mini_req, winner2, objectId=duel_id)

        elif StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course):
            student_id = duel_challenge.challengee
            vc_winner = StudentRegisteredCourses.objects.get(studentID=student_id, courseID=current_course)
            # Winner gets the total virtual currency and an amount of virtual currency set by teacher
            virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const
            vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
            vc_winner.save()
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = student_id
            winner.courseID = current_course
            winner.save()

            notify.send(None, recipient=duel_challenge.challengee.user, actor=duel_challenge.challenger.user,
                                            verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+". \nYou are the only one who has taken the duel and the duel has just expired.", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': duel_challenge.challengee.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, duel_challenge.challengee, objectId=duel_id)

            notify.send(None, recipient=duel_challenge.challenger.user, actor=duel_challenge.challengee.user,
                                            verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+". \nYou have not submitted the duel on time and the duel has just expired.", nf_type='Lost Annoucement', extra=json.dumps({"course": str(course_id)}))
            
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': duel_challenge.challenger.user.username,
            }
            register_event_simple(Event.duelLost, mini_req, duel_challenge.challenger, objectId=duel_id)

        elif StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course):
            student_id = duel_challenge.challenger
            vc_winner = StudentRegisteredCourses.objects.get(studentID=student_id, courseID=current_course)
            # Winner gets the total virtual currency and an amount of virtual currency set by teacher
            virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const
            vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
            vc_winner.save()
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = student_id
            winner.courseID = current_course
            winner.save()

            notify.send(None, recipient=duel_challenge.challenger.user, actor=duel_challenge.challengee.user,
                                            verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+". \nYou are the only one who has taken the duel and the duel has just expired.", nf_type='Win Annoucement', extra=json.dumps({"course": str(course_id)}))
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': duel_challenge.challenger.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, duel_challenge.challenger, objectId=duel_id)

            notify.send(None, recipient=duel_challenge.challengee.user, actor=duel_challenge.challenger.user,
                                            verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+". \nYou have not submitted the duel on time and the duel has just expired.", nf_type='Lost Annoucement', extra=json.dumps({"course": str(course_id)}))
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': duel_challenge.challengee.user.username,
            }
            register_event_simple(Event.duelLost, mini_req, duel_challenge.challengee, objectId=duel_id)

        duel_challenge.hasEnded = True
        duel_challenge.save()

@login_required
def callouts_list(request):
    ''' return the list of call out challenges'''
    
    context_dict,current_course = studentInitialContextDict(request)
    student_id = context_dict['student']
    context_dict['course_id'] = current_course.courseID
    
    #Get the duel challenges for challenger
    sent_duel_challenges = DuelChallenges.objects.filter(courseID=current_course, challenger=student_id)
    sent_challenges = []
    is_editables = []
    sent_vc_bets = []
    sent_status = []
    archived_sent_challenges = []
    sent_challengee_avatars = []
    sent_challenger_avatars = []
    sent_topics = []
    sent_w_l = [] # won or lost
    for sent_chall in sent_duel_challenges:
        # if challenge has not expired
        #if not sent_chall.hasEnded:

            #get parties avatars
            s_challengee_av = StudentRegisteredCourses.objects.get(studentID=sent_chall.challengee, courseID=sent_chall.courseID)
            sent_challengee_avatars.append(s_challengee_av.avatarImage)
            s_challenger_av = StudentRegisteredCourses.objects.get(studentID=sent_chall.challenger, courseID=sent_chall.courseID)
            sent_challenger_avatars.append(s_challenger_av.avatarImage)

            sent_challenges.append(sent_chall)
            # if challenge is accepted and or started, can't edit it
            if not sent_chall.status == 2:  
                is_editables.append(True)
                sent_status.append("Pending")
            else:
                sent_status.append("Accepted")
                is_editables.append(False)    
            double_vc = sent_chall.vcBet * 2
            sent_vc_bets.append(double_vc)
            
            chall_topics = ChallengesTopics.objects.filter(challengeID=sent_chall.challengeID)
            topic_names = ""
            for chall_topic in chall_topics:
                topic_names += chall_topic.topicID.topicName + "   "
            sent_topics.append(topic_names)
            
            if sent_chall.hasEnded and not Winners.objects.filter(DuelChallengeID = sent_chall):
                sent_w_l.append("Not Submitted")
            elif Winners.objects.filter(DuelChallengeID = sent_chall, studentID = student_id):
                sent_w_l.append("Won")
            elif Winners.objects.filter(DuelChallengeID = sent_chall):
                sent_w_l.append("Lost")
            else:
                sent_w_l.append("On Going")
        #else:
            # if a challenge has already ended, put it in archav
            #archived_sent_challenges.append(sent_chall)
    context_dict["sent_duel_challenges"]  = zip(range(0,len(sent_challenges)),sent_challenges, is_editables,sent_vc_bets,sent_status, sent_challengee_avatars, sent_challenger_avatars, sent_topics, sent_w_l)
    context_dict["archived_sent_duel_challenges"]  = zip(range(0,len(sent_challenges)),archived_sent_challenges)

    #Get the duel challenges for challengee
    requested_duel_challenges = DuelChallenges.objects.filter(courseID=current_course, challengee=student_id)
    requested_challenges = []
    requested_vc_bets = []
    requested_status = []
    has_accepted = []
    archived_requested_challenges = []
    requested_challengee_avatars = []
    requested_challenger_avatars = []
    requested_topics = []
    requested_w_l = []
    
    for requested_chall in requested_duel_challenges:
        # if challenge has not expired
        #if not requested_chall.hasEnded:

            #get parties avatars
            r_challengee_av = StudentRegisteredCourses.objects.get(studentID=requested_chall.challengee, courseID=requested_chall.courseID)
            requested_challengee_avatars.append(r_challengee_av.avatarImage)
            r_challenger_av = StudentRegisteredCourses.objects.get(studentID=requested_chall.challenger, courseID=requested_chall.courseID)
            requested_challenger_avatars.append(r_challenger_av.avatarImage)

            requested_challenges.append(requested_chall)
            if not requested_chall.status == 2 :
                requested_status.append("Pending")
                has_accepted.append(False)
            else:
                has_accepted.append(True)
                requested_status.append("Accepted")
            double_vc = requested_chall.vcBet * 2
            requested_vc_bets.append(double_vc)
            
            chall_topics = ChallengesTopics.objects.filter(challengeID=requested_chall.challengeID)
            topic_names = ""
            for chall_topic in chall_topics:
                topic_names += chall_topic.topicID.topicName + "   "
            requested_topics.append(topic_names)
            
            if sent_chall.hasEnded and not Winners.objects.filter(DuelChallengeID = requested_chall):
                requested_w_l.append("Not Submitted")
            elif Winners.objects.filter(DuelChallengeID = requested_chall, studentID = student_id):
                requested_w_l.append("Won")
            elif Winners.objects.filter(DuelChallengeID = requested_chall):
                requested_w_l.append("Lost")
            else:
                requested_w_l.append("On Going")
        #else:
            #archived_requested_challenges.append(requested_chall)
    
    context_dict["requested_duel_challenges"] = zip(range(0,len(requested_challenges)),requested_challenges,requested_vc_bets,requested_status, has_accepted, requested_challengee_avatars, requested_challenger_avatars, requested_topics, requested_w_l )
    context_dict["archived_requested_duel_challenges"] = zip(range(0,len(requested_challenges)),archived_requested_challenges)
    context_dict["sent_call_outs"], context_dict["requested_call_outs"] = call_out_list(student_id, current_course)
    return render(request,'Students/CalloutListForm.html', context_dict)

def convert_time_to_int(time):
    '''convert_time_to_int converts string time format (hh:mm) into munites'''

    hh,mm = time.split(":")
    return int(hh)*60+int(mm)

def get_random_challenge(topic, difficulty, current_course, student_id, challengee):
    '''get_challenge returns a random challenge based on specified topic and difficulty'''

    if topic == "Any":
        course_topics = CoursesTopics.objects.filter(courseID=current_course) 
    else:
        topic_obj = Topics.objects.get(topicID=int(topic))
        print("topic nameeeeee", topic_obj.topicName)
        course_topics = CoursesTopics.objects.filter(courseID=current_course, topicID=topic_obj)

    challenges_list = []
    for crs_t in course_topics:
        challenges_topics = ChallengesTopics.objects.filter(topicID=crs_t.topicID)
        for chall_t in challenges_topics:
            # check if challenge has not been taken by challenger and challengee
            if not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID=challengee) and not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID=student_id):
                if not chall_t.challengeID.isGraded:
                    # check if challenge has any questions
                    if ChallengesQuestions.objects.filter(challengeID=chall_t.challengeID):
                        print("difficulty selected", difficulty)
                        if difficulty == "Any":
                            challenges_list.append(chall_t.challengeID)

                        elif difficulty == 'Unspecified' and chall_t.challengeID.challengeDifficulty=='':
                            challenges_list.append(chall_t.challengeID)
                            
                        else:
                            if chall_t.challengeID.challengeDifficulty == difficulty:
                                challenges_list.append(chall_t.challengeID)

    duel_challenges = []
    # Make sure challenges are not picked by any duel before 
    challenger_duels = DuelChallenges.objects.filter(challenger = student_id)
    challenger_duels_challs = []
    for challenger_duel in challenger_duels:
        challenger_duels_challs.append(challenger_duel.challengeID)
        
    challengee_duels = DuelChallenges.objects.filter(challengee= challengee)
    challengee_duels_challs = []
    for challengee_duel in challengee_duels:
        challenger_duels_challs.append(challengee_duel.challengeID)
        
    for chall in challenges_list:
        if not chall in challenger_duels_challs and not chall in challengee_duels_challs:
            duel_challenges.append(chall)

    print("challenges")
    print(duel_challenges)

    if duel_challenges:

        # get random number for random challenge
        rand_val = randint(0, len(duel_challenges)-1)

        # return a random challenge
        return duel_challenges[rand_val]
    else:
        return 'error'

@login_required
def duel_challenge_create(request):
    
    context_dict,current_course = studentInitialContextDict(request)
    student_id = context_dict['student']

    # get list of challengees and exclude the challenger and test students
    reg_students = StudentRegisteredCourses.objects.filter(courseID=current_course).exclude(studentID=student_id).exclude(studentID__isTestStudent=True).order_by('?')
    
    if not reg_students:
        return render(request,'Students/NoDuelForm.html', context_dict)
    avatars=[]
    challengees = []
    challengees_ids = []
    ids_avs = []
    for challengee in reg_students:
        try:
            scparam = StudentConfigParams.objects.get(studentID=challengee.studentID, courseID=current_course)
            if scparam.participateInDuel:
                challengees.append(challengee)
                challengees_ids.append(challengee.studentID.user.id)
                avatar = challengee.avatarImage #checkIfAvatarExist(challengee)
                avatars.append(avatar)
                ids_avs.append(str(challengee.studentID.user.id)+"---"+str(avatar))
        except:
            challengees.append(challengee)
            challengees_ids.append(challengee.studentID.user.id)
            avatar = challengee.avatarImage #checkIfAvatarExist(challengee)
            avatars.append(avatar)
            ids_avs.append(str(challengee.studentID.user.id)+"---"+str(avatar))
            
    if avatars:
        context_dict['first_avatar'] = avatars[0]
    context_dict['challengees_range']=zip(range(0,len(avatars)),challengees_ids,avatars, challengees, ids_avs)
    
    ccparams = CourseConfigParams.objects.get(courseID = current_course)
    duel_vc_const = ccparams.vcDuel
    duel_vc_participants_const = ccparams.vcDuelParticipants

    context_dict['max_bet'] = ccparams.vcDuelMaxBet
    
    if ccparams.betVC:
        context_dict["is_bet_vc"] = True
    else:
        context_dict["is_bet_vc"] = False

    # Get course topics
    
    #course_topics_list = []
    #course_topics = CoursesTopics.objects.filter(courseID=current_course)   
    #for ct in course_topics:
        #course_topics_list.append(ct)
    #context_dict['course_topics'] = course_topics_list
    
    course_topics_set = set()
    #course_topics_dict = {}
    difficulty_set = set()
    challenges_list = []
    chall_topics = []
    challenges_topics = ChallengesTopics.objects.filter(challengeID__courseID=current_course)
    for chall_t in challenges_topics:
            # check if challenge has not been taken by challenger and challengee
            if not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID=student_id) and not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID=reg_students[0].studentID) :
                if not chall_t.challengeID.isGraded:
                    # check if challenge has any questions
                    if ChallengesQuestions.objects.filter(challengeID=chall_t.challengeID):
                        challenges_list.append(chall_t.challengeID)
                        chall_topics.append(chall_t)
 
    challenger_duels = DuelChallenges.objects.filter(challenger = student_id)
    challenger_duels_challs = []
    for challenger_duel in challenger_duels:
        challenger_duels_challs.append(challenger_duel.challengeID)
         
    challengee_duels = DuelChallenges.objects.filter(challengee = reg_students[0].studentID)
    challengee_duels_challs = []
    for challengee_duel in challengee_duels:
        challengee_duels_challs.append(challengee_duel.challengeID)
         
    topic_ids = []
    for chall, chall_topic in zip(challenges_list, chall_topics):
        if not chall in challenger_duels_challs and not chall in challengee_duels_challs:
            difficulty_set.add(chall.challengeDifficulty)
            
            if chall_topic.topicID.topicID in topic_ids:
                continue
            else:
                topic_ids.append(chall_topic.topicID.topicID)
            course_topics_set.add(chall_topic)
#             if not chall_topic.topicID.topicName in course_topics_dict:
#                 course_topics_dict[chall_topic.topicID.topicName] = [chall_topic.topicID.topicName, {chall.challengeDifficulty}]
#             else:
#                 course_topics_dict[chall_topic.topicID.topicName][1].add(chall.challengeDifficulty)
#                 
                
    print(course_topics_set)
    if '' in difficulty_set:
        difficulty_set.remove('')
        difficulty_set.add('Unspecified')
    print(difficulty_set)
                     
    context_dict['course_topics'] = course_topics_set
    context_dict['difficulty_set'] = difficulty_set

    if request.POST:
        # If editing
        if 'duel_challengeID' in request.POST:
            duel_challenge = DuelChallenges.objects.get(pk=int(request.POST['duelChallengeID']))
        else:
            #create a new Duel Challenge
            duel_challenge = DuelChallenges()

        #print(int(request.POST['challengee_id']))
        
        id_av = request.POST['challengee_id'].split("---")
        challengee_reg_crs = StudentRegisteredCourses.objects.get(studentID__user__id=int(id_av[0]), courseID=current_course)
        challengee = challengee_reg_crs.studentID
        print("challengee")
    
        print(challengee)
        duel_challenge.challengee = challengee

        # student initiating challenge
        duel_challenge.challenger = student_id
        
        duel_chall_name = request.POST['duelChallName']
        duel_challenge.duelChallengeName = duel_chall_name
        
        duel_challenge.courseID = current_course

        time = utcDate()
        duel_challenge.sendTime = time
        custom_message = "This duel is anonymous. Both you and your are opponent are called to solve a challenge/problem(s) selected by the system based on specified topic and difficulty by sender. The duel is"


        # Get random challenge
        topic = request.POST['topic']
        difficulty = request.POST['difficulty']
        random_challenge = get_random_challenge(topic,difficulty,current_course,student_id, challengee)
        
        try:
            topic_obj = Topics.objects.get(topicID=int(topic))
            print("topic nameeeeee", topic_obj.topicName)
            topic_name = topic_obj.topicName
        except:
            topic_name = 'Any'
        
        
        custom_message +=" on "+topic_name+" (topic) and "+difficulty+" level of difficulty."
        duel_challenge.challengeID = random_challenge

        if 'startTime' in request.POST:
            # start time in hh:mm format
            #s_t_hh_mm = request.POST['startTime']

            # Convert input time into integer
            start_time = int(request.POST['startTime'])
            duel_challenge.startTime = start_time
            custom_message +=" The duel will start in "+str(start_time)+" minute(s) after acceptance, and"
        else:
            # If not given, get the default time to customize message
            custom_message +=" The duel will start in 24:00 (hh:mm) after acceptance, and"

        if 'timeLimit' in request.POST:
            # Convert input time into integer
            #t_l_hh_mm = request.POST['timeLimit']
            time_limit = int(request.POST['timeLimit'])
            duel_challenge.timeLimit = time_limit
            custom_message +=" will last for "+str(time_limit)+" minute(s)."
        else:
            # If not given, get the default time to customize message
            custom_message +=" will last for 01:00 (hh:mm)."
        
        # chech if betting is true
        if 'isBetting' in request.POST:
            duel_challenge.isBetting = True
            print('is betting is true')
             # Set the amount of VC
            if 'vcBetting' in request.POST:
                vc_bet = abs(int(request.POST['vcBetting']))
                double_vc = 2*vc_bet
                duel_challenge.vcBet = vc_bet
                custom_message += " This Challenge is a bet that rewards the winner an amount of Virtual Currency of " +str(double_vc) 
                if duel_vc_const > 0:
                    custom_message +=" plus "+str(duel_vc_const) +" (winner's award)"
                if duel_vc_participants_const > 0:
                    custom_message += " and " + str(duel_vc_participants_const) + " (participation's award)"
                if duel_vc_const or duel_vc_participants_const:
                    custom_message += " Virtual Currency provided by Instructor"
                custom_message += ". Upon acceptance, you are agreeing an amount of Virtual Currency of "+str(vc_bet)+" will be withdrawn from your account and put at stake."
            
                # Take the amount of vc from challenger's account
                challenger_reg_crs = StudentRegisteredCourses.objects.get(studentID=student_id, courseID=current_course)
                challenger_reg_crs.virtualCurrencyAmount -= vc_bet
                challenger_reg_crs.save()

        else:
            duel_challenge.isBetting = False

        custom_message += " To win the challenge, you must solve the problem(s) the same as or better than your opponent."
        custom_message += " In case of a tie, you and your opponent are both considered winners and your Virtual Currency will be reimbursed if applicable. If you fail to submit this duel on time, you will lose."
        print(custom_message)
 
        print("random challenge")
        print(random_challenge)

        duel_challenge.customMessage = custom_message
        
        duel_name = duel_challenge.duelChallengeName
        
        duel_challenge.save()

        print("duel challenge")
        print(duel_challenge)

        notify.send(None, recipient=challengee.user, actor=student_id.user,
                                    verb= 'Someone sent you a duel request named '+duel_name, nf_type='Duel Request', extra=json.dumps({"course": str(current_course.courseID)}))
        
        mini_req = {
            'currentCourseID': current_course.pk,
            'user': student_id.user.username,
        }
        register_event_simple(Event.duelSent, mini_req, student_id, objectId=duel_challenge.duelChallengeID)

        return redirect('/oneUp/students/Callouts')
    #elif request.GET:
    return render(request,'Students/DuelChallengeCreateForm.html', context_dict)

@login_required
def get_create_duel_topics_difficulties(request):
    from django.http import JsonResponse

    c_d,current_course = studentInitialContextDict(request)
    student_id = c_d['student']
    context_dict = {}

    challengee_id = request.GET['challengee']
    course_topics_set = set()
    difficulty_set = set()

    challenges_list = []
    chall_topics = []

    if 'topic_id' in request.GET:
        topic = request.GET['topic_id']
        if topic == "Any":
            course_topics = CoursesTopics.objects.filter(courseID=current_course) 
        else:
            topic_obj = Topics.objects.get(topicID=int(topic))
            print("topic nameeeeee", topic_obj.topicName)
            course_topics = CoursesTopics.objects.filter(courseID=current_course, topicID=topic_obj)
    else:
        course_topics = CoursesTopics.objects.filter(courseID=current_course)

    challenges_list = []
    for crs_t in course_topics:
        challenges_topics = ChallengesTopics.objects.filter(topicID=crs_t.topicID)

    if 'topicID' in request.GET:
        topic = request.GET['topicID']

        if topic == "Any":
            challenges_topics = ChallengesTopics.objects.filter(challengeID__courseID=current_course)
        else:
            challenges_topics = ChallengesTopics.objects.filter(challengeID__courseID=current_course, topicID=int(topic))
    else:
        challenges_topics = ChallengesTopics.objects.filter(challengeID__courseID=current_course)
       

    for chall_t in challenges_topics:
            # check if challenge has not been taken by challenger and challengee
            if not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID=student_id) and not StudentChallenges.objects.filter(challengeID=chall_t.challengeID, studentID__user__id=challengee_id) :
                if not chall_t.challengeID.isGraded:
                    # check if challenge has any questions
                    if ChallengesQuestions.objects.filter(challengeID=chall_t.challengeID):
                        challenges_list.append(chall_t.challengeID)
                        chall_topics.append(chall_t)
 

    challenger_duels = DuelChallenges.objects.filter(challenger = student_id)
    challenger_duels_challs = []
    for challenger_duel in challenger_duels:
        challenger_duels_challs.append(challenger_duel.challengeID)
         
    challengee_duels = DuelChallenges.objects.filter(challengee__user__id=challengee_id)
    challengee_duels_challs = []
    for challengee_duel in challengee_duels:
        challengee_duels_challs.append(challengee_duel.challengeID)
         
    topic_ids = []
    i=0
    for chall, chall_topic in zip(challenges_list, chall_topics):
        if not chall in challenger_duels_challs and not chall in challengee_duels_challs:
            
            difficulty_set.add(chall.challengeDifficulty)
            
            if chall_topic.topicID.topicID in topic_ids:
                continue
            else:
                topic_ids.append(chall_topic.topicID.topicID)
            course_topics_set.add(str(chall_topic.topicID.topicID)+"---"+chall_topic.topicID.topicName)

    if '' in difficulty_set:
        difficulty_set.remove('')
        difficulty_set.add('Unspecified')

    print(course_topics_set)
                     
    context_dict['course_topics'] = list(course_topics_set)
    context_dict['difficulty_set'] = list(difficulty_set)

    print(context_dict)
    return JsonResponse(context_dict)

@login_required
def validate_duel_challenge_creation(request):
    from django.http import JsonResponse
    from Badges.models import CourseConfigParams

    c_d,current_course = studentInitialContextDict(request)
    student_id = c_d['student']

    context_dict = {}
    if request.POST:
    
        random_chall_error = []
        max_vc_error = []
        challengee_vc_error = []
        challenger_vc_error = []
        
        id_av = request.POST['challengee_id'].split("---")
        challengee_reg_crs = StudentRegisteredCourses.objects.get(studentID__user__id=int(id_av[0]), courseID=current_course)
        challengee = challengee_reg_crs.studentID

        # check if we got a random chall or an error message
        topic = request.POST['topic']
        difficulty = request.POST['difficulty']
        random_challenge = get_random_challenge(topic,difficulty,current_course,student_id, challengee)
        try:
            if random_challenge == 'error':
                random_chall_error.append("There is no challenge/problem for specified topic and difficulty. Tip: Don't narrow too much.")
                
        except:
            random_chall = "success"
                 
        # check if students have enough vc to bet
        if 'isBetting' in request.POST:
            if request.POST['vcBetting']:
                vc_bet = int(request.POST['vcBetting'])
                
                ccparams = CourseConfigParams.objects.get(courseID = current_course)
                if ccparams.vcDuelMaxBet < vc_bet:
                    max_vc_error.append("Maximum virtual currency you are allowed to bet is "+ str(ccparams.vcDuelMaxBet))
 
                challengee_reg_crs = StudentRegisteredCourses.objects.get(studentID=challengee, courseID=current_course)
    
                if challengee_reg_crs.virtualCurrencyAmount < vc_bet:
                    challengee_vc_error.append('Your opponent does not have sufficient virtual currency to bet. Tip: Bet less or uncheck betting.')
                     
                        
                challenger_reg_crs = StudentRegisteredCourses.objects.get(studentID=student_id, courseID=current_course)
                challenger_vc = challenger_reg_crs.virtualCurrencyAmount
                
                if challenger_vc < vc_bet:
                    challenger_vc_error.append('You do not have sufficient virtual currency to bet. Your virtual currency is ' + str(challenger_vc) + '.')
        
        context_dict['random_chall_error'] = random_chall_error 
        context_dict['challengee_vc_error'] = challengee_vc_error
        context_dict['challenger_vc_error'] = challenger_vc_error           
        context_dict['max_vc_error'] = max_vc_error
        
        print(context_dict)
        return JsonResponse(context_dict)
    
    return redirect('/oneUp/students/Callouts') 

@login_required
def duel_challenge_description(request):
    ''' Challenge description '''

    context_dict,current_course = studentInitialContextDict(request)
    student_id = context_dict['student']
    context_dict['course_id'] = current_course.courseID
    
    ccparams = CourseConfigParams.objects.get(courseID = current_course)
    duel_vc_const = ccparams.vcDuel
    duel_vc_participants_const = ccparams.vcDuelParticipants

    if 'duelChallengeID' in request.GET:
        try:
            duel_challenge = DuelChallenges.objects.get(pk=int(request.GET['duelChallengeID']))
        except:
            return redirect('/oneUp/students/Callouts') 
        
        context_dict['timeLimit'] = duel_challenge.timeLimit
        
        context_dict['award'] = duel_vc_const + 2 * duel_challenge.vcBet + duel_vc_participants_const
        
        if 'sTime' in request.GET:
            context_dict['startTime'] = 0
            print("sTime tart time ", 0)
        elif duel_challenge.hasStarted or duel_challenge.status == 1:
            context_dict['startTime'] = 0
    
            if duel_challenge.hasStarted:
                total_time = duel_challenge.acceptTime +timedelta(minutes=duel_challenge.startTime) +timedelta(minutes=duel_challenge.timeLimit)+timedelta(seconds=20)
                remaing_time = total_time-utcDate()
                difference_minutes = remaing_time.total_seconds()/60.0
                context_dict['testDuration'] = difference_minutes
        else:
            start_accept_time = duel_challenge.acceptTime +timedelta(minutes=duel_challenge.startTime)+timedelta(seconds=20)
            difference =  start_accept_time - utcDate()
            difference_minutes = difference.total_seconds()/60.0
        
            context_dict['startTime'] = difference_minutes

        def results(duel_challenge, student_id):
            message = ''
            winners = Winners.objects.filter(DuelChallengeID=duel_challenge)
            
            if len(winners) == 0:
                message +="Both you and opponent have failed to submit duel on time. Duel has already expired and cannot be taken."
                if duel_challenge.isBetting:
                    message +=" You and opponent are reimbursed an amount of "+str(duel_challenge.vcBet)+" virtual currency each."
            elif len(winners)==2:
                message +="You and opponent are both winners of this duel."
                if duel_challenge.isBetting:
                    message +=" You and opponent are reimbursed an amount of "+str(duel_challenge.vcBet)
                    if duel_vc_const > 0:
                        message +=" plus "+str(duel_vc_const) 
                    if duel_vc_participants_const > 0: 
                        message +=", and "+str(duel_vc_participants_const)
                    message +=" virtual currency each."
            else:
                winner = winners[0]
                amount = duel_challenge.vcBet*2
                if winner.studentID == student_id:
                    message += "You are the winner of this duel."
                    if duel_challenge.isBetting:
                        message += " You have been rewarded an amount of "+str(amount)
                        if duel_vc_const > 0:
                            message +=" plus "+str(duel_vc_const) + " (given by instructor)"
                        if duel_vc_participants_const > 0: 
                            message +=", and "+str(duel_vc_participants_const) + " (participation award)"
                        message +=" virtual currency."
                   
                    message +="\nCongratulations!"
                else:
                    #message += winner.studentID.user.first_name+" "+winner.studentID.user.last_name+ " is the winner of this duel. "
                    message += "You have lost this duel."
                    if duel_vc_participants_const > 0: 
                        message += " You have been rewarded an amount of " +str(duel_vc_participants_const) + " virtual currency for having participated in this duel."
                        
                    if duel_challenge.isBetting:
                        message += " Your opponent has been rewarded an amount of "+str(amount)
                        if duel_vc_const > 0:
                            message +=" plus "+str(duel_vc_const) + " (given by instructor)"
                        if duel_vc_participants_const > 0: 
                            message +=", and "+str(duel_vc_participants_const) + " (participation award)"
                        message +=" virtual currency."
                    message += "\nThank you for your participation!"
                   
            return message

        if duel_challenge.challenger == student_id:
            context_dict['vc_bet_dobule'] = 2*duel_challenge.vcBet
            context_dict['sent_duel_challenge']=duel_challenge
            context_dict["duel_vc_const"] = duel_vc_const
            context_dict["duel_vc_participants_const"] = duel_vc_participants_const
            #context_dict['time_limit'] = convert_time_to_hh_mm(duel_challenge.timeLimit)

            #if not duel_challenge.hasStarted:
                #context_dict['start_time'] = convert_time_to_hh_mm(duel_challenge.startTime)

            #get avatars
            opponent_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challengee, courseID=duel_challenge.courseID)
            context_dict['opponent_avatar'] = opponent_av.avatarImage
            your_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
            context_dict['your_avatar'] = your_av.avatarImage

            if duel_challenge.status == 1:
                context_dict['acceptance_status'] = 'pending'
                context_dict['isAccepted'] = False
            elif duel_challenge.status == 2:
                context_dict['acceptance_status'] = 'Accepted'
                context_dict['isAccepted'] = True
            if duel_challenge.hasEnded:
                if not Winners.objects.filter(DuelChallengeID=duel_challenge):
                    context_dict['hasExpired'] = True
                context_dict['hasEnded'] = True
                context_dict['message'] = results(duel_challenge, student_id)
               
            # duel challengeID is a warmup challenge
            context_dict['isWarmup'] = True

            # Check if challenge is already taken by student 
            if StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course):
                context_dict['isTaken'] = True
                context_dict['sChall'] = StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
            else:
                context_dict['isTaken'] = False

            return render(request,'Students/SentDuelChallengeDescriptionForm.html', context_dict)
       
        elif duel_challenge.challengee == student_id:
            context_dict['vc_bet_dobule'] = 2*duel_challenge.vcBet
            context_dict['requested_duel_challenge']=duel_challenge
            context_dict["duel_vc_const"] = duel_vc_const
            context_dict["duel_vc_participants_const"] = duel_vc_participants_const
            #context_dict['time_limit'] = convert_time_to_hh_mm(duel_challenge.timeLimit)

            #if not duel_challenge.hasStarted:
                #context_dict['start_time'] = convert_time_to_hh_mm(duel_challenge.startTime)
            
            #get opponent avatar
            opponent_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
            context_dict['opponent_avatar'] = opponent_av.avatarImage
            your_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challengee, courseID=duel_challenge.courseID)
            context_dict['your_avatar'] = your_av.avatarImage


            if duel_challenge.status == 1:
                context_dict['acceptance_status'] = 'pending'
                context_dict['isAccepted'] = False
            elif duel_challenge.status == 2:
                context_dict['acceptance_status'] = 'Accepted'
                context_dict['isAccepted'] = True
            if duel_challenge.hasEnded:
                context_dict['hasEnded'] = True
                context_dict['message'] = results(duel_challenge, student_id)

            # duel challengeID is a warmup challenge
            context_dict['isWarmup'] = True

            # Check if challenge is already taken by student
            if StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course):
                context_dict['isTaken'] = True
                context_dict['sChall'] = StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
            else:
                context_dict['isTaken'] = False

            #if 'accept' in request.GET:
                # duel_challenge.hasStarted = True
                 #duel_challenge.save()

            return render(request,'Students/RequestedDuelChallengeDescriptionForm.html', context_dict)

    return redirect('/oneUp/students/Callouts')

@login_required
def duel_challenge_accept(request):
    ''' duel_challenge_accept saves duel request acceptance '''

    if 'duelChallengeID' in request.GET:
        context_dict = {}
        duel_challenge = DuelChallenges.objects.get(pk=int(request.GET['duelChallengeID']))
        course_id = duel_challenge.courseID.courseID
        # Take the amount of vc from challengee's account
        challengee = duel_challenge.challengee
        challengee_reg_crs = StudentRegisteredCourses.objects.get(studentID=challengee, courseID=duel_challenge.courseID)
        # Check if vc amount can be taken from challengee's account
        if duel_challenge.isBetting:
            if challengee_reg_crs.virtualCurrencyAmount < duel_challenge.vcBet:
                context_dict['name'] = duel_challenge.duelChallengeName
                context_dict['message'] = 'Your amount of virtual currency is insufficient. Duel can not be taken and will be deleted'
                context_dict['your_vc'] = challengee_reg_crs.virtualCurrencyAmount
                context_dict['duel_vc'] = duel_challenge.vcBet

                challenger_reg_crs = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
                challenger_vc = challenger_reg_crs.virtualCurrencyAmount
                challenger_reg_crs.virtualCurrencyAmount = challenger_vc + duel_challenge.vcBet
                duel_challenge.delete()
                
                notify.send(None, recipient=duel_challenge.challenger.user, actor=challengee.user,
                                        verb= "Your opponent does not have enough virtual currency to take the duel " + duel_challenge.duelChallengeName +' at this moment.\n The duel has been deleted and you are reimbursed an amount of '+str(duel_challenge.vcBet)+' virtual currency.', nf_type='Insufficient Virtual Currency', extra=json.dumps({"course": str(course_id)}))
                
                return  render(request,'Students/DuelChallengeInsufficientVCForm.html', context_dict)
        
            # if student has sufficient amount of vc then take it and put at stake 
            challengee_vc = challengee_reg_crs.virtualCurrencyAmount
            challengee_reg_crs.virtualCurrencyAmount = challengee_vc-duel_challenge.vcBet
            challengee_reg_crs.save()

        # toggle status to accpeted
        duel_challenge.status = 2 
        #duel_challenge.hasStarted = True
        duel_challenge.acceptTime = utcDate()
        duel_challenge.save()
        context_dict['requested_duel_challenge']=duel_challenge
        #context_dict['time_limit'] = convert_time_to_hh_mm(duel_challenge.timeLimit)
        #context_dict['start_time'] = convert_time_to_hh_mm(duel_challenge.startTime)
        context_dict['acceptance_status'] = 'Accepted'
        context_dict['isAccepted'] = True
        context_dict['startTime'] = duel_challenge.startTime
        #get opponent avatar
        opponent_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
        context_dict['opponent_avatar'] = opponent_av.avatarImage
        your_av = StudentRegisteredCourses.objects.get(studentID=duel_challenge.challengee, courseID=duel_challenge.courseID)
        context_dict['your_avatar'] = your_av.avatarImage

        ccparams = CourseConfigParams.objects.get(courseID = duel_challenge.courseID)
        duel_vc_const = ccparams.vcDuel
        duel_vc_participants_const = ccparams.vcDuelParticipants
        context_dict["duel_vc_const"] = duel_vc_const
        context_dict["duel_vc_participants_const"] = duel_vc_participants_const
        
        ################################################################################################################################################
        # Start duel after specified time using celery 
        # get database start time and subtract 20 seconds from it to be consistent with network latency 
        start_time = utcDate() +timedelta(minutes=duel_challenge.startTime)-timedelta(seconds=20)
        print("start time ", start_time)
        start_duel_challenge.apply_async((duel_challenge.duelChallengeID, duel_challenge.courseID.courseID), eta=start_time)
        print("start duel celery")
        ##################################################################################################################################################

        ##################################################################################################################################################
        # Automatically evaluate duel after specified time using Celery 
        # get database start time and add a munite to it to be consistent with network latency 
        evaluation_time = utcDate() +timedelta(minutes=duel_challenge.startTime)+timedelta(minutes=duel_challenge.timeLimit)+timedelta(minutes=1)
        print("evaluation time ", evaluation_time )
        automatic_evaluator.apply_async((duel_challenge.duelChallengeID, duel_challenge.courseID.courseID), eta=evaluation_time)
        print("automatic evaluation duel celery")
        ##################################################################################################################################################

        # Notify challenger that the challengee has accepted the request
        notify.send(None, recipient=duel_challenge.challenger.user, actor=challengee.user,
                                    verb= "Your opponent has accepted the duel, " + duel_challenge.duelChallengeName +", request. The duel will start in "+str(duel_challenge.startTime)+" minutes." , nf_type='Request Acceptance', extra=json.dumps({"course": str(course_id)}))           

        mini_req = {
            'currentCourseID': duel_challenge.courseID.pk,
            'user': challengee.user.username,
        }
        register_event_simple(Event.duelSent, mini_req, challengee, objectId=duel_challenge.duelChallengeID)

        return render(request,'Students/RequestedDuelChallengeDescriptionForm.html', context_dict)

    return redirect('/oneUp/students/Callouts')

@login_required
def duel_challenge_delete(request):
    ''' Delete a declined and deleted duel'''

    if 'duelChallengeID' in request.GET:
        duel_challenge = DuelChallenges.objects.get(pk=int(request.GET['duelChallengeID']))
        course_id = duel_challenge.courseID.courseID
        challenger = duel_challenge.challenger
        challengee = duel_challenge.challengee

        # if duel has betting, reimburse parties' virtual currency
        if duel_challenge.isBetting:
            challenger_reg_crs = StudentRegisteredCourses.objects.get(studentID=challenger, courseID=duel_challenge.courseID)
            challenger_vc = challenger_reg_crs.virtualCurrencyAmount
            challenger_reg_crs.virtualCurrencyAmount = challenger_vc + duel_challenge.vcBet
            challenger_reg_crs.save()
            
            # if duel has been accepted, reimburse challengee's vc 
            if duel_challenge.status == 2:
                challengee_reg_crs = StudentRegisteredCourses.objects.get(studentID=challengee, courseID=duel_challenge.courseID)
                challengee_vc = challengee_reg_crs.virtualCurrencyAmount
                challengee_reg_crs.virtualCurrencyAmount = challengee_vc + duel_challenge.vcBet
                challengee_reg_crs.save()
        
        # if request denied, notify challenger
        if 'denial' in request.GET:
            notify.send(None, recipient=challenger.user, actor=challengee.user,
                                    verb= "Your opponent has declined your duel," + duel_challenge.duelChallengeName +", request. You are reimbursed an amount of "+str(duel_challenge.vcBet)+" virtual currency." , nf_type='Request denial', extra=json.dumps({"course": str(course_id)}))           
        else:
            notify.send(None, recipient=challengee.user, actor=challenger.user,
                                    verb= 'The duel, ' + duel_challenge.duelChallengeName +", request has been canceled by opponent." , nf_type='Request Delete', extra=json.dumps({"course": str(course_id)}))           

        duel_challenge.delete()
        
    return redirect('/oneUp/students/Callouts')

def duel_challenge_evaluate(student_id, current_course, duel_challenge,context_dict):
    '''duel_challenge_evaluate evalutes and determines the winners, and handles virtual current transaction if betting is enable'''
   
    def has_duel_expired(student_id, duel_challenge, context_dict, duel_vc_const, duel_vc_participants_const):
            ''' Check whether duel has expired and if has expired, then reward student who submitted duel on time'''

            # get start and limit time from database 
            start_and_limit_time = duel_challenge.startTime + duel_challenge.timeLimit
            
            # get utc time now and add 15 seconds for network latency and items in queue that may make a delay
            date_now = utcDate() + timedelta(seconds=15) 

            # get the time when duel was accpeted and add start_and_limit_time to time
            duel_allowed_time = duel_challenge.acceptTime+timedelta(minutes=start_and_limit_time) 
            
            if duel_allowed_time < date_now:
                
                # Challenge is expired
                context_dict['isExpired']=True

                vc_winner = StudentRegisteredCourses.objects.get(studentID=student_id, courseID=duel_challenge.courseID)
                # Winner gets the total virtual currency and an amount of virtual currency set by teacher
                virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
                vc_winner.save()
                winner = Winners()
                winner.DuelChallengeID = duel_challenge
                winner.studentID = student_id
                winner.courseID = current_course
                winner.save()
                
                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = duel_challenge.courseID
                w_student_vc.studentID = student_id
                w_student_vc.objectID = 0
                w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
                w_student_vc.vcName = duel_challenge.duelChallengeName
                w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
                w_student_vc.save()

                if duel_challenge.challenger == student_id:
                    notify.send(None, recipient=duel_challenge.challenger.user, actor=duel_challenge.challengee.user,
                                            verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+". \nYou are the only one who has taken the duel and the duel has just expired.", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
                    # Register event that the student has won the duel
                    mini_req = {
                        'currentCourseID': duel_challenge.courseID.pk,
                        'user': duel_challenge.challenger.user.username,
                    }
                    register_event_simple(Event.duelWon, mini_req, duel_challenge.challenger, objectId=duel_challenge.duelChallengeID)

                    notify.send(None, recipient=duel_challenge.challengee.user, actor=duel_challenge.challenger.user,
                                            verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+". \nYou have not submitted the duel on time and the duel has just expired.", nf_type='Lost Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
                    # Register event that the student has lost the duel
                    mini_req = {
                        'currentCourseID': duel_challenge.courseID.pk,
                        'user': duel_challenge.challengee.user.username,
                    }
                    register_event_simple(Event.duelLost, mini_req, duel_challenge.challengee, objectId=duel_challenge.duelChallengeID)

                else: 
                        
                    notify.send(None, recipient=duel_challenge.challengee.user, actor=duel_challenge.challenger.user,
                                            verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+". \nYou are the only one who has taken the duel and the duel has just expired.", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
                    mini_req = {
                        'currentCourseID': duel_challenge.courseID.pk,
                        'user': duel_challenge.challengee.user.username,
                    }
                    register_event_simple(Event.duelWon, mini_req, duel_challenge.challengee, objectId=duel_challenge.duelChallengeID)

                    notify.send(None, recipient=duel_challenge.challenger.user, actor=duel_challenge.challengee.user,
                                            verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+". \nYou have not submitted the duel on time and the duel has just expired.", nf_type='Lost Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
                    mini_req = {
                        'currentCourseID': duel_challenge.courseID.pk,
                        'user': duel_challenge.challenger.user.username,
                    }
                    register_event_simple(Event.duelLost, mini_req, duel_challenge.challenger, objectId=duel_challenge.duelChallengeID)


                duel_challenge.hasEnded = True
                duel_challenge.save()
                
                context_dict['areAllDone'] = True
                return context_dict

            context_dict['areAllDone'] = False
            return context_dict
                
    def evaluator(challenger_challenge, challengee_challenge, duel_challenge, current_course, duel_vc_const, duel_vc_participants_const):

        if challenger_challenge.testScore > challengee_challenge.testScore:
            winner_s = challenger_challenge.studentID
            vc_winner = StudentRegisteredCourses.objects.get(studentID=winner_s , courseID=current_course)
            # Winner gets the total virtual currency and an amount of virtual currency set by teacher
            virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
            vc_winner.save()
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = winner_s
            winner.courseID = current_course
            winner.save()
            # save earning transaction
            w_student_vc = StudentVirtualCurrency()
            w_student_vc.courseID = duel_challenge.courseID
            w_student_vc.studentID = winner_s
            w_student_vc.objectID = 0
            w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            w_student_vc.vcName = duel_challenge.duelChallengeName
            w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
            w_student_vc.save()
            
            # Notify winner
            notify.send(None, recipient=winner.studentID.user, actor=challengee_challenge.studentID.user,
                                    verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
            
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': winner.studentID.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, winner.studentID, objectId=duel_challenge.duelChallengeID)

            if duel_vc_participants_const > 0:
                        
                        vc_loser = StudentRegisteredCourses.objects.get(studentID=challengee_challenge.studentID, courseID=duel_challenge.courseID)
                        # participants gets an amount of virtual currency set by teacher
                        virtualCurrencyAmount = duel_vc_participants_const
                        vc_loser.virtualCurrencyAmount = virtualCurrencyAmount
                        vc_loser.save()
                
                        # save earning transaction
                        l_student_vc = StudentVirtualCurrency()
                        l_student_vc.courseID = duel_challenge.courseID
                        l_student_vc.studentID = challengee_challenge.studentID
                        l_student_vc.objectID = 0
                        l_student_vc.value = virtualCurrencyAmount
                        l_student_vc.vcName = duel_challenge.duelChallengeName
                        l_student_vc.vcDescription = "You have participated in the duel, " + duel_challenge.duelChallengeName
                        l_student_vc.save()
            # Notify student about their lost
            notify.send(None, recipient=challengee_challenge.studentID.user, actor=winner.studentID.user,
                                    verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+".", nf_type='Lost Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))

            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': challengee_challenge.studentID.user.username,
            }
            register_event_simple(Event.duelLost, mini_req, challengee_challenge.studentID, objectId=duel_challenge.duelChallengeID)

        elif challengee_challenge.testScore > challenger_challenge.testScore:
            winner_s = challengee_challenge.studentID
            vc_winner = StudentRegisteredCourses.objects.get(studentID=winner_s, courseID=current_course)
            # Winner gets the total virtual currency and an amount of virtual currency set by teacher
            virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
            vc_winner.save()
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = winner_s
            winner.courseID = current_course
            winner.save()
            
            # save earning transaction
            w_student_vc = StudentVirtualCurrency()
            w_student_vc.courseID = duel_challenge.courseID
            w_student_vc.studentID = winner_s
            w_student_vc.objectID = 0
            w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            w_student_vc.vcName = duel_challenge.duelChallengeName
            w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
            w_student_vc.save()

            # Notify winner
            notify.send(None, recipient=winner_s.user, actor=challenger_challenge.studentID.user,
                                    verb= 'Congratulations! You have won the duel ' +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))
            
            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': winner_s.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, winner_s, objectId=duel_challenge.duelChallengeID)

            if duel_vc_participants_const > 0:
                        
                        vc_loser = StudentRegisteredCourses.objects.get(studentID=challenger_challenge.studentID, courseID=duel_challenge.courseID)
                        # participants gets an amount of virtual currency set by teacher
                        virtualCurrencyAmount = duel_vc_participants_const
                        vc_loser.virtualCurrencyAmount = virtualCurrencyAmount
                        vc_loser.save()
                
                        # save earning transaction
                        l_student_vc = StudentVirtualCurrency()
                        l_student_vc.courseID = duel_challenge.courseID
                        l_student_vc.studentID = challenger_challenge.studentID
                        l_student_vc.objectID = 0
                        l_student_vc.value = virtualCurrencyAmount
                        l_student_vc.vcName = duel_challenge.duelChallengeName
                        l_student_vc.vcDescription = "You have participated in the duel, " + duel_challenge.duelChallengeName
                        l_student_vc.save()
                        
            # Notify student about their lost
            notify.send(None, recipient=challenger_challenge.studentID.user, actor=winner_s.user,
                                    verb= 'You have lost the duel ' +duel_challenge.duelChallengeName+".", nf_type='Lost Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))

            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': challenger_challenge.studentID.user.username,
            }
            register_event_simple(Event.duelLost, mini_req, challenger_challenge.studentID, objectId=duel_challenge.duelChallengeID)

        else:
            winner1 = challengee_challenge.studentID
            vc_winner1 = StudentRegisteredCourses.objects.get(studentID=winner1, courseID=current_course)
            virtualCurrencyAmount1 = vc_winner1.virtualCurrencyAmount + duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            vc_winner1.virtualCurrencyAmount = virtualCurrencyAmount1
            vc_winner1.save()
            
            # save earning transaction
            w_student_vc = StudentVirtualCurrency()
            w_student_vc.courseID = duel_challenge.courseID
            w_student_vc.studentID = winner1
            w_student_vc.objectID = 0
            w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            w_student_vc.vcName = duel_challenge.duelChallengeName
            w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
            w_student_vc.save()
            
            winner2 = challenger_challenge.studentID
            vc_winner2 = StudentRegisteredCourses.objects.get(studentID=winner2, courseID=current_course)
            virtualCurrencyAmount2 = vc_winner2.virtualCurrencyAmount + duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            vc_winner2.virtualCurrencyAmount = virtualCurrencyAmount2
            vc_winner2.save()
            
            # save earning transaction
            w_student_vc = StudentVirtualCurrency()
            w_student_vc.courseID = duel_challenge.courseID
            w_student_vc.studentID = winner2
            w_student_vc.objectID = 0
            w_student_vc.value = 2*duel_challenge.vcBet + duel_vc_const + duel_vc_participants_const
            w_student_vc.vcName = duel_challenge.duelChallengeName
            w_student_vc.vcDescription = "You have won the duel, "+duel_challenge.duelChallengeName+". Total amount might include particpation's awards"
            w_student_vc.save()
            
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = winner1
            winner.courseID = current_course
            winner.save()
            winner = Winners()
            winner.DuelChallengeID = duel_challenge
            winner.studentID = winner2
            winner.courseID = current_course
            winner.save()

            # Notify winners
            notify.send(None, recipient=winner1.user, actor=winner2.user,
                                        verb= "Congratulations! Both you and your opponent are winners of the duel, " +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))

            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': winner1.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, winner1, objectId=duel_challenge.duelChallengeID)

            notify.send(None, recipient=winner2.user, actor=winner1.user,
                                        verb= "Congratulations! Both you and your opponent are winners of the duel, " +duel_challenge.duelChallengeName+".", nf_type='Win Annoucement', extra=json.dumps({"course": str(current_course.courseID)}))

            mini_req = {
                'currentCourseID': duel_challenge.courseID.pk,
                'user': winner2.user.username,
            }
            register_event_simple(Event.duelWon, mini_req, winner2, objectId=duel_challenge.duelChallengeID)

        duel_challenge.hasEnded = True
        duel_challenge.save()
    
    ccparams = CourseConfigParams.objects.get(courseID = current_course)
    duel_vc_const = ccparams.vcDuel
    duel_vc_participants_const = ccparams.vcDuelParticipants

    if duel_challenge.challenger == student_id:
        challenger_challenge = StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
        # if challengee has no challenge object, duel may have not submitted the duel yet
        if not StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course):
            
            #################################################################
            # check whether duel is expired 
            return has_duel_expired(student_id, duel_challenge, context_dict, duel_vc_const, duel_vc_participants_const)
            #################################################################

        challengee_challenge = StudentChallenges.objects.filter(studentID=duel_challenge.challengee,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp') 
        evaluator(challenger_challenge, challengee_challenge, duel_challenge, current_course, duel_vc_const,duel_vc_participants_const)
        context_dict['areAllDone'] = True
        return context_dict
    
    elif duel_challenge.challengee == student_id:
        challengee_challenge = StudentChallenges.objects.filter(studentID=student_id,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
        
        # if challenger has no challenge object, duel may have not submitted the duel yet
        if not StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course):
            
            #################################################################
            # check whether duel is expired 
            return has_duel_expired(student_id, duel_challenge, context_dict, duel_vc_const, duel_vc_participants_const)
            #################################################################

        challenger_challenge = StudentChallenges.objects.filter(studentID=duel_challenge.challenger,challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
        evaluator(challenger_challenge, challengee_challenge, duel_challenge, current_course, duel_vc_const, duel_vc_participants_const)
        context_dict['areAllDone'] = True
        return context_dict

    else:
        #context_dict['error']= "Some error has occurred!"
        context_dict['error'] = True
        return context_dict

    
            

        
    
     
    

        
