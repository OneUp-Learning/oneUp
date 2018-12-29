class QuestionTypes():
    multipleChoice=1
    multipleAnswers=2
    matching=3
    trueFalse=4
    essay=5
    dynamic=6
    templatedynamic=7
    parsons=8
    questionTypes={
        multipleChoice:{
           'index': multipleChoice,
           'name':'multipleChoice',
           'displayName':'Multiple Choice Questions',             
        },
        multipleAnswers:{
           'index': multipleAnswers,
           'name':'multipleAnswers',
           'displayName':'Multiple Answer Questions',             
        },            
        matching:{
           'index': matching,
           'name':'matching',
           'displayName':'Matching Questions',             
        },
        trueFalse:{
           'index': trueFalse,
           'name':'trueFalse',
           'displayName':'True/False Questions',             
        },
        essay:{
           'index': essay,
           'name':'essay',
           'displayName':'Essay Questions',             
        },
        dynamic:{
           'index': dynamic,
           'name':'dynamic',
           'displayName':'Dynamic Questions (Raw Lua)',                         
        },
        templatedynamic:{
           'index': templatedynamic,
           'name':'templatedynamic',
           'displayName':'Dynamic Questions (Template)',
        },  
        parsons:{
           'index': parsons,
           'name':'parsons',
           'displayName':'Parsons Problems',
        },                     
    }   

staticQuestionTypesSet = { QuestionTypes.matching, QuestionTypes.multipleAnswers, QuestionTypes.multipleChoice, QuestionTypes.trueFalse, QuestionTypes.parsons, QuestionTypes.essay }
dynamicQuestionTypesSet = { QuestionTypes.dynamic, QuestionTypes.templatedynamic }