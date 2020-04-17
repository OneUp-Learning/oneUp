'''
Created on Apr 9, 2014
Updated 02/28/2015

@author: dichevad, irwink
'''

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect

from Students.models import Student, StudentRegisteredCourses, StudentConfigParams
from Instructors.models import Questions, Courses, Challenges, Skills, ChallengesQuestions, Topics, CoursesSubTopics, Announcements, Activities, Milestones, FlashCardGroup
from Badges.models import VirtualCurrencyCustomRuleInfo
from Instructors.constants import unassigned_problems_challenge_name
from Instructors.models import (Activities, Announcements, Challenges,
                                ChallengesQuestions, Courses, Questions,
                                Skills, Topics)
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck
from Students.models import (Student, StudentConfigParams,
                             StudentRegisteredCourses)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteQuestion(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:

        try:
            if request.POST['questionId']:
                question = Questions.objects.get(
                    pk=int(request.POST['questionId']))
                message = "Question #" + \
                    str(question.questionID) + " " + \
                    question.preview+" successfully deleted"
                question.delete()
        except Questions.DoesNotExist:
            message = "There was a problem deleting Question #" + \
                str(question.questionID) + " "+question.preview

        context_dict['message'] = message

    return redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteQuestionFromChallenge(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:

        # Delete only the record in the ChallengesQuestions(models.Model)
        try:
            if request.POST['questionId']:
                challenge_question = ChallengesQuestions.objects.filter(
                    challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for cq in challenge_question:
                    points = cq.points
                    position = cq.questionPosition
                question = Questions.objects.get(
                    pk=int(request.POST['questionId']))
                message = "Question #" + \
                    str(question.questionID) + " "+question.preview + \
                    " successfully deleted from Challenge "

                # Once a question is deleted, the positions of the rest of question after it are shift one position one
                chall_questions = ChallengesQuestions.objects.filter(
                    challengeID=request.POST['challengeID'])
                for chall_question in chall_questions:
                    if chall_question.questionPosition > position:
                        chall_question.questionPosition -= 1
                        chall_question.save()

                challenge_question.delete()
                unassign = 0

            # Check if this question does not appears in another challenge - then add it to Unassigned Problem list
            if not ChallengesQuestions.objects.filter(questionID=question.questionID):
                currentCourse = Courses.objects.get(
                    pk=int(request.session['currentCourseID']))
                chall = Challenges.objects.filter(
                    challengeName=unassigned_problems_challenge_name, courseID=currentCourse)
                for challID in chall:
                    challengeID = challID.challengeID
                challenge = Challenges.objects.get(pk=int(challengeID))
                print(request.POST['challengeID'])
                print(challengeID)

                # Check if unassigned problem list is deleting the question, if it is then delete it
                # if is not then save the question in unassigned problem list
                if (int(request.POST['challengeID']) == int(challengeID)):
                    question.delete()
                    unassign = 1
                else:
                    ChallengesQuestions.addQuestionToChallenge(
                        question, challenge, points, position)

        except Questions.DoesNotExist:
            message = "There was a problem deleting Question #" + \
                str(question.questionID) + " "+question.preview

        context_dict['message'] = message

        challengeID = request.POST['challengeID']

    # return redirect('/oneUp/instructors/challengeEditQuestions?challengeID=' + challengeID, context_dict)
    if unassign == 1:
        return redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict)
    else:
        return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeID, context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteChallenge(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:

        try:
            if request.POST['challengeID']:
                challenge = Challenges.objects.get(
                    pk=int(request.POST['challengeID']))
                message = "Challenge #" + \
                    str(challenge.challengeID) + " " + \
                    challenge.challengeName+" successfully deleted"

                # Get the Unassigned Problems challenge
                currentCourse = Courses.objects.get(
                    pk=int(request.session['currentCourseID']))
                unassignedChallenge = Challenges.objects.get(
                    challengeName=unassigned_problems_challenge_name, courseID=currentCourse)

                # Unassign all the questions from the challenge to delete by setting it under the unassign challenge object (which holds unassigned problems)
                challenge_questions = ChallengesQuestions.objects.filter(
                    challengeID=request.POST['challengeID'])
                for question in challenge_questions:
                    question.challengeID = unassignedChallenge
                    question.save()

                # Now that we unassigned questions associate with this challenge, we can delete it
                challenge.delete()

        except Challenges.DoesNotExist:
            message = "There was a problem deleting Challenge #" + \
                str(challenge.challengeID) + " "+challenge.challengeName

        context_dict['message'] = message

    if 'warmUp' in request.GET:
        return redirect('/oneUp/instructors/warmUpChallengeList', context_dict)
    else:
        return redirect('/oneUp/instructors/challengesList', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteSkill(request):

    context_dict, currentCourse = initialContextDict(request)
    if request.POST:
        try:
            if request.POST['skillID']:
                skill = Skills.objects.get(pk=int(request.POST['skillID']))
                print(skill)
                message = "skill #"+str(skill.skillID) + \
                    " "+skill.skillName+" successfully deleted"
                skill.delete()
        except Skills.DoesNotExist:
            message = "There was a problem deleting Skill #" + \
                str(skill.skillID) + " "+skill.skillName

        context_dict['message'] = message

    return redirect('/oneUp/instructors/skillsList', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteStudent(request):

    context_dict, currentCourse = initialContextDict(request)
    print(str('got here for delete student'))

    if request.POST:

        try:
            if request.POST['userID']:
                u = User.objects.get(username=request.POST['userID'])
                print(u)
                # We need to check if this student is registered in other courses.
                # If so, we should not delete it, but should only delete the StudentRejsiteredCourse entry
                student = Student.objects.get(user=u)
                studentCourses = StudentRegisteredCourses.objects.filter(
                    studentID=student)

                # KI: Changed this so that the user is not actually deleted.  This is in order to make certain that we
                # preserve the student data.  Once a student is in no courses, they should not be able to do anything in
                # the system.
                currentCourseID = int(request.session['currentCourseID'])
                student_course = StudentRegisteredCourses.objects.filter(
                    studentID=student, courseID=currentCourseID)
                student_config_params = StudentConfigParams.objects.filter(
                    studentID=student, courseID=currentCourseID)
                student_course.delete()
                student_config_params.delete()

                message = "Student " + \
                    str(u.first_name) + " "+str(u.last_name) + \
                    " was successfully deleted from this course"

        except User.DoesNotExist:
            message = "There was a problem deleting user #"

        context_dict['message'] = message

    return redirect('/oneUp/instructors/createStudentListView', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteUser(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict, currentCourse = initialContextDict(request)
    print(str('got here for delete user'))
    if request.POST:

        try:
            if request.POST['userID']:
                u = User.objects.get(username=request.POST['userID'])
                print(u)
                message = "User "+str(u.first_name) + " " + \
                    str(u.last_name)+" was successfully deleted"
                u.delete()

#                 studentEventLog = StudentEventLog.objects.filter(student = u)
#                 for sEventLog in studentEventLog:
#                     sEventLog.delete()
#                 print 'delete student event log'

        except User.DoesNotExist:
            message = "There was a problem deleting user #"

        context_dict['message'] = message

    return redirect('/oneUp/instructors/createStudentListView', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteTopic(request):

    context_dict, currentCourse = initialContextDict(request)
    if request.POST:

        try:
            if request.POST['topicID']:
                topic = Topics.objects.get(pk=int(request.POST['topicID']))
                print(topic)
                message = "topic #"+str(topic.topicID) + \
                    " "+topic.topicName+" successfully deleted"
                if topic.topicName == "Miscellaneous":
                    return redirect('/oneUp/instructors/warmUpChallengeList', context_dict)
                topic.delete()
        except Topics.DoesNotExist:
            message = "There was a problem deleting Topic #" + \
                str(topic.topicID) + " "+topic.topicName

        context_dict['message'] = message

    return redirect('/oneUp/instructors/warmUpChallengeList', context_dict)

@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteActivity(request):

    context_dict, currentCourse = initialContextDict(request)
    if request.POST:
        print("Deleting Activity")
        message = ""
        try:
            if request.POST['activityID']:
                activity = Activities.objects.get(
                    pk=int(request.POST['activityID']))
                message = "Activity #" + \
                    str(activity.activityID) + ": " + \
                    str(activity.activityID) + "was successfully deleted"
                activity.delete()
        except Activities.DoesNotExist:
            message = "There was a problem deleting Activity #" + \
                str(activity.activityID)

        context_dict['message'] = message

    return redirect('/oneUp/instructors/activitiesList', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def deleteAnnouncement(request):

    context_dict, currentCourse = initialContextDict(request)

    if request.POST:

        try:
            if request.POST['announcementID']:
                announcement = Announcements.objects.get(
                    pk=int(request.POST['announcementID']))
                message = "Announcement #"+str(announcement.announcementID) + " created by "+str(
                    announcement.authorID) + " on " + str(announcement.startTimestamp) + "was successfully deleted"
                announcement.delete()
        except Announcements.DoesNotExist:
            message = "There was a problem deleting Announcement #" + \
                str(announcement.announcementID)

        context_dict['message'] = message

    return redirect('/oneUp/instructors/announcementList', context_dict)

@login_required
def deleteManualSpendRule(request):
    context_dict, currentCourse = initialContextDict(request)
    if request.method == 'POST':
        try:
            if request.POST['vcRuleID']:
                # Delete the Virtual Currency Rule
                deleteVC = VirtualCurrencyCustomRuleInfo.objects.get(
                    pk=int(request.POST['vcRuleID']), courseID=currentCourse)
                message = "VC Spend Rule #" + \
                    str(deleteVC.vcRuleID) + " - " + \
                    str(deleteVC.vcRuleName) + " was successfully deleted"
                deleteVC.delete()

        except VirtualCurrencyCustomRuleInfo.DoesNotExist:
            message = "There was a problem deleting VC Spend Rule #" + \
                str(request.POST['vcRuleID'])
        context_dict['message'] = message
    return redirect('/oneUp/badges/VirtualCurrencySpendRuleList', context_dict)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def deleteGroup(request):
    
    context_dict, currentCourse = initialContextDict(request)
    if request.POST:

        try:
            if request.POST['groupID']:
                group= FlashCardGroup.objects.get(pk=int(request.POST['groupID']))           
                message = "Group #"+str(group.groupID)+ " "+group.groupName+" successfully deleted"
                group.delete()
        except FlashCardGroup.DoesNotExist:
            
            message = "There was a problem deleting Group #"+str(group.groupID)+ " "+group.groupName
            
        context_dict['message'] = message  
    return redirect('/oneUp/instructors/groupList', context_dict)
