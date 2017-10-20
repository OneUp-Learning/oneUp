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
        if v ~= blist[i] then
          return {success=false,value=0}
        end
      end
    end
    return {success=true,value=pts}
  end
end

oneUp.string_equality_ignore_spaces = function(str)
  return function(b,pts)
    local str_no_space = str:gsub("%s*","")
    local b_no_space = b:gsub("%s*","")
    if str_no_space == b_no_space then
      return {success=true,value=pts}
    else
      return {success=false,value=0}
    end
  end
end

