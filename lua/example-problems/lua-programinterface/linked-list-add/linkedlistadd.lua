tests = {
   {name="One empty list",command="java TestAdd test1", points=2},
   {name="A single element list",command="java TestAdd test2", points=2},  
   {name="Element added at end of list",command="java TestAdd test3", points=2}, 
   {name="Element added in middle of list",command="java TestAdd test4", points=2},
   {name="Element added to beginning of list",command="java TestAdd test5", points=2} 
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-add","LList.java","javac *.java",10,tests)
