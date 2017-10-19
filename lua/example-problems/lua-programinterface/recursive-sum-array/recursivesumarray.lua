tests = {
   {name="test1",command="java TestSumArray test1", points=2},
   {name="test2",command="java TestSumArray test2", points=2},   
   {name="test3",command="java TestSumArray test3", points=2},
   {name="test4",command="java TestSumArray test4", points=2},   
   {name="test5",command="java TestSumArray test5", points=2}   
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/recursive-sum-array","RecursiveSumArray.java","javac *.java",10,tests)
