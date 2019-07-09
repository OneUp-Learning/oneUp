import importlib
from oneUp.settings import BASE_DIR
import os

lupa_spec = importlib.util.find_spec('lupa')
lupa_available = True
if lupa_spec is None:
    # We are on a platform with no lupa installed.  Ooops.
    # We note this and then make stub methods to make sure everything still compiles right even though it can't run correctly.
    lupa_available = False
    
    def sandboxLupaWithLibraries(libs,seed):
        return None
    class LupaRuntimeLink:
        error_str = "Dynamic problems are unavailable on this server because Lupa is not loaded.  Please contact your administrator."

        def __init__(self,libs,seed,make=True):
            return
        def getIdentifier(self):
            return self.error_str
        def checkIdentifier(self,ident):
            return False
        def dump(self):
            return self.error_str
        @staticmethod
        def getLinkFromIdAndDump(ident,dump):
            return LupaRuntimeLink([],0,True)
        def eval(self,code):
            return self.error_str
        def sys_exec(self,code):
            return self.error_str
        def user_exec(self,code):
            return self.error_str
        @staticmethod
        def clearCache_FOR_TESTING_ONLY():
            return None            
        def removeFromCache(self):
            return None
    
    class LupaQuestion(object):
        error_str = "Dynamic problems are unavailable on this server because Lupa is not loaded.  Please contact your administrator."

        def __init__(self,code,libs,seed,formid,numParts):    
            return
        def getRuntime(self):
            return LupaRuntimeLink([],0,True)
        def updateRuntime(self, runtime):
            return
        def getQuestionPart(self,n):
            return self.error_str
        def answerQuestionPart(self,n,answer_dict):
            return self.error_str
        def getPartMaxPoints(self,n):
            return self.error_str
        def getPartExamleAnswers(self,n):
            return self.error_str
        def serialize(self):
            return self.error_str
        def setError(self,result, current_code):
            return self.error_str
        @staticmethod
        def createFromDump(dump):
            return LupaQuestion.error_str

else:
    # All good.  This is the part which should be run under normal circumstances.
    
    from lupa import LuaRuntime
    from lupa import LuaError
    from lupa import lua_type
    from uuid import uuid4
    import re
    import json
    
    # Safe functions as drawn from http://lua-users.org/wiki/SandBoxes
    # Coroutine functions are left out because they should probably not
    # be necessary  and used wrongly couldreally bog down the processor
    toplevel_functions = {"assert","error","ipairs","next","pairs","pcall","select",
                 "tonumber","tostring","type","unpack","_VERSION","xpcall","print"}
    modules = { "string":{"byte","char","find","format","gmatch","gsub",
                         " len","lower","match","rep","reverse","sub","upper"},
                "table":{"insert","maxn","remove","sort"},
                "math":{"abs","acos","asin","atan","atan2","ceil","cos","cosh",
                        "deg","exp","floor","fmod","frexp","huge","ldexp","log",
                        "log10","max","min","modf","pi","pow","rad","random",
                        "sin","sinh","sqrt","tan","tanh"},
                "os":{"clock","difftime","time"},
                "python":{"iter"}
    }
    
    def sandboxLupaWithLibraries(libs,seed):
        lua = LuaRuntime()
                
        # We need to change the seed for the random function now because the sandboxing
        # will remove that ability (not so much for security reasons, although it might
        # be possible that an obscure attack exists, but for reasons of preventing the
        # instructor from accidentally setting it outside our interface and thus messing
        # up the randomization of problems).
        setRandomSeed = lua.eval("math.randomseed")
        setRandomSeed(seed)
        
        # There's an obscure problem which appears to occur in some version of Lua where
        # the first random seed is always low.  This may be fixed already in the version
        # we're using, but the overhead of generating one additional random number is so
        # small that it's worth doing just in case.
        lua.eval("math.random()")
        sandbox = lua.eval("{}")
        
        globalstuff = lua.globals()
            
        for fun in toplevel_functions:
            setattr(sandbox,fun,getattr(globalstuff,fun))
            
        for name in modules.keys():
            table = lua.eval("{}")
            for fun in modules[name]:
                setattr(table,fun,getattr(getattr(globalstuff,name),fun))
            setattr(sandbox,name,table)
        
        lua.execute("package.path = package.path .. ';"+BASE_DIR+os.sep+"lua"+os.sep+"system-libs/?.lua;"+BASE_DIR+os.sep+"media"+os.sep+"lua"+
                    os.sep+"uploadedLuaLibs/?.lua'")
        libs.append("programinterface")
        #print(lua.eval("package.path"))
        #print("LIBS:"+str(libs))
        for lib in libs:
            #print("Adding library: "+lib)
            libTable = lua.eval('require "'+lib+'"')
            setattr(sandbox,lib,libTable)
        
        setfenv = lua.eval("setfenv")
        setfenv(0, sandbox)
        return lua
    
    class LuaErrorType:
        syntax = 7701
        module_not_found = 7702
        runtime = 7703
        required_part_not_defined = 7704
        answer_sorting_error = 7705
    
    luaModuleNotFoundRegex = re.compile("\s*module '(.*)' not found")
    luaModuleSyntaxErrorRegex = re.compile("\s*error loading module '(.*)' from file '(.*)':(.*)")
    luaMainErrorRegex = re.compile('\s*(error loading code:)?\s*(.*):(\d+):(.*)')
    luaErrorPythonStringRegex = re.compile('.*string.*python')
    # Parses a Lua Error and returns a dictionary which contains information gleaned from the error message
    def parseLuaError(luaerr):
        errstr = str(luaerr)
        
        # A dictionary which we're going to fill with information about the error
        error = {}
        
        main_matches = re.match(luaMainErrorRegex,errstr)
        if main_matches and main_matches.group(1):
            # This means it contains the "error loading code" part and thus is a syntax error.
            error['type'] = LuaErrorType.syntax
        else: 
            mnf_matches = re.match(luaModuleNotFoundRegex,errstr)
            if mnf_matches:
                error['type'] = LuaErrorType.module_not_found
                error['module'] = mnf_matches.group(1)
            else:
                mse_matches = re.match(luaModuleSyntaxErrorRegex,errstr)
                if mse_matches:
                    error['type'] = LuaErrorType.syntax
                    error['source'] = 'module'
                    error['module'] = mse_matches.group(1)
                    error['module_file'] = mse_matches.group(2) # this should be the same as the file, but we record it here, just in case.
                    #print("MODULE ERROR MESSAGE:\n"+errstr+"\n\n")
                    main_matches = re.match(luaMainErrorRegex,errstr.splitlines()[1])
                else:
                    error['type'] = LuaErrorType.runtime
        
        if re.match(luaErrorPythonStringRegex,main_matches.group(2)):
            error['source'] = 'input'
        else:
            error['source'] = 'module'
            error['file'] = main_matches.group(2)
        error['line'] = int(main_matches.group(3))
        error['message'] = main_matches.group(4)
        
        return error            
    
    class LupaRuntimeLink:
        cache = {}
            
        def __init__(self,libs,seed,make=True):
            self.libs = libs
            self.seed = seed
            if make:
                self.uuid = str(uuid4())
                self.history = []
                self.runtime = sandboxLupaWithLibraries(libs,seed)
                self.version = 0
                self.cache[self.uuid] = self
            
        def getIdentifier(self):
            return str(self.uuid)+'+'+str(self.version)
        
        def checkIdentifier(self,ident):
            parts = ident.split('+')
            return parts[0] == self.uuid and parts[1] == self.version
    
        def dump(self):
            dictionary = {
                    'seed':self.seed,
                    'libs':self.libs,
                    'history':self.history,
            }
            return json.dumps(dictionary)
            
        @staticmethod
        def getLinkFromIdAndDump(ident,dump):
            parts = ident.split('+')
            uuid = parts[0]
            version = int(parts[1])
            
            if uuid in LupaRuntimeLink.cache:
                link = LupaRuntimeLink.cache[uuid]
                if link.version == version:
                    return link
            dictionary = json.loads(dump)
            link = LupaRuntimeLink(dictionary['libs'],float(dictionary['seed']),False)
            link.history = dictionary['history']
            link.uuid = uuid
            link.version = version
            link.runtime = sandboxLupaWithLibraries(link.libs,link.seed)
    
    #       set_persistents = runtime.eval('function (val) persistents=val return end')
    #       set_persistents(self.persistents)
            for cmdtype,text in link.history:
                if cmdtype == 'eval':
                    link.runtime.eval(text)
                if cmdtype == 'execute':
                    link.runtime.execute(text)
    
            LupaRuntimeLink.cache[uuid] = link 
            return link
        
        def eval(self,code):
            try:
                result = self.runtime.eval(code)
                self.history.append(('eval',code))
                #print ("EVAL:"+code)
                self.version += 1
                return (True,result)
            except LuaError as luaerr:
                return (False,parseLuaError(luaerr))
        def sys_exec(self,code):
            try:
                result = self.runtime.execute(code)
                self.history.append(('execute',code))
                #print ("SYS_EXEC:"+code)
                self.version += 1
                return True
            except LuaError as luaerr:
                return parseLuaError(luaerr)
        def user_exec(self,codesegments):            
            # We have to put the code segments together to form the actual code 
            code = ""
            for codeseg in codesegments:
                code += codeseg['code']
            
            self.history.append(('execute',code))
            #print ("USER_EXEC:"+code)
            self.version += 1
            
            try:
                self.runtime.execute(code)
                return True
            except LuaError as luaerr:
                return parseLuaError(luaerr)
    
        @staticmethod
        def clearCache_FOR_TESTING_ONLY():
            LupaRuntimeLink.cache = {}
            
        def removeFromCache(self):
            LupaRuntimeLink.cache[self.uuid] = None
    
    class LupaQuestion(object):
        
        def __init__(self,code_segments,libs,seed,formid,numParts):
            self.code_segments = code_segments
            self.libs = libs
            self.seed = seed
            self.uniqid = formid
            self.numParts = int(numParts)
            self.error = None
            
            # This should not actually be used in practice, but we need to set it in case there's an error in the 
            # initial build because setError expects it to exist.  We should not end up with an error in that part
            # of the code, however, because it is not yet being run.
            self.user_code_segments = code_segments 
                        
            try:
                runtime = LupaRuntimeLink(libs,seed)
            except LuaError as luaerr:
                self.setError(parseLuaError(luaerr),"module loading")
                return

            # We start the header code to make sure that the user code is all more than 10 lines into the Lua so that we can know that anything from a
            # line number greater than 10 is from the user code portion since all of the system execs are only a line or two long.
            # We use this to distinguish between errors in the code which was immediately run and the code used to set-up the problem.
            header_code = '\n'*10 + '''
    _debug_print = print
    _debug_print_table = function (t) for k,v in pairs(t) do _debug_print(k..'='..v) end end 

    _output = ""
    print =
        function (s)
            _output = _output .. tostring(s)
        end
    
    _inputs = {}
    _init_inputs =
        function (num_inputs)
            for i=1,num_inputs do
                _inputs[i]={}
                _inputs[i]['_sequence_number']=1
            end
        end
    _current_part = 1
    _uniqid = nil
    _set_uniqid =
        function (v)
            _uniqid = v
        end
        
    make_input =
        function (name,type,size)
            local fullname = _uniqid..'-'.._current_part..'-'..name
            local originaltype = type
            type = string.upper(type)
            _inputs[_current_part][name] = {}
            _inputs[_current_part][name]['type'] = type
            _inputs[_current_part][name]['seqnum'] = _inputs[_current_part]['_sequence_number']
            _inputs[_current_part]['_sequence_number'] = _inputs[_current_part]['_sequence_number'] + 1
            local i,j = string.find(type,'CODE')
            if i ~= nil then
                local lang = string.sub(originaltype,j+2,-1)
                -- Now we trim whitespace from lang
                lang = lang:match'^()%s*$' and '' or lang:match'^%s*(.*%S)'
                
                return '<div class="ace-editor" id="'..fullname..'" title="'..lang..'" style="height: 200px; width: 500px">'..
                       'Type your code here!</div>'..
                       '<input type="hidden" name="'..fullname..'" id="'..fullname..'-hidden">'
            end
            local by_type = {
                ["NUMBER"] =
                    function ()
                        return '<input type="text" name="'..fullname..'">'..
                               '<span class="helper-text">'..name..'</span>'
                    end,
                ["STRING"] = 
                    function ()
                        return '<input type="text" name="'..fullname..'">'..
                               '<span class="helper-text">'..name..'</span>'
                    end
            }
            return by_type[type]()
        end
    
            '''
            
            header_code_seg = CodeSegment.new(CodeSegment.system_lua,header_code,"")
            set_uniqid_code_seg = CodeSegment.new(CodeSegment.system_lua,'_set_uniqid("'+self.uniqid+'")\n',"")
            init_inputs_code_seg = CodeSegment.new(CodeSegment.system_lua,'_init_inputs('+str(self.numParts)+')\n',"")
            
            prepended_code_segments = [header_code_seg, set_uniqid_code_seg, init_inputs_code_seg] + code_segments
            
            self.user_code_segments = prepended_code_segments
            result = runtime.user_exec(prepended_code_segments)
            
            self.updateRuntime(runtime)
            
            if result != True:
                self.setError(result,"")   # We leave current code empty because the current code is used for situations where the error did not
                                           # occur in the big block of user code which defines the question.  This is that block of code so there's no
                                           # other possibility
    
        def setError(self,result, current_code):
            if result == True:
                return
            if result['type'] == LuaErrorType.required_part_not_defined:
                self.error = result
                return
            line = result['line']
            if line < 10:
                result['segment']=CodeSegment.new(CodeSegment.system_lua, current_code,"")
            else:
                lines_remaining = line
                prev_lines_remaining = line
                code_segment_index = 0
                num_code_segments = len(self.user_code_segments)
                while lines_remaining > 0 and code_segment_index < num_code_segments:
                    prev_lines_remaining = lines_remaining
                    lines_remaining -= self.user_code_segments[code_segment_index]['num_new_lines']
                    code_segment_index += 1
                code_segment_index -= 1
                result['line'] = prev_lines_remaining
                result['segment'] = self.user_code_segments[code_segment_index]
                result['has_previous_segment']=code_segment_index > 0
                if code_segment_index > 0:
                    result['previous_segment']= self.user_code_segments[code_segment_index-1]
            self.error=result
    
        def getRuntime(self):
            try:
                runtime = LupaRuntimeLink.getLinkFromIdAndDump(self.lupaid, self.lupadump)
                return runtime
            except LuaError as luaerr:
                self.setError(parseLuaError(luaerr),"runtime reconstruction")
                return None
    
        def updateRuntime(self, runtime):
            self.lupaid = runtime.getIdentifier()
            self.lupadump = runtime.dump()
        
        def getQuestionPart(self,n):
            runtime = self.getRuntime()
            if runtime is None:
                return False
            (success,result) = runtime.eval('part_'+str(n)+'_text')
            self.updateRuntime(runtime)
            if not success:
                self.setError(result)
                return False
            if result is None:
                self.setError({'type':LuaErrorType.required_part_not_defined,
                               'number':n,
                               'function_name':'part_'+str(n)+'_text'},
                              "")
                return False
            
            question_code = '_output = ""\n'
            question_code += '_current_part = ' + str(n) + '\n'
            question_code += '_qtext = part_'+str(n)+'_text()\n'
            question_code += 'if _qtext==nil then _qtext="" else _qtext=tostring(_qtext) end\n'
            exec_result = runtime.sys_exec(question_code)
            if exec_result != True:
                self.setError(exec_result,question_code)
                self.updateRuntime(runtime)
                return False

            output_value = '_output .. _qtext'
            (success,result) = runtime.eval(output_value)
            self.updateRuntime(runtime)

            if not success:
                self.setError(result,output_value)
                return False
            else:
                return result
        
        def answerQuestionPart(self,n,answer_dict):
            runtime = self.getRuntime()
            if runtime is None:
                print("ERROR: no runtime")
                return False
            (success,evalAnswerFunc) = runtime.eval('evaluate_answer_'+str(n))
            if not success:
                self.updateRuntime(runtime)
                self.setError(evalAnswerFunc,"")
                print("ERROR: no evaluate_answer_1 function")
                return False
            if evalAnswerFunc is None:
                self.updateRuntime(runtime)
                self.setError({'type':LuaErrorType.required_part_not_defined,
                               'number':n,
                               'function_name':'evaluate_answer_'+str(n)},
                              "")
                print("ERROR: "+str(self.error))
                return False
            self.updateRuntime(runtime)
            try:
                results = evalAnswerFunc(answer_dict)
            except LuaError as luaerr:
                self.updateRuntime(runtime)
                self.setError(parseLuaError(luaerr), 'evaluate_answer_'+str(n)+'('+str(answer_dict)+')')
                print("ERROR: "+str(self.error))
                return False                
                
            # There are problems dealing with Lua tables in Django templates, so we create
            # Python lists instead.  This also gives us a chance to sort things into the correct order.
            pyresults = []
            for answer_name in results:
                answer = results[answer_name]
                pyanswer = {}
                pyanswer['success']=answer['success']
                pyanswer['value']=answer['value']
                (success,pyanswer['seqnum'])=runtime.eval("_inputs["+str(n)+"]['"+answer_name+"']['seqnum']")
                if not success:
                    self.updateRuntime(runtime)
                    self.setError({'type':LuaErrorType.answer_sorting_error,
                                   'line':0,
                                   'number':n,
                                   'answer_name':answer_name,
                                   'result':pyanswer['seqnum']},  "")
                    print("ERROR: something went wrong with sequence numbers (this should not happen)")
                    return False
                pyanswer['name']=answer_name
                if 'details' in answer:
                    pydetails = []
                    for detail_name in answer['details']:
                        detail = answer['details'][detail_name]
                        pydetail = {}
                        pydetail['seqnum'] = detail['seqnum']
                        pydetail['name'] = detail_name
                        pydetail['success'] = detail['success']
                        pydetail['value'] = detail['value']
                        pydetail['max_points'] = detail['max_points']
                        pydetails.append(pydetail)
                    pydetails.sort(key=lambda x: x['seqnum'])
                    pyanswer['details']=pydetails
                pyresults.append(pyanswer)
                
            pyresults.sort(key=lambda x: x['seqnum'])
            #print(pyresults)
            
            return pyresults
        
        def getPartMaxPoints(self,n):
            runtime = self.getRuntime()
            if runtime is None:
                return False
            (success,weightFunc) = runtime.eval('part_'+str(n)+'_max_points')
            if not success:
                self.setError({'type':LuaErrorType.required_part_not_defined,
                               'number':n,
                               'function_name':'part_'+n+'_max_points'},
                              "")
                return False
            if weightFunc is None:
                result = 1
            else:
                try:
                    result = weightFunc()
                except LuaError as luaerr:
                    self.setError(parseLuaError(luaerr), 'part_'+str(n)+'_max_points()')
                    self.updateRuntime(runtime)
                    return False
            self.updateRuntime(runtime)
            return result
        
        def getPartExamleAnswers(self,n):
            runtime = self.getRuntime()
            if runtime is None:
                return False
            (success,exampleDictFunc) = runtime.eval('part_'+str(n)+'_example_answers')
            if not success:
                # The part_n_example_answers function is optional.  If we do not find it defined, we simply return an empty dictionary
                return dict()
            if exampleDictFunc is None:
                return dict()
            try:
                result = exampleDictFunc()
            except LuaError as luaerr:
                self.setError(parseLuaError(luaerr), 'part_'+str(n)+'_max_points')
                self.updateRuntime(runtime)
                return False
            self.updateRuntime(runtime)
            
            def pyDictFromLuaTable(lt):
                output = dict(lt)
                for k in output:
                    if lua_type(output[k])=='table':
                        output[k]=pyDictFromLuaTable(output[k])
                return output
            
            return pyDictFromLuaTable(result)
        
        def serialize(self):
            return json.dumps(self.__dict__)
        
        @staticmethod
        def createFromDump(dump):
            members = json.loads(dump)
            newLupaQuestion = LupaQuestion.__new__(LupaQuestion)
            for key in members:
                setattr(newLupaQuestion,key,members[key])
            return newLupaQuestion
        
# This class is intentionally outside the if because it does not actually depend on Lua.
# It is also not really a class.  It's a wrapper for creating a dictionary and manipulating it.
# This is done this way because the "object" needs to be easily serialized by Django and by making
# it as basic type rather than an object it will automatically be serialized correctly without any additional code.
class CodeSegment:
    system_lua = 6101
    raw_lua = 6102
    template_setup_code = 6103
    template_richtext = 6104
    template_expression = 6105
    template_code = 6106
        
    error_message = {
                        system_lua: "The error has occurred in the following code which comes with the OneUp system.  Generally, if you are not a developer of OneUp you should not see this message.",
                        raw_lua:"The error has occurred in the following Lua code you have provided.",
                        template_setup_code:"The error has occurred in the following code which was part of the setup code for your templated problem",
                        template_richtext:"The error has occurred in the following Lua code which is meant to display the rich text part of your templated problem.  In theory, you should never be seeing this error message, but if you are, you have somehow managed to create something which the system cannot print.",
                        template_expression:"The error has occurred in the following Lua expression which was included in your templated problem inside a [|  \] block.",
                        template_code:"The error has occurred in the following Lua code which was included as part of your templated problem inside a [{  }] block."
                    }
    
    type_description = {
                        system_lua: "OneUp System Code",
                        raw_lua: "Raw Lua code",
                        template_setup_code: "Template Set-up Code",
                        template_richtext: "Template Text",
                        template_expression: "Template Expression",
                        template_code: "Template Code"
                       }
        
    @staticmethod
    def new(type,code,original):
        new_code_seg = {}
        new_code_seg['type'] = type
        new_code_seg['code'] = code
        new_code_seg['original'] = original
        new_code_seg['num_new_lines'] = code.count("\n")
        new_code_seg['type_error'] = CodeSegment.error_message[type]
        new_code_seg['type_name'] = CodeSegment.type_description[type]
        return new_code_seg
    
