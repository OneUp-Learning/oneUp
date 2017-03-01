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

oneUp.exactEquality =
   function(a)
      return function(b,pts) 
	 if a==b then
	    return {success=true,value=pts}
	 else
	    return {success=false,value=0}
	 end
      end
   end

oneUp.exactEqualityWithPartialForClose =
   function(a,range,partialpts)
      local check = function(b,pts)
	 if a==b then
	    return {success=true,value=pts}
	 elseif math.abs(a-b) <= range then
	    return {success=false,value=partialpts}
	 else
	    return {success=false,value=0}
	 end
      end
      return check
   end

oneUp.approximateEquality =
   function(a,fudgefraction)
      local check = function(b,pts)
	 local diff = math.abs(a-b)
	 if diff/a<fudgeFraction then
	    return {success=true,value=pts}
	 else
	    return {success=false,value=0}
	 end
      end
   end

