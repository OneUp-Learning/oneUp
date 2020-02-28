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

local function replaceInString(String) --> to Index then substitute, then to Letter
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
      for i = 1, shiftAmt do
        table.insert(t, 1, table.remove(t, #t))
      end
    else
      for i = -1, shiftAmt, -1 do
        table.insert(t, #t, table.remove(t, 1))
      end
    end
  end
end