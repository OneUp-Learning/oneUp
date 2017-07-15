'''
Created on May 1, 2017

@author: dichevad
'''
from django.shortcuts import redirect, render, HttpResponse

from Instructors.models import Courses, Challenges, ChallengesQuestions, Questions, StaticQuestions, Answers, MatchingAnswers, CorrectAnswers, UploadedFiles 
from Instructors.models import DynamicQuestions, TemplateDynamicQuestions, TemplateTextParts, QuestionLibrary, LuaLibrary, QuestionsSkills, Skills
from Badges.enums import QuestionTypes

from xml.etree.ElementTree import Element, SubElement, parse
import xml.etree.ElementTree as eTree

def str2bool(value):
    return value in ('True', 'true') 

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
       
    if request.method == 'GET':
        chall_name = [] 
        chall_ID = []      
        challenges = Challenges.objects.filter(courseID=currentCourse)        
        for challenge in challenges:
            print(challenge)
            chall_name.append(challenge.challengeName)
            chall_ID.append(challenge.challengeID)

        context_dict['challenge_range'] = zip(range(1, len(chall_name) + 1), chall_ID, chall_name)            
        return render(request,'Instructors/ChallengeExport.html', context_dict)

    if request.method == 'POST':        
       
        selectedChallenges = []
        # get the list of all checked challenges
        selected = request.POST.getlist('selected')
        selectedChallenges_num = [ int(x) for x in selected ]
        
        if not selectedChallenges_num:
            selectedChallenges = Challenges.objects.filter(courseID=currentCourse)
        else:
            for i in range(1,int(max(selectedChallenges_num))+1):
                if i in selectedChallenges_num:
                    chID =  request.POST.get('challengeID'+str(i))
                    ch = Challenges.objects.get(pk=int(chID))
                    selectedChallenges.append(ch) 
        
        # Build the tree  
        # We do not save the IDs, since upon importing the objects will be saved in the DB as new objects
                  
        root = Element('TreeRoot')
        
        el_challenges = SubElement(root, 'Challenges') 
                    
        for challenge in selectedChallenges:
            el_challenge = SubElement(el_challenges, 'Challenge')
            
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
            
            # TO DO:  Add ChallengesTopics entry
             
            el_challengeQuestions = SubElement(el_challenge, 'ChallengeQuestions')           
            chall_questioins = ChallengesQuestions.objects.filter(challengeID=challenge)        
 
            for chall_question in chall_questioins:            
                el_challengeQuestion = SubElement(el_challengeQuestions, 'ChallengeQuestion')
                el_points = SubElement(el_challengeQuestion, 'points')
                el_points.text = str(chall_question.points)
                 
                # Questions
                question = chall_question.questionID
                el_question = SubElement(el_challengeQuestion, 'Question')
                 
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
                
                # Skills for this question
                questionSkills = QuestionsSkills.objects.filter(questionID=question, challengeID=challenge)
                print(questionSkills)

                if questionSkills:
                    el_skills = SubElement(el_question, 'Skills')
                    for questionSkill in questionSkills: 
                        print('in el_skill')           
                        el_skill = SubElement(el_skills, 'Skill')
                        el_skillName = SubElement(el_skill, 'skillName')
                        el_skillName.text = questionSkill.skillID.skillName
                        print('el_skillName: ', el_skillName.text)
                        el_skillPoints = SubElement(el_skill, 'questionSkillPoints')
                        el_skillPoints.text= str(questionSkill.questionSkillPoints)
                        print('el_skillPoints.text: ', el_skillPoints.text)
            
                # Static Questions
                staticQuestions = StaticQuestions.objects.filter(questionID=int(question.questionID))
                if staticQuestions:
                    staticQuestion = staticQuestions[0]
                    
                    el_staticQuestion = SubElement(el_question, 'StaticQuestion')                    
                    el_sqQuestionText = SubElement(el_staticQuestion, 'questionText')
                    el_sqQuestionText.text = staticQuestion.questionText
                    el_sqCorrectAnswerFeedback = SubElement(el_staticQuestion, 'correctAnswerFeedback')
                    el_sqCorrectAnswerFeedback.text = staticQuestion.correctAnswerFeedback
                    el_sqIncorrectAnswerFeedback = SubElement(el_staticQuestion, 'incorrectAnswerFeedback')
                    el_sqIncorrectAnswerFeedback.text = staticQuestion.incorrectAnswerFeedback
            
                    # Answers
                    el_answers = SubElement(el_staticQuestion, 'Answers')
                    answers = Answers.objects.filter(questionID=staticQuestion)        
                    for answer in answers:            
                        el_answer = SubElement(el_answers, 'Answer')
     
                        el_answerText= SubElement(el_answer, 'answerText')
                        el_answerText.text = answer.answerText
                     
                        # Check if it is a correct answer
                        correctAnswers = CorrectAnswers.objects.filter(questionID=staticQuestion, answerID = answer)
                        if correctAnswers:
                            el_correctAnswer = SubElement(el_answer, 'correctAnswer')
                            el_correctAnswer.text = "yes"
                            
                        # Check if this answer has a matching answer
                        if chall_question.questionID.type == QuestionTypes.matching:                                               
                            m_answer = MatchingAnswers.objects.get(answerID=answer, questionID=staticQuestion) 
                            el_matchingAnswer = SubElement(el_answer, 'matchingAnswer') 
                            el_matchingAnswer.text = m_answer.matchingAnswerText
                       
                # Dynamic Questions
                dynamicQuestions = DynamicQuestions.objects.filter(questionID=int(question.questionID))
                if dynamicQuestions:
                    dynamicQuestion = dynamicQuestions[0]
                    print('dynamic_question')
                    print(dynamicQuestion)
                    
                    el_dynamicQuestion = SubElement(el_question, 'DynamicQuestion')
                    el_dqnumParts = SubElement(el_dynamicQuestion, 'numParts')
                    el_dqnumParts.text = str(dynamicQuestion.numParts)
                    el_dqcode = SubElement(el_dynamicQuestion, 'code')
                    el_dqcode.text = dynamicQuestion.code
           
                    # TemplateDynamicQuestions
                    templateDynamicQuestions = TemplateDynamicQuestions.objects.filter(questionID=int(question.questionID))
                    if templateDynamicQuestions:
                        templateDynamicQuestion = templateDynamicQuestions[0]
                    
                        el_templateDynamicQuestion = SubElement(el_dynamicQuestion, 'TemplateDynamicQuestion')
                        el_templateText = SubElement(el_templateDynamicQuestion, 'templateText')
                        el_templateText.text = str(templateDynamicQuestion.templateText)
                        el_setupCode = SubElement(el_templateDynamicQuestion, 'setupCode')
                        el_setupCode.text = str(templateDynamicQuestion.setupCode)

                        print('templateDynamicQuestion.el_setupCode.text: ', el_setupCode.text)

                        # TemplateTextParts
                        templateTextParts = TemplateTextParts.objects.filter(dynamicQuestion=question)
                        if templateTextParts:                        
                            el_templateTextParts = SubElement(el_templateDynamicQuestion, 'TemplateTextParts')
                                                   
                            for templateTextPart in templateTextParts:    
                                el_templateTextPart = SubElement(el_templateTextParts, 'TemplateTextPart')        
                                el_partNumber = SubElement(el_templateTextPart, 'partNumber')
                                el_partNumber.text = str(templateTextPart.partNumber)
                                el_templateText = SubElement(el_templateTextPart, 'templateText')
                                el_templateText.text = templateTextPart.templateText
         
                    # QuestionLibrary
                    questionLibraries = QuestionLibrary.objects.filter(question=question)
                    if questionLibraries:
                        el_questionLibraries = SubElement(el_dynamicQuestion, 'QuestionLibraries')
                        
                        for questionLibrary in questionLibraries:                      
                            el_questionLibrary = SubElement(el_questionLibraries, 'QuestionLibrary')
                            el_questionLibrary.text = questionLibrary.library.libraryName
                            print('el_questionLibrary.text: ', el_questionLibrary.text)
                          
        tree = eTree.ElementTree(root)
        print(eTree.tostring(el_challenge))  
                
        f = open('media/textfiles/xmlfiles/challenges.xml', 'w') 
        tree.write(f, encoding="unicode")        
        return render(request,'Instructors/ChallengeExportSave.html', context_dict)

       
def saveExportedChallenges(request):

    f = open('media/textfiles/xmlfiles/challenges.xml', 'r') 
    response = HttpResponse(f.read(), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="yourchallenges.xml"'

    return response


def uploadChallenges(request):
    context_dict = {}
    
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"] = request.user.username
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
        
    if request.method == 'GET':
        print("In request GET")
        return render(request,'Instructors/ChallengeImport.html', context_dict)

    if request.method == 'POST' and len(request.FILES) != 0:            
        challengesFile = request.FILES['challenges']
        uploadedFileName = challengesFile.name
        print(uploadedFileName)
        
        upfile = UploadedFiles() 
        upfile.uploadedFile = challengesFile        
        upfile.uploadedFileName = uploadedFileName
        upfile.uploadedFileCreator = request.user
        upfile.save()
    
        importChallenges(uploadedFileName)
        
        # TO DO:  After importing the challenges in the database, perhaps we need to delete the user's file

        return redirect('/oneUp/instructors/instructorCourseHome') 
    
    
def importChallenges(uploadedFileName):
         
    f = open('media/textfiles/xmlfiles/' + uploadedFileName, 'r') 
    tree = parse(f)

    root = tree.getroot()
    #print(minidom.parseString(eTree.tostring(root)).toprettyxml(indent = "   "))
    
    # get all Challenge Nodes; root[0] is the element Challenges
    for el_challenge in root[0]:
        
        # Handle the challenge element information
        
        # Create new challenge
        challenge = Challenges()  
                       
        # Set the attributes to database object
        challenge.challengeName = el_challenge.find('challengeName').text
        challenge.courseID = Courses.objects.get(pk=int(el_challenge.find('courseID').text))
        challenge.isGraded = str2bool(el_challenge.find('isGraded').text)
        challenge.numberAttempts = int(el_challenge.find('numberAttempts').text)
        challenge.timeLimit = int(el_challenge.find('timeLimit').text)
        challenge.feedbackOption1 = str2bool(el_challenge.find('feedbackOption1').text)
        challenge.feedbackOption2 = str2bool(el_challenge.find('feedbackOption2').text)
        
        challenge.feedbackOption3 = str2bool(el_challenge.find('feedbackOption3').text)
        challenge.challengeAuthor = el_challenge.find('challengeAuthor').text
        challenge.challengeDifficulty = el_challenge.find('challengeDifficulty').text
        if not challenge.challengeDifficulty:
            challenge.challengeDifficulty = 'Easy'
        
        challenge.challengePassword = el_challenge.find('challengePassword').text # Empty string represents no password required.
        if not challenge.challengePassword:
            challenge.challengePassword = ''

        challenge.save()
        
        # Get all ChallengeQuestions
        el_challengeQuestions = el_challenge.find('ChallengeQuestions')        
        for el_challengeQuestion in el_challengeQuestions.findall('ChallengeQuestion'):

            # Process Question
            el_points = el_challengeQuestion.find('points').text
            el_question = el_challengeQuestion.find('Question')
            
#  For some reason inheritance does not work

#             question = Questions()             
#             question.preview = el_question.find('preview').text
#             question.instructorNotes = el_question.find('instructorNotes').text
#             if not question.instructorNotes:
#                 question.instructorNotes = ''
#             question.type = int(el_question.find('type').text)            
#             question.difficulty = el_question.find('difficulty').text
#             if not question.difficulty:
#                 question.difficulty = 'Easy'
#             question.author = el_question.find('author').text           
#             question.save()
           
            # Process Static question           
            el_staticQuestion = el_question.find("StaticQuestion")
            if not el_staticQuestion is None:   
                #staticQuestion = StaticQuestions(question.questionID)  
                staticQuestion = StaticQuestions()
                staticQuestion.preview = el_question.find('preview').text
                staticQuestion.instructorNotes = el_question.find('instructorNotes').text
                if not staticQuestion.instructorNotes:
                    staticQuestion.instructorNotes = ''
                staticQuestion.type = int(el_question.find('type').text)
                 
                staticQuestion.difficulty = el_question.find('difficulty').text
                if not staticQuestion.difficulty:
                    staticQuestion.difficulty = 'Easy'
                staticQuestion.author = el_question.find('author').text  
                                            
                for i in range(0,2):
                    if el_staticQuestion[i].text:                       
                        setattr(staticQuestion,el_staticQuestion[i].tag,el_staticQuestion[i].text)
                    else:
                        setattr(staticQuestion,el_staticQuestion[i].tag,'')
                        
                staticQuestion.save()
                
                # Process Skills elements
                el_skills = el_question.find('Skills')
                if not el_skills is None:
                    for el_skill in el_skills.findall('Skill'):
                        questionSkill = QuestionsSkills()
                        skill = Skills.objects.filter(skillName=el_skill.find('skillName').text)
                        if skill:
                            questionSkill.skillID = skill[0]
                            questionSkill.questionID = staticQuestion
                            questionSkill.challengeID = challenge
                            questionSkill.questionSkillPoints = int(el_skill.find('questionSkillPoints').text)
                            questionSkill.save()    
                            print('questionSkill: ')
                            print(questionSkill)                
            
                # Process Answers elements
                el_answers = el_staticQuestion.find('Answers')
                if not el_answers is None:
                    for el_answer in el_answers.findall('Answer'):
                        
                        answer = Answers()     
                        answer.answerText = el_answer.find('answerText').text
                        print('answer.answerText', answer.answerText)
                        print('answer-question-ID', staticQuestion.questionID)
                        answer.questionID = staticQuestion
                        answer.save()                    

                        # Check if this answer is a correct answer               
                        el_correctAnswer = el_answer.find('correctAnswer')   
                        if not el_correctAnswer is None:   
                            print('el_correctAnswer  found')
                            correctAnswer = CorrectAnswers()  
                            correctAnswer.questionID = staticQuestion
                            correctAnswer.answerID = answer
                            correctAnswer.save()
                            print('correct answerID: ', str(correctAnswer.answerID))
                            
                        # Check if this answer has a matching answer
                        el_matchingAnswer = el_answer.find('matchingAnswer')    
                        if not el_matchingAnswer is None:
                            print('el_matchingAnswer  found')                              
                            matchingAnswer = MatchingAnswers()  
                            matchingAnswer.matchingAnswerText = el_matchingAnswer.text
                            matchingAnswer.answerID = answer
                            matchingAnswer.questionID = staticQuestion
                            matchingAnswer.save()
               
            # Process Dynamic Questions
            el_dynamicQuestion = el_question.find("DynamicQuestion")
            if not el_dynamicQuestion is None:  
                  
                dynamicQuestion = DynamicQuestions()  
                
                dynamicQuestion.preview = el_question.find('preview').text
                dynamicQuestion.instructorNotes = el_question.find('instructorNotes').text
                if not dynamicQuestion.instructorNotes:
                    dynamicQuestion.instructorNotes = ''
                dynamicQuestion.type = int(el_question.find('type').text)                
                dynamicQuestion.difficulty = el_question.find('difficulty').text
                if not dynamicQuestion.difficulty:
                    dynamicQuestion.difficulty = 'Easy'
                dynamicQuestion.author = el_question.find('author').text  
                                
                dynamicQuestion.numParts = int(el_dynamicQuestion.find('numParts').text)
                dynamicQuestion.code = el_dynamicQuestion.find('code').text                            
                print('dynamicQuestion.code: ', dynamicQuestion.code)  
                dynamicQuestion.save()
                        
                # TemplateDynamicQuestions
                el_templateDynamicQuestion = el_dynamicQuestion.find("TemplateDynamicQuestion")

                if not el_templateDynamicQuestion is None:    
                    templateDynamicQuestion = TemplateDynamicQuestions(dynamicQuestion.questionID)      
                    templateDynamicQuestion.templateText = el_dynamicQuestion.find('templateText').text
                    templateDynamicQuestion.setupCode = el_dynamicQuestion.find('setupCode').text
                    print('templateDynamicQuestion.templateText: ', templateDynamicQuestion.templateText)  
                    templateDynamicQuestion.save()
                
                    # TemplateTextParts
                    el_templateTextParts = el_dynamicQuestion.find("TemplateTextParts")  
                    if not el_templateTextParts is None:
                        
                        for el_templateTextPart in el_templateTextParts.findall('TemplateTextPart'):                            
                            templateTextPart = TemplateTextParts()          
                            templateTextPart.partNumber = int(el_templateTextPart.find('partNumber').text)
                            templateTextPart.dynamicQuestion = templateDynamicQuestion
                            templateTextPart.templateText = el_templateTextPart.find('templateText').text
                            templateTextPart.save()                    
                            print('templateTextPart.templateText: ', templateTextPart.templateText)
                                      
                    # QuestionLibrary
                    el_questionLibraries = el_dynamicQuestion.find("QuestionLibraries") 
                    if not el_questionLibraries is None:  
                        for el_questionLibrary in el_questionLibraries.findall('QuestionLibrary'):
                            questionLibrary = QuestionLibrary()                             
                            questionLibrary.question = dynamicQuestion
                            qlibrary = LuaLibrary.objects.get(libarayName=el_questionLibrary.text)
                            questionLibrary.library = qlibrary
                            questionLibrary.save()                    
                            print('questionLibrary: ', str(questionLibrary.ID))
                                                       
            # Save the information in ChallengeQuestion object
            challengeQuestion = ChallengesQuestions()
            challengeQuestion.challengeID = challenge
            if staticQuestion:
                challengeQuestion.questionID = staticQuestion
            else:
                challengeQuestion.questionID = dynamicQuestion
            challengeQuestion.points = int(el_points)  
                          
            print('challengeQuestion: ') 
            print(challengeQuestion) 
            challengeQuestion.save()

    return

    #return redirect('/oneUp/instructors/instructorCourseHome') 
                 
            