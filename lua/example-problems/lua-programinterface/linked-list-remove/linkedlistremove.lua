tests = {
   {name="One empty list",command="java TestRemove test1", points=2},
   {name="A list with only one element",command="java TestRemove test2", points=2},
   {name="Removing the first element of a list",command="java TestRemove test3", points=2},  
   {name="Removing an element from the middle",command="java TestRemove test3", points=2},  
   {name="Removing the last element of a list",command="java TestRemove test3", points=2}  

}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-remove","LList.java","javac *.java",10,tests)
