#
# Created  updated 10/21/2019
# GGM
#

from django.shortcuts import render, redirect

from Instructors.models import StaticQuestions, Answers, CorrectAnswers
from Instructors.models import Challenges, ChallengesQuestions

from Instructors.views.utils import initialContextDict, getCourseSkills, addSkillsToQuestion, saveTags, getSkillsForQuestion, extractTags, utcDate
from Badges.enums import ObjectTypes
from Instructors.questionTypes import QuestionTypes
from Instructors.constants import unassigned_problems_challenge_name, default_time_str, unlimited_constant


from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal

from oneUp.logger import logger
import re
from django.templatetags.i18n import language
from sqlparse.utils import indent
from django.template.defaultfilters import length
from oneUp.decorators import instructorsCheck
from oneUp.ckeditorUtil import config_ck_editor

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def parsonsForm(request):
    context_dict, currentCourse = initialContextDict(request)

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback',
                  'incorrectAnswerFeedback','instructorNotes','author'];

    if 'view' in request.GET:
        context_dict['view'] = 1
             
    context_dict['skills'] = getCourseSkills(currentCourse)
    context_dict['tags'] = []
    if request.method == 'POST':

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            qi = request.POST['questionId']
            if not qi == "":
                logger.debug('questionId '+request.POST['questionId'])
                question = StaticQuestions.objects.get(pk=int(qi))
            else:
                question = StaticQuestions()
        else:
            question = StaticQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
            
        question.difficulty = request.POST['difficulty']
        
        # Fix the question type
        question.type = QuestionTypes.parsons
        
        if question.author == '':
            question.author = request.user.username
        
        question.save();  
        
        # Save the entered model solution as "correctAnswer"        
        answers = Answers.objects.filter(questionID=question)
        if answers:
            answer = answers[0]
            answer.answerText = "";
            languageName = request.POST['languageName']
            indentationBoolean = request.POST['indetationBoolean']
            
            languageName = "Language:"+languageName+";"
            indentationBoolean = "Indentation:" + indentationBoolean+";"
            
            instructorLine = languageName + indentationBoolean
            answer.answerText += instructorLine
            setUpCode = request.POST['setupCode']
            print("setupcode", setUpCode)
            ##setUpCode = re.sub("\r\n\s{4}", "\r\n\t", setUpCode)
            answer.answerText += setUpCode
            print("Answer edit answer:", repr(answer.answerText))
            answer.save()
            # no need to change correct answer
            #correctAnswerObject = CorrectAnswers.objects.filter(questionID=question)
        else:
            answer = Answers()         
            answer.questionID = question
           #we are crafting a new answer in this section
           # answer.answerText = request.POST['setupCode']
            
            answer.answerText = "";
            languageName = request.POST['languageName']
            indentationBoolean = request.POST['indetationBoolean']
            
            languageName = "Language:"+languageName+";"
            indentationBoolean = "Indentation:" + indentationBoolean+";"
            
            instructorLine = languageName + indentationBoolean
            
            
            answer.answerText += instructorLine
            setUpCode = request.POST['setupCode']
            print("setupcode", setUpCode)
            ##setUpCode = re.sub("\r\n\s{4}", "\t", setUpCode)
            answer.answerText += setUpCode
            print("Answer new answer", answer.answerText)
            answer.save()
            # the answer is also the correct answer - model solution to be displayed to the student
            correctAnswerObject = CorrectAnswers()
            correctAnswerObject.questionID = question           
            correctAnswerObject.answerID = answer
            correctAnswerObject.save()

       
        # Processing and saving tags in DB
        saveTags(request.POST['tags'], question, ObjectTypes.question)
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved            
            
            position = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).count() + 1
            
            if  'questionId' in request.POST:                         
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for chall_question in challenge_question:
                    position = chall_question.questionPosition
                
                challenge_question.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
        
            ChallengesQuestions.addQuestionToChallenge(question, challenge, Decimal(request.POST['points']), position)

            # Processing and saving skills for the question in DB
            addSkillsToQuestion(currentCourse,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
    
            # Processing and saving tags in DB
            
            saveTags(request.POST['tags'], question, ObjectTypes.question)
                
                
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
        # Question is unassigned so create unassigned challenge object
        challenge = Challenges()
        challenge.challengeName = unassigned_problems_challenge_name
        challenge.courseID = currentCourse
        challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.numberAttempts = unlimited_constant
        challenge.timeLimit = unlimited_constant
        challenge.save()
        ChallengesQuestions.addQuestionToChallenge(question, challenge, 0, 0)
        
        redirectVar = redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict)
        return redirectVar

    elif request.method == 'GET':
            
        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True
            context_dict['tags'] = []
            
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
                context_dict["unassign"]= 1
            
        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = StaticQuestions.objects.get(pk=int(request.GET['questionId']))
            
            # Copy all of the attribute values into the context_dict to display them on the page.
            context_dict['questionId']=request.GET['questionId']
            
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)

            # Load the model solution, which is stored in Answers
            answer = Answers.objects.filter(questionID=question)
            answer = answer[0].answerText
            context_dict['languageName'] = re.search(r'Language:([^;]+)', answer).group(1).lower().lstrip()
            context_dict['indentation'] = re.search(r';Indentation:([^;]+);', answer).group(1)
            print("language", context_dict['languageName'])
            print("indentation", context_dict['indentation'])
            
            languageAndLanguageName = re.search(r'Language:([^;]+)', answer)
            intentationEnabledVariableAndValue = re.search(r';Indentation:([^;]+);', answer)
            answer = answer.replace(languageAndLanguageName.group(0), "")
            answer = answer.replace(intentationEnabledVariableAndValue.group(0), "")
            
            answer =  re.sub("^ *\\t", "  ", answer)
            
            #tokenizer characters ☃ and ¬
            answer = re.sub("\n", "\n¬☃", answer)
            answer = re.sub("^[ ]+?", "☃", answer)
            
            #we turn the student solution into a list
            answer = [x.strip() for x in answer.split('¬')]
            
            #get how many spces there are in the first line
            print("answer[0]",answer[0])
            answer[0] = re.sub("☃"," ",answer[0])
            leadingSpacesCount = len(answer[0]) - len(answer[0].lstrip(' '))
            print("leading spaces", leadingSpacesCount)
            
            #give each string the new line
            tabedanswer = []
            lengthOfModelSolution = len(answer)
            for index, line in enumerate(answer):
                line = re.sub("☃", "", line)
                line = re.sub("^[ ]{" + str(leadingSpacesCount) + "}", "", line)
                if index < len(answer)- 1:
                    line = line +"\n"
                tabedanswer.append(line)
            
            answer = ""
            answer = answer.join(tabedanswer)
            
            
            context_dict['model_solution'] = answer
            
 
            # Extract the tags from DB            
            context_dict['tags'] = extractTags(question, "question")
            
            if 'challengeID' in request.GET:
                # get the challenge points for this problem to display
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                if challenge_questions:
                    context_dict['points'] = challenge_questions[0].points
                    
                    # set default skill points - 1
                    context_dict['q_skill_points'] = int('1')
    
                    # Extract the skill                                        
                    context_dict['selectedSkills'] = getSkillsForQuestion(currentCourse,question)   

            print("loaded feedback")
            context_dict['incorrectAnswerFeedback'] = question.correctAnswerFeedback
            context_dict['incorrectAnswerFeedback'] = question.incorrectAnswerFeedback

        if 'questionId' in request.POST:         
            return redirect('challengesView')
        
        context_dict['ckeditor'] = config_ck_editor()
    
    return render(request,'Instructors/ParsonsForm.html', context_dict)

#parsons grading software for grading inside the system.
@login_required
def parsonDynamicGrader(request):
    ##this is used to track how many times the student clicks class average
    ##we use ajax to track the information, otherwise they'd get the page refreshed on them
    ##and it would be "wrong".
    from django.http import JsonResponse

    context_dictionary,current_course = studentInitialContextDict(request)
    student_id = context_dictionary['student']
    ##if we posted data with ajax, use it, otherwise just return.
    if request.POST:
        gradeParson()
        print("ajax call", context_dictionary, student_id)
        return JsonResponse({})
    
# def normalizeIndents(lines):
#       var normalized = [];
#       var new_line;
#       var match_indent = function(index) {
# 	  //return line index from the previous lines with matching indentation
# 	  for (var i = index-1; i >= 0; i--) {
#               if (lines[i].indent == lines[index].indent) {
# 		  return normalized[i].indent;
#               }
# 	  }
# 	  return -1;
#       };
#       for ( var i = 0; i < lines.length; i++ ) {
# 	  //create shallow copy from the line object
# 	  new_line = jQuery.extend({}, lines[i]);
# 	  if (i === 0) {
#               new_line.indent = 0;
#               if (lines[i].indent !== 0) {
# 		  new_line.indent = -1;
#               }
# 	  } else if (lines[i].indent == lines[i-1].indent) {
#               new_line.indent = normalized[i-1].indent;
# 	  } else if (lines[i].indent > lines[i-1].indent) {
#               new_line.indent = normalized[i-1].indent + 1;
# 	  } else {
#               // indentation can be -1 if no matching indentation exists, i.e. IndentationError in Python
#               new_line.indent = match_indent(i);
# 	  }
# 	  normalized[i] = new_line;
#       }
#       return normalized;
#   }; 

# def getModifiedCode(search_string):
#     #this gets the ids of the modified code
#     #search string is passed as an array, or we could pass in ids
#     lines_to_return = []
#     solution_ids = search_string
#     i, item;
#       for (i = 0; i < solution_ids.length; i++) {
# 	      item = this.getLineById(solution_ids[i]);
# 	      lines_to_return.push($.extend(new ParsonsCodeline(), item));
#       }
#       return lines_to_return;

# def gradeParsonSecurely(parson):    
#     #The "original" grader for giving line based feedback has now become a python based grader
#   # var LineBasedGrader = function(parson) {
#   #   this.parson = parson;
#   # };
#   # graders.LineBasedGrader = LineBasedGrader;
# #    var parson = this.parson;
#     #var elemId = elementId || parson.options.sortableId;
#     var student_code = parson.normalizeIndents(parson.getModifiedCode("#ul-" + elemId));
#     var lines_to_check = Math.min(student_code.length, parson.model_solution.length);
#     var errors = [], log_errors = [];
#     var incorrectLines = [], studentCodeLineObjects = [];
#     var i;
#     var wrong_order = false;

#     // Find the line objects for the student's code
#     for (i = 0; i < student_code.length; i++) {
#       studentCodeLineObjects.push($.extend(true, 
#     	                                   {},
#     	                                   parson.getLineById(student_code[i].id)));
#     }

#     // This maps codeline strings to the index, at which starting from 0, we have last
#     // found this codeline. This is used to find the best indices for each 
#     // codeline in the student's code for the LIS computation and, for example,
#     // assigns appropriate indices for duplicate lines.
#     var lastFoundCodeIndex = {};
#     $.each(studentCodeLineObjects, function(index, lineObject) {
#     	// find the first matching line in the model solution
#     	// starting from where we have searched previously
#     	for (var i = (typeof(lastFoundCodeIndex[lineObject.code]) !== 'undefined') ? lastFoundCodeIndex[lineObject.code]+1 : 0; 
#     	     i < parson.model_solution.length;
#     	     i++) {
#     	  if (parson.model_solution[i].code === lineObject.code) {
#     		  // found a line in the model solution that matches the student's line
#     		  lastFoundCodeIndex[lineObject.code] = i;
#               lineObject.lisIgnore = false;
#               // This will be used in LIS computation
#         	  lineObject.position = i;
#         	  break;
#     	  }
#     	}
#     	if (i === parson.model_solution.length) {
#     	  if (typeof(lastFoundCodeIndex[lineObject.code]) === 'undefined') {
# 	    	// Could not find the line in the model solution at all,
# 	    	// it must be a distractor
# 	    	// => add to feedback, log, and ignore in LIS computation
# 	        wrong_order = true;
# 	        lineObject.markIncorrectPosition();
# 	    	incorrectLines.push(lineObject.orig);
# 	        lineObject.lisIgnore = true;
# 	      } else {
# 	        // The line is part of the solution but there are now
# 	    	// too many instances of the same line in the student's code
# 	          // => Let's just have their correct position to be the same
# 	    	// as the last one actually found in the solution.
# 	        // LIS computation will handle such duplicates properly and
# 	    	// choose only one of the equivalent positions to the LIS and
# 	        // extra duplicates are left in the inverse and highlighted as
# 	    	// errors.
# 	        // TODO This method will not always give the most intuitive 
# 	    	// highlights for lines to supposed to be moved when there are 
# 	        // several extra duplicates in the student's code.
#                   lineObject.lisIgnore = false;
#                   lineObject.position = lastFoundCodeIndex[lineObject.code];
# 	  }
	         
#     	}
#     });
    
#     var lisStudentCodeLineObjects = 
#     studentCodeLineObjects.filter(function (lineObject) { return !lineObject.lisIgnore; });
#     var inv = 
#     LIS.best_lise_inverse_indices(lisStudentCodeLineObjects
#     			 	  .map(function (lineObject) { return lineObject.position; }));
#     $.each(inv, function(_index, lineObjectIndex) {
#     	// Highlight the lines that could be moved to fix code as defined by the LIS computation
#         lisStudentCodeLineObjects[lineObjectIndex].markIncorrectPosition();
#         incorrectLines.push(lisStudentCodeLineObjects[lineObjectIndex].orig);
#     });
#     if (inv.length > 0 || incorrectLines.length > 0) {
#             wrong_order = true;
#             log_errors.push({type: "incorrectPosition", lines: incorrectLines});
#     }

#     if (wrong_order) {
#             errors.push(parson.translations.order());
#     }

#     // Check the number of lines in student's code
#     if (parson.model_solution.length < student_code.length) {
#       $("#ul-" + elemId).addClass("incorrect");
#       errors.push(parson.translations.lines_too_many());
#       log_errors.push({type: "tooManyLines", lines: student_code.length});
#     } else if (parson.model_solution.length > student_code.length){
#       $("#ul-" + elemId).addClass("incorrect");
#       errors.push(parson.translations.lines_missing());
#       log_errors.push({type: "tooFewLines", lines: student_code.length});
#     }

#     // Finally, check indent if no other errors
#     if (errors.length === 0) {
#       for (i = 0; i < lines_to_check; i++) {
#         var code_line = student_code[i];
#         var model_line = parson.model_solution[i];
#         if (code_line.indent !== model_line.indent &&
#              ((!parson.options.first_error_only) || errors.length === 0)) {
#           code_line.markIncorrectIndent();
#           errors.push(parson.translations.block_structure(i+1));
#           log_errors.push({type: "incorrectIndent", line: (i+1)});
#         }
#         if (code_line.code == model_line.code &&
#              code_line.indent == model_line.indent &&
#              errors.length === 0) {
#           code_line.markCorrect();
#         }
#       }
#     }

#     return {errors: errors, log_errors: log_errors, success: (errors.length === 0)};
#   };
# #     <script>
# #     function track_get_class_avg_click()
# #    {    
# #        var student_id = "{{student}}";
# #        console.log(student_id);

# #        $.ajax({
# #                 url: "/oneUp/students/Track_class_avg_button_clicks", 
# #                 dataType: 'json',
# #                 async: true,
# #                 type: 'POST',
# #                 data: {student_id: "student_id"}
# #             });

# #    }

# # </script>

