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

local concatFile = function(filename,text)
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
   function (text,rootdir,filename,commands,resultsFiles)
      local workingDirName = uniqid..'_'..seed..'_'..username
      makeWorkingDir(rootdir,workingDirName)
      cd(workingDirName)
      concatFile(filename,text)
      

return prograInterface
