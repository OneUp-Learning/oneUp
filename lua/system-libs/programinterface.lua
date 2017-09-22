local lfs = require "lfs"

local _debug_print = print

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

local programinterface = {}

uniqid = "UNIQID_GOES_HERE"
seed = 0
username = "USERNAME_GOES_HERE"

pathsep = package.config:sub(1,1)

programinterface.initialize =
   function(_uniqid,_seed,_username)
      uniqid = _uniqid
      seed = _seed
      username = _username
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

local cp = function(oldloc,newloc)
   if ostype == "Windows" then
      return os.execute('copy "'..oldloc..'" "'..newloc..'"') == 0
   else 
      return os.execute('cp "'..oldloc..'" "'..newloc..'"') == 0 
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
   lfs.chdir(rootDir)
   copydirectory(modelDir,newDir)
end

local concatFile = function(filename,text,workingDirName)
   local workingFileName = workingDirName..pathsep..filename
   cp(filename..".head",workingFileName)
   local outfile = io.open(workingFileName,"a")
   outfile:write(text)
   local tailfile = io.open(filename..".tail","r")
   tailfiletext = tailfile:read("*a")
   outfile:write(tailfiletext)
   outfile:close()
   tailfile:close()
end

programinterface.program_checker =
   function (rootdir,filename,compile_cmd,total_max_pts,tests)
      return function (text,pts)
	 local startDir = lfs.currentdir()
	 _debug_print(startDir)	 
	 local workingDirName = '/home/oneUpUserCodeSandbox/'..uniqid..'_'..seed..'_'..username
   makeWorkingDir(rootdir,"model",workingDirName)
   concatFile(filename,text,workingDirName)

   local clean_up_dir = function ()
      lfs.chdir(rootdir)
      killdir(workingDirName)
      

	 lfs.chdir(workingDirName)
   if pcall(function ()
      os.execute(compile_cmd)
   ) then 
   else
      
   end
	 local success = true
	 local value = 0
	 local ptsratio = pts/total_max_pts
	 local details = {}
	 for i,test in ipairs(tests) do
	    os.execute("pwd")
	    _debug_print(test['command'])
	    local outputFileHandle = io.popen('sudo -u oneUpUserCodeSandbox firejail --net=none --overlay-tmpfs --quiet '..test['command'],'r')
	    local firstLine = outputFileHandle:read("*l")
	    local pointsAwarded = outputFileHandle:read("*n")
	    outputFileHandle:close()
	    local testpoints = 0
	    local testsuccess = false
	    if string.match(string.upper(firstLine),"SUCCESS") ~= nil then
	       testpoints = pointsAwarded*ptsratio
	       value = value + testpoints
	       testsuccess = true
	    else
	       success = false
	    end
	    details[test['name']] =
	       {
		  value=testpoints,
		  max_points=test['points']*ptsratio,
		  success=testsuccess
	       }
	 end
	 lfs.chdir("..")
	 killdir(workingDirName)
	 lfs.chdir(startDir)
	 return {success=success,value=value,details=details}
      end
   end	 
		  
return programinterface
