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

local getRandomBytes = function (n)
  rand = io.open('/dev/urandom','rb')
  local bytes = rand:read(n)
  rand:close()
  return bytes
end

local dirChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
local dirCharsLen = string.len(dirChars)

local getRandomDirName = function ()
  local bytes = getRandomBytes(20)
  local output = ""
  for i=1,20 do
    local charNum = string.byte(bytes,i) % dirCharsLen
    output = output .. dirChars:sub(charNum,charNum)
  end
  return output
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
  copydirectory(rootDir..pathsep..modelDir,newDir)
end

local concatFile = function(rootdir,filename,text,workingDirName)
  local workingFileName = workingDirName..pathsep..filename
  cp(rootdir..pathsep..filename..".head",workingFileName)
  local outfile = io.open(workingFileName,"a")
  outfile:write(text)
  local tailfile = io.open(rootdir..pathsep..filename..".tail","r")
  tailfiletext = tailfile:read("*a")
  outfile:write(tailfiletext)
  outfile:close()
  tailfile:close()
end

programinterface.program_checker =
function (rootdir,filename,compile_cmd,total_max_pts,tests)
  return function (text,pts) 
    local workingDirName = '/home/oneUpUserCodeSandbox/'..getRandomDirName()
    makeWorkingDir(rootdir,"model",workingDirName)
    concatFile(rootdir,filename,text,workingDirName)

    local result = 0
    result = os.execute('cd '..workingDirName..';'..compile_cmd)
    
    local success = true
    local value = 0
    local ptsratio = pts/total_max_pts
    local details = {}
    for i,test in ipairs(tests) do
      local outputFileHandle = io.popen('cd '..workingDirName..'; sudo -u oneUpUserCodeSandbox firejail --net=none --quiet '..test['command'],'r')
      local firstLine = outputFileHandle:read("*l")
      if firstLine == nil then
        firstLine = ""
      end
      local pointsAwarded = outputFileHandle:read("*n")
      if pointsAwarded == nil then
        pointsAwarded = 0
      end
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
    killdir(workingDirName)
    return {success=success,value=value,details=details}
  end
end	 

return programinterface
