#module for builtsin for oneUp.

local oneUp = {}

oneUp.checkInputs =
function(inputsTable,checkerTable)
  results = {}
  for inputName,inputAnswer in pairs(inputsTable) do
    results[inputName] = checkerTable[inputName](inputAnswer)
  end
  return results
end

oneUp.exact_equality = function(a)
  return function(b,pts)
    if tonumber(a)==tonumber(b) then
      return {success=true,value=pts}
    else
      return {success=false,value=0}
    end
  end
end

oneUp.exact_equality_with_partial_credit_range = function(a,range,partialpts)
  return function(b,pts)
    a = tonumber(a)
    b = tonumber(b)
    if b==nil then
      return {success=false,value=0}
    end
    if a==b then
      return {success=true,value=pts}
    elseif math.abs(a-b) <= range then
      return {success=false,value=partialpts}
    else
      return {success=false,value=0}
    end
  end
end

oneUp.approximate_equality = function(a,fudgefraction)
  return function(b,pts)
    a = tonumber(a)
    b = tonumber(b)
    fudgefraction = tonumber(fudgefraction)
    if a == nil or b == nil or fudgefraction == nil then
      return {success=false,value=0}
    end
    local diff = math.abs(a-b)
    if diff/a<fudgefraction then
      return {success=true,value=pts}
    else
      return {success=false,value=0}
    end
  end
end

oneUp.word_list_equality = function(wl)
  return function(b,pts)
    local blist = {}
    while b ~= '' do
      local word = string.match(b,"[%a%d]*")
      table.insert(blist,word)
      b = string.sub(b,word:len()+1)
      local sep = string.match(b,"[^%a%d]*")
      b = string.sub(b,sep:len()+1)
    end
    if #wl ~= #blist then 
      return {success=false,value=0}
    else
      for i,v in ipairs(wl) do
        if string.upper(v) ~= string.upper(blist[i]) then
          return {success=false,value=0}
        end
      end
    end
    return {success=true,value=pts}
  end
end

oneUp.string_equality_ignore_spaces = function(str)
  return function(b,pts)
    if b == nil then
       return {success=false,value=0}
    end
    local str_no_space = str:gsub("%s*","")
    local b_no_space = b:gsub("%s*","")
    if string.upper(str_no_space) == string.upper(b_no_space) then
      return {success=true,value=pts}
    else
      return {success=false,value=0}
    end
  end
end

set_equality = function(wl)
  return function(b,pts)
     local make_failure_result_with_error = function(message,pts)
	local onedetail = {seqnum=1,success=false,value=0,max_points=pts}
	local details = {}
	details[message] = onedetail
	return {success=false,value=0, details=details}
     end
    b = string.gsub(b,"^%s*(.-)%s*$", "%1")
    if string.sub(b,1,1) ~= '{' or string.sub(b,#b) ~= '}' then
      name = "Used curly braces"
      return make_failure_result_with_error("Used curly braces",pts)
    end
    b = string.sub(b,2,#b-1)
    local blist = {}
    while b ~= '' do
      local superword = string.match(b,"^%s*[%a%d]+%s*,?%s*")
      local word = string.match(superword,"^%s*([%a%d]+)%s*,?%s*")
      local sep = string.match(superword,"^%s*[%a%d]+%s*(,?)%s*")
      table.insert(blist,word)
      b = string.sub(b,superword:len()+1)
      print("superword: "..superword..">end")
      print("word: "..word..">end")
      print("sep: "..sep..">end")
      print("b: "..b..">end")
      if sep ~= ',' and b ~= '' then
        return make_failure_result_with_error("Used commas properly",pts)
      end
    end
    if #wl ~= #blist then 
      return make_failure_result_with_error("Correct number of values",pts)
    else
      for i=1,#wl do
        local isGood=false
        for j=1,#wl do
        if string.upper(wl[i]) == string.upper(blist[j]) then
            isGood=true
        end
        end
        if not isGood then
          return make_failure_result_with_error("Matched values correctly",pts)
        end
      end
    end
    return {success=true,value=pts}
  end
end

-- Not yet sent to oneUp

local function charToAlphaIndex( chr )
  assert( type(chr)=="string", "bad argument #1 for 'index', number expected got "..type(chr))
  
  return function()
    local Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  
  if(not string.find(Alphabet, string.upper(chr)))then
    error"The expected argument is a letter of the alphabet."
  end
  
  return string.find(Alphabet, string.upper(chr))
  end
end

local function numToLetter( ind )
  assert( type(ind)=="number", "bad argument #1 for 'index', number expected got "..type(ind))
  
  return function()
    if(ind < 1)then
      ind = 1;
    elseif(ind>26)then
      ind = 26;
    end
    
    return string.upper(string.char(ind + 96)); -- any letter is located between n+96 & (n+(96+26)).
  end
end

local function replaceInString(String)
  return function(f1, f2, subFunc)
    local rtn = "";
    
    for i = 1,String:len() do
      local currentChar = string.sub(String, i, i)
      local newStr = f2(subFunc(f1(currentChar)))
      
      rtn = rtn .. newStr;
    end
  return rtn
  end
end

local function tableShift(t)
  return function(shiftAmt)
    if(shiftAmt > 0)then
      print("Going forwards.")
      for i = 1, shiftAmt do
        table.insert(t, 1, table.remove(t, #t))
      end
    else
      print("Going backwards.")
      for i = -1, shiftAmt, -1 do
        table.insert(t, #t, table.remove(t, 1))
      end
    end
  end
end
