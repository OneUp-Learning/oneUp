tests = {

   {name="An empty list",command="java TestCycle test1", points=2},
   {name="A list with one element",command="java TestCycle test2", points=2},
   {name="A list with two elements",command="java TestCycle test3", points=3},
   {name="A list with multiple elements",command="java TestCycle test4", points=3}
   
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-cycle","LList.java","javac *.java",10,tests)
