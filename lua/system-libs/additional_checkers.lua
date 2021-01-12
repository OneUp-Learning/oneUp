--- Module for additional answer checkers for oneUp
-- 

local additional_checkers = {}

--- Answer checker for exact equality, but with some partial credit for being close.
-- This checker checks if the answer is exactly equal to a given value.
-- If it is an exact match, it awards full points.
-- If it is not an exact match, but is within the range of the correct answer, it awards ptsfrac of the points.  The amount awarded is calculated by multiplying the number of points the problem is worth by ptsfrac.
-- Otherwise, it awards 0.
--
-- If called with arguments, `(120,20,0.5)` and as part of a challenge where the
-- problem is assigned a value of 10 points if the students answers:
--
-- - **120** :  They will get 10 points
-- - **130** : They will get 5 points
-- - **110** : They will get 5 points
-- - **100** : They will get 5 points
-- - **99** : They will get 0 points
-- - **140** : They will get 5 points
-- - **141** : They will get 0 points
-- 
-- @tparam number a The correct answer
-- @tparam number range A number representing how close to the correct answer the student can be and still get partial credit.  This is calculated via simple subtraction and should represent the exact difference, not a ratio of any sort.
-- @tparam number ptsfrac What fraction of the points is awarded when the student receives partial credit.  This should always been greater than 0 and less than 1.
-- @usage additional_checkers.exact_equality_with_partial_credit_range(120,20,0.5)
additional_checkers.exact_equality_with_partial_credit_range = function(a,range,ptsfrac)
  a = tonumber(a)
  return function(b,pts)
    b = tonumber(b)
    if b==nil then
      return {success=false,value=0}
    end
    if a==b then
      return {success=true,value=pts}
    elseif math.abs(a-b) <= range then
      return {success=false,value=ptsfrac*pts}
    else
      return {success=false,value=0}
    end
  end
end

--- Word list equality answer checker.
-- This checks a list of words against a student answer list of words.
-- The lua representation is as a list of strings (i.e. an indexed lua
-- table containing strings) in a case-insensitive manner.
-- The student answer is expected to be a list of words where a word is
-- combination of letters and/or digits with either spaces or punctuation
-- between them.  It does not follow the syntax rules of programming languages
-- so underscores do break words apart.  The student may use any mix of
-- punctuation and whitespace to separate the words in the list.
-- Order is treated as important.  No partial credit is given.
-- 
-- If the function is called using `{'bob','sally','fido'}` as the correct
-- word list, here are some answers which will be marked correct
--
-- - 'bob sally fido'
-- - 'Bob, Sally, Fido '
-- - 'BOB;Sally;Fido'
-- - ' BOB:--:sally:=()       fido '
--
-- Here are some answers which will get no credit
--
-- - 'sally bob fido'
-- - 'b ob sally fido'
-- - 'bob saly fido'
-- 
-- @tparam table wl A list of words which is the correct answer 
-- @usage answer = {'bob','sally','fido'}
-- @usage additional_checkers.word_list_equality(answer)
additional_checkers.word_list_equality = function(wl)
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

--- Set Equality Answer Checker.
-- This answer checker is similar to the word list checker except that
-- it ignores order and it expects the student input to conform to set
-- notation, which is to say that it should be enclosed in curly braces
-- and that the entries should be separated with commas.
-- It returns errors with additional details if the curly braces or commas
-- are omitted.
-- It ignores case and any whitespace between the words and punctuation.
-- It expects each member of the set to be a combination of letters and
-- numbers.
--
-- If called with the correct answer `{'A','B','D'}` here are some answers which would be marked correct
-- 
-- - {A,B,D}
-- - {  A, B, D }
-- - {B,A,D}
-- - {D, B, A }
-- 
-- Here are some answers which would be marked incorrect
--
-- - {A,A,A,B,D}
-- - A,B,D
-- - (A,B,D)
-- - {A;B;D}
-- - {A B D}
--
-- @tparam table wl A list of words to be treated as a set which is the correct answer.
-- @usage answer = {'A','B','D'}
-- @usage additional_checkers.set_equality(answer)
additional_checkers.set_equality = function(wl)
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
--      print("superword: "..superword..">end")
--      print("word: "..word..">end")
--      print("sep: "..sep..">end")
--      print("b: "..b..">end")
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

return additional_checkers
