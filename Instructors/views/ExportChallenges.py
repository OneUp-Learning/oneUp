
from django.template import RequestContext
from django.shortcuts import redirect
from Instructors.models import Courses, Challenges, ChallengesQuestions, StaticQuestions, Answers, MatchingAnswers, CorrectAnswers
from Badges.enums import Event, QuestionTypes

from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring, parse
import xml.etree.ElementTree as eTree
from xml.dom import minidom

def exportChallenges(request):   
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName

        root = Element('TreeRoot')
        
        el_challenges = SubElement(root, 'Challenges')
        
        challenges = Challenges.objects.filter(courseID=currentCourse)        
        for challenge in challenges:
            print(challenge)
            el_challenge = SubElement(el_challenges, 'Challenge')
            
            el_ID = SubElement(el_challenge, 'challengeID')
            el_ID.text = str(challenge.challengeID)            
            el_Name = SubElement(el_challenge, 'challengeName')
            el_Name.text = challenge.challengeName
 
            el_courseID = SubElement(el_challenge, 'courseID')
            el_courseID.text = str(challenge.courseID.courseID)            
 
            el_isGraded = SubElement(el_challenge, 'isGraded')
            el_isGraded.text = str(challenge.isGraded)            
 
            el_numberAttempts = SubElement(el_challenge, 'numberAttempts')
            el_numberAttempts.text = str(challenge.numberAttempts)            
 
            el_timeLimit = SubElement(el_challenge, 'timeLimit')
            el_timeLimit.text = str(challenge.timeLimit)            
 
            el_feedbackOption1 = SubElement(el_challenge, 'feedbackOption1')
            el_feedbackOption1.text = str(challenge.feedbackOption1)            
         
            el_feedbackOption2 = SubElement(el_challenge, 'feedbackOption2')
            el_feedbackOption2.text = str(challenge.feedbackOption2)            
         
            el_feedbackOption3 = SubElement(el_challenge, 'feedbackOption3')
            el_feedbackOption3.text = str(challenge.feedbackOption3)            
         
            el_challengeAuthor = SubElement(el_challenge, 'challengeAuthor')
            el_challengeAuthor.text = challenge.challengeAuthor            
 
            el_difficulty = SubElement(el_challenge, 'challengeDifficulty')
            el_difficulty.text = challenge.challengeDifficulty            
             
            el_challengePassword = SubElement(el_challenge, 'challengePassword')
            el_challengePassword.text = str(challenge.challengePassword)
             
            #   isVisible, startTimestamp, and endTimestamp are not saved   
             
            el_challengeQuestions = SubElement(el_challenge, 'ChallengeQuestions')           
            chall_questioins = ChallengesQuestions.objects.filter(challengeID=challenge)        
 
            for chall_question in chall_questioins:  
                print(chall_question)          
                el_challengeQuestion = SubElement(el_challengeQuestions, 'ChallengeQuestion')
                el_points = SubElement(el_challengeQuestion, 'points')
                el_points.text = str(chall_question.points)
                 
                # Questions
                question = chall_question.questionID
                print(question)
                el_question = SubElement(el_challengeQuestion, 'Question')
                 
                el_questionID = SubElement(el_question, 'questionID')
                el_questionID.text = str(question.questionID)
                 
                el_preview = SubElement(el_question, 'preview')
                el_preview.text = question.preview
                 
                el_instructorNotes = SubElement(el_question, 'instructorNotes')
                el_instructorNotes.text = question.instructorNotes
                                 
                el_type = SubElement(el_question, 'type')
                el_type.text = str(question.type)
                                                                                 
                el_difficulty = SubElement(el_question, 'difficulty')
                el_difficulty.text = question.difficulty
                 
                el_author = SubElement(el_question, 'author')
                el_author.text = question.author
             
                # Static questions
                static_question = StaticQuestions.objects.get(pk=int(question.questionID))
                print('static_question')
                print(static_question)
                el_questionText = SubElement(el_question, 'questionText')
                el_questionText.text = static_question.questionText
                el_correctAnswerFeedback = SubElement(el_question, 'correctAnswerFeedback')
                el_correctAnswerFeedback.text = static_question.correctAnswerFeedback
                el_incorrectAnswerFeedback = SubElement(el_question, 'incorrectAnswerFeedback')
                el_incorrectAnswerFeedback.text = static_question.incorrectAnswerFeedback
            
                # Answers
                el_answers = SubElement(el_question, 'Answers')
                answers = Answers.objects.filter(questionID=question.questionID)        
                print('answers')
                print(answers)
                for answer in answers:            
                    el_answer = SubElement(el_answers, 'Answer')
                    el_answerID = SubElement(el_answer, 'answerID')
                    el_answerID.text = str(answer.answerID)
 
                    el_answerText= SubElement(el_answer, 'answerText')
                    el_answerText.text = answer.answerText
                    el_questionID= SubElement(el_answer, 'questionID')
                    el_questionID.text = str(question.questionID)
                     
                # Correct Answers
                print('correctAnswers')
                el_correctAnswers = SubElement(el_question, 'CorrectAnswers')        
                correctAnswers = CorrectAnswers.objects.filter(questionID=question.questionID)        
        
                for correctAnswer in correctAnswers: 
                    print(correctAnswer)
                    el_correctAnswer = SubElement(el_correctAnswers, 'CorrectAnswer')
                    el_questionID = SubElement(el_correctAnswer, 'questionID')
                    el_questionID.text = str(correctAnswer.questionID.questionID)
 
                    el_answerID= SubElement(el_correctAnswer, 'answerID')
                    el_answerID.text = str(correctAnswer.answerID.answerID)
                         
                if chall_question.questionID.type == QuestionTypes.matching:
                    # matching answers for a matching question
                    el_matchingAnswers = SubElement(el_question, 'MatchingAnswers') 
                    m_answers = MatchingAnswers.objects.filter(questionID=question.questionID)        
                    for m_answer in m_answers:  
                        print('MatchingAnswers')
                        print(answer)
           
                        el_matchingAnswer = SubElement(el_matchingAnswers, 'MatchingAnswer')
                        el_matchingAnswerID = SubElement(el_matchingAnswer, 'matchingAnswerID')
                        el_matchingAnswerID.text = str(m_answer.matchingAnswerID)
     
                        el_matchingAnswerText= SubElement(el_matchingAnswer, 'matchingAnswerText')
                        el_matchingAnswerText.text = m_answer.matchingAnswerText
                     
                        el_answerID= SubElement(el_matchingAnswer, 'answerID')
                        el_answerID.text = str(m_answer.answerID.answerID)
                        el_questionID= SubElement(el_matchingAnswer, 'questionID')
                        el_questionID.text = str(question.questionID)
                     
                        #el_answers.append(el_matchingAnswer)
          
        tree = eTree.ElementTree(root)
#         tree.write(sys.stdout)
        print(eTree.tostring(el_challenge))  
                
        f = open('media/textfiles/xmlfiles/first.xml', 'w') 
        tree.write(f, encoding="unicode")
    
    return redirect('/oneUp/instructors/instructorCourseHome')        
            
def importChallenges(root):
      
    f = open('media/textfiles/xmlfiles/first.xml', 'r') 
    tree = parse(f)

    #print(eTree.tostring(tree))
    root = tree.getroot()
    print(minidom.parseString(eTree.tostring(root)).toprettyxml(indent = "   "))

    return redirect('/oneUp/instructors/instructorCourseHome') 
    
#   #To access the subelements, you can use ordinary list (sequence) operations. This includes len(element) to get the number of subelements, element[i] to fetch the i’th subelement, and using the for-in statement to loop over the subelements:
#   for node in root:
#       print(node)              
            