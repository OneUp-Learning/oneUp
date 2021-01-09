--- Module for builtsin for oneUp
-- This file should be kept in sync with the code in Instructors/views/templateDynamicQuestionsView.py

local oneUp = {}

oneUp.checkInputs =
function(inputsTable,checkerTable)
  results = {}
  for inputName,inputAnswer in pairs(inputsTable) do
    results[inputName] = checkerTable[inputName](inputAnswer)
  end
  return results
end

--- Answer checker for exact equality.
-- This checker checks if the answer is exactly numeric equal to a given value.
-- If it is an exact match, it awards full points.
-- Otherwise, it awards 0.
-- It is recommended to use this checker with numeric equality of whole number
-- values, but not for strings or floating point values.
-- @tparam number a The answer
-- @usage exact_equality(5)
oneUp.exact_equality = function(a)
  return function(b,pts)
    if tonumber(a)==tonumber(b) then
      return {success=true,value=pts}
    else
      return {success=false,value=0}
    end
  end
end

--- Answer checker for approximate equality
-- Checks if an answer is approximately equal to another one.
-- If the student answer is within a given ratio of the correct answer
-- full points are awarded.
-- Otherwise, no point are awarded.
-- For example, if you want the student to be within 1% of the answer 79.28
-- you would use approximate_equality(79.28,0.01)
-- This checker is highly recommended for use with floating point values
-- to avoid small differences in rounding as binary floating point numbers
-- are rarely exactly the same as their decimal equivalents.
-- Note that the behavior of this answer checker means that if the correct answer is 0, the student must get it exactly.
--
-- If this is called with the arguments `(20,0.01)` any answer
-- greater than 19.8 and less than 20.2 would be counted as correct.
-- Exactly 19.8 and exactly 20.2 may or may not be considered correct
-- depending on the internal rounding of the floating point numbers.
-- Anything less than 19.8 or greater than 20.2 will not be considered correct.
--
-- @tparam number a The correct answer
-- @tparam number fudgefraction A ratio which expresses how close the student must be to the correct answer
-- @usage approximate_equality(20,0.01)
oneUp.approximate_equality = function(a,fudgefraction)
  a = tonumber(a)
  fudgefraction = tonumber(fudgefraction)
  return function(b,pts)
    b = tonumber(b)
    fudgefraction = tonumber(fudgefraction)
    if a == nil or b == nil or fudgefraction == nil then
      return {success=false,value=0}
    end
    if a == 0 then
       if b <= fudgefraction and b >= -fudgefraction then
	  return {success=true,value=pts}
       else
	  return {success=false,value=0}
    else
       local diff = math.abs((a-b)/a)
       if diff <= fudgefraction then
	  return {success=true,value=pts}
       else
	  return {success=false,value=0}
    end
  end
end

--- String equality answer checker which ignores spaces
-- This answer checker checks a student answer against a string but it
-- ignores any whitespace (before, after, or in the middle).
-- It is also case-insensitive.
--
-- If called with `"the answer"` as the correct answer, here are
-- some answers which would be marked correct
--
-- - `the answer`
-- - `The Answer`
-- - `theanswer`
-- - `  t H e   a N S w e   r   `
--
-- Here are some example answers which would be marked as incorrect
--
-- - `the answer!`
-- - `teh answer`
-- - `an answer`
--
-- @tparam string str The correct answer
-- @usage string_equality_ignore_spaces("the answer")
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

