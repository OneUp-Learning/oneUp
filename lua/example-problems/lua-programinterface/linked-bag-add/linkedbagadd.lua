tests = {
   {name="One empty list",command="java TestAdd test1", points=3.34},
   {name="A single element list",command="java TestAdd test2", points=3.33},  
   {name="A list with multiple elements",command="java TestAdd test3", points=3.33}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-add","LinkedBag.java","javac *.java",10,tests)
