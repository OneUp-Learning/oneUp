tests = {
   {name="One empty list",command="java TestContains test1", points=2},
   {name="A list with one element",command="java TestContains test2", points=2},  
   {name="A list with two elements",command="java TestContains test3", points=2}, 
   {name="A list with multiple elements",command="java TestContains test4", points=2},
   {name="A list without the desired element",command="java TestContains test5", points=2}
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-contains","LList.java","javac *.java",10,tests)
