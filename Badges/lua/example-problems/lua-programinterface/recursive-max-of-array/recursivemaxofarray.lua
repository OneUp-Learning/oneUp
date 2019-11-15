tests = {
   {name="test1",command="java TestMaxArray test1", points=1},   
   {name="test2",command="java TestMaxArray test2", points=1},  
   {name="test3",command="java TestMaxArray test3", points=1},
   {name="test4",command="java TestMaxArray test4", points=1},
   {name="test5",command="java TestMaxArray test5", points=1},
   {name="test6",command="java TestMaxArray test6", points=1},
   {name="test7",command="java TestMaxArray test7", points=1},
   {name="test8",command="java TestMaxArray test8", points=1},
   {name="test9",command="java TestMaxArray test9", points=1},
   {name="test10",command="java TestMaxArray test10", points=1}     
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/recursive-max-of-array","RecursiveMaxOfArray.java","javac *.java",10,tests)
