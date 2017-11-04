tests = {
   {name="Testing with an empty list",command="java TestReverse test1", points=2},
   {name="Testing with a list with only one element",command="java TestReverse test2", points=2},
   {name="Testing with a list with two elements",command="java TestReverse test3", points=3},
   {name="Testing with a list with multiple elements",command="java TestReverse test4", points=3}

}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-reverse","LList.java","javac *.java",10,tests)
