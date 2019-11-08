ba = math.random(10)
bl = math.random(10)
ja = math.random(10)
jl = math.random(10)
if ba+ja == bl+jl then
   ba = ba + 1
end
part_1_text = function ()
    return 'If Bob has '..ba..' apples and '..bl..' limes and Jane has '..
       ja..' apples and '..jl..' limes and they put their fruit in a basket '..
       'togehter, how much of each fruit is in the basket? ' .. 
       make_input('total','string',30) .. 
       '<BR> of which fruit is there more? '.. make_input('more','string',10)
end
evaluate_answer_1 = function(answers)
   local results = {}
   local correct_more = "APPL"
   if (ba+ja < bl+jl) then
      correct_more = "LIME"
   end
   if (string.match(string.upper(answers.more),correct_more)) then
      results['more'] = {success=true,value=5}
   else
      results['more'] = {success=false,value=0}
   end
   getNumThing = function (s,thing) 
      return tonumber(string.match(string.match(string.upper(s),"%d+%s*"..string.upper(thing)),"%d+"))
   end
   local ansapple = getNumThing(answers.total,"appl")
   local anslime = getNumThing(answers.total,"lime")
   results.total = {}
   results.total.success = true
   results.total.value = 0
   results.total.details = {}
   if ansapple==ba+ja then
      results.total.details.apple = {success=true,value=5,max_points=5}
      results.total.value = results.total.value + 5
   else
      results.total.details.apple = {success=false,value=0,max_points=5}
      results.total.success = false
   end
   if anslime==bl+jl then
      results.total.details.lime = {success=true,value=5,max_points=5}
      results.total.value = results.total.value + 5
   else
      results.total.details.lime = {success=false,value=0,max_points=5}
      results.total.success = false
   end
   return results
end
part_1_max_points = function()
    return {total=10,more=5}
end
