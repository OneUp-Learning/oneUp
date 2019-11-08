tests = {
   {name="One empty stack",command="java TestPop test1", points=3.34},
   {name="A single element stack",command="java TestPop test2", points=3.33},  
   {name="A multiple element stack",command="java TestPop test3", points=3.33}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/array-stack-pop","ArrayStack.java","javac *.java",10,tests)
