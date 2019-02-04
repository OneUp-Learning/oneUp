tests = {
   {name="One empty stack",command="java TestPush test1", points=3.34},
   {name="A single element stack",command="java TestPush test2", points=3.33},  
   {name="A multiple element stack",command="java TestPush test3", points=3.33}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-stack-push","LinkedStack.java","javac *.java",10,tests)
