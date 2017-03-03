local binaryFormat = package.cpath:match("%p[\\|/]?%p(%a+)")
if binaryForamt == "dll" then
   ostype = "Windows"
elseif binaryFormat == "so" then
   ostype = "Unix"
elseif binaryFormat == "dylib" then
   ostype = "MaxOS"
else
   ostype = "unknown"
end

local programInterface = {}

uniqid = "UNIQID_GOES_HERE"
seed = 0
username = "USERNAME_GOES_HERE"

pathsep = package.config[0]

programInterface.initialize =
   function(_uniqid,_seed,_username)
      uniqid = _uniqid
      seed = _seed
   end

local cd = function(dir)
   return os.execute('cd "'..dir..'"') == 0
end

local makeDir = function(dir)
   return os.execute("mkdir "..dir) == 0
end

local copydirectory = function(oldloc,newloc)
   if ostype == "Windows" then
      return os.execute('xcopy "'..oldloc..'" "'..newloc..'"') == 0
   else 
      return os.execute('cp -r "'..oldloc..'" "'..newloc..'"') == 0 
   end
end

local killdir = function(dir)
   if ostype == "Windows" then
      return os.execute('rmdir /s "'..dir..'"') == 0
   else
      return os.execute('rm -rf "'..dir..'"') == 0
   end
end

local makeWorkingDir = function(rootDir,modelDir,newDir)
   if not cd(rootDir) then
      return false,"Error changing directories"
   elseif not copydirectory(modelDir,newDir) then
      return false,"Error creating working directory"
   else
      return true,"Working directory created."
   end
end

local concatFile = function(filename,text,workingDirName)
   cp(filename..".head",filename)
   local outfile = io.open(filename,"a")
   outfile:write(text)
   local tailfile = io.open(filename..".tail","r")
   tailfiletext = tailfile:read(*a)
   outfile:write(tailfiletext)
   outfile:close()
   tailfile:close()
end

programInterface.programChecker =
   function (rootdir,filename,total_max_pts,tests)
      return function (text,pts)
	 local workingDirName = uniqid..'_'..seed..'_'..username
	 makeWorkingDir(rootdir,workingDirName)
	 concatFile(filename,text,workingDirName)
	 local success = true
	 local value = 0
	 local ptsratio = total_max_pts/pts
	 local detail = {}
	 for test in tests do
	    local outputFileHandle = io.popen(test['command'],'r')
	    local firstLine = outputFileHandle:read("*l")
	    local testpoints = 0
	    local testsuccess = false
	    if str.match(string.upper(firstLine),"SUCCESS") ~= nil then
	       testpoints = test['points']*ptsratio
	       value = value + testpoints
	       testsuccess = true
	    else
	       success = false
	    end
	    detail[test['name']] =
	       {
		  name=test[name],
		  points=testpoints,
		  max_points=test['points']*ptsratio
		  success=testsuccess
	       }
	 end
	 return {success=success,value=value,detail=detail}
      end
   end	 
		  
return programInterface
