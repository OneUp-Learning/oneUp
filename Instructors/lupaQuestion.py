import importlib
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
        def execute(self,code):
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
        def getPartWeight(self,n):
            return self.error_str
        def serialize(self):
            return self.error_str




else:
    # All good.  This is the part which should be run under normal circumstances.
    
    from lupa import LuaRuntime
    from lupa import LuaError
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
                "os":{"clock","difftime","time"}
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
                
        for lib in libs:
            libTable = lua.eval('require "'+lib+'"')
            setattr(sandbox,lib,libTable)
        
        setfenv = lua.eval("setfenv")
        setfenv(0, sandbox)
        return lua
    
    class LupaRuntimeLink:
        cache = {}
            
        def __init__(self,libs,seed,make=True):
            self.libs = libs
            self.seed = seed
            if make:
                self.uuid = str(uuid4())
                self.history = []
                self.runtime = sandboxLupaWithLibraries(libs,seed)
                #self.persistents = runtime.eval('{}')
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
                    'history':self.history
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
            link = LupaRuntimeLink(dictionary['libs'],int(dictionary['seed']),False)
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
            result = self.runtime.eval(code)
            self.history.append(('eval',code))
    #        self.persistents = runtime.eval('persistents')
            self.version += 1
            return result
        def execute(self,code):
            self.history.append(('execute',code))
            self.runtime.execute(code)
    #        self.persistents = runtime.eval('persistents')
            self.version += 1
    
        @staticmethod
        def clearCache_FOR_TESTING_ONLY():
            LupaRuntimeLink.cache = {}
            
        def removeFromCache(self):
            LupaRuntimeLink.cache[self.uuid] = None
    
    class LupaQuestion(object):
        
        def __init__(self,code,libs,seed,formid,numParts):
            self.code = code
            self.libs = libs
            self.seed = seed
            self.uniqid = formid
            self.numParts = numParts
            self.error = None
            runtime = LupaRuntimeLink(libs,seed)
            try:
                runtime.execute(code)
            except LuaError as e:
                error_mess = str(e)
                error_mess = re.sub(r'\[string "<python>"\]:','',error_mess)
                self.error = 'LuaError: '+error_mess
            runtime.execute('''\
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
            end
        end
    _current_part = 1
    _uniqid = nil
    _set_uniqid =
        function (v)
            _uniqid = v
        end
        
    make_input =
        function (name,t,s)
            _inputs[_current_part] = t
            local by_type = {
                ["int"] =
                    function ()
                        return '<input type="text" name="'.._uniqid..'_'..name..'">'
                    end
            }
            return by_type[t]()
        end
    
            ''')
            
            set_uniqid = runtime.eval('_set_uniqid')
            set_uniqid(self.uniqid)
            
            init_inputs = runtime.eval('_init_inputs')
            init_inputs(int(numParts))
            
            runtime.execute(code)
            self.lupaid = runtime.getIdentifier()
            self.lupadump = runtime.dump()
    
        def getRuntime(self):
            return LupaRuntimeLink.getLinkFromIdAndDump(self.lupaid, self.lupadump)
    
        def updateRuntime(self, runtime):
            self.lupaid = runtime.getIdentifier()
            self.lupadump = runtime.dump()
        
        def getQuestionPart(self,n):
            runtime = self.getRuntime()
            if runtime.eval('part_'+str(n)+'_text') is None:
                self.updateRuntime(runtime)
                return "No question part "+str(n)+" defined."
            runtime.execute('_output = ""')
            runtime.execute('_qtext = tostring(part_'+str(n)+'_text())')
            result = runtime.eval('_output .. _qtext')
            self.updateRuntime(runtime)
            return result
        
        def answerQuestionPart(self,n,answer_dict):
            runtime = self.getRuntime()
            evalAnswerFunc = runtime.eval('evaluate_answer_'+str(n)+'')
            if evalAnswerFunc is None:
                self.updateRuntime(runtime)
                return "No answer evaluator for part "+str(n)+" is defined."
            result = evalAnswerFunc(answer_dict)
            self.updateRuntime(runtime)
            return result
        
        def getPartWeight(self,n):
            runtime = self.getRuntime()
            weightFunc = runtime.eval('part_'+n+'_weight')
            if weightFunc is None:
                result = 1
            else:
                result = weightFunc()
            self.updateRuntime(runtime)
            return result
        
        def serialize(self):
            return json.dumps(self.__dict__)
        
        @staticmethod
        def createFromDump(dump):
            members = json.loads(dump)
            newLupaQuestion = LupaQuestion.__new__(LupaQuestion)
            for key in members:
                setattr(newLupaQuestion,key,members[key])
            return newLupaQuestion
        
        
        
        
