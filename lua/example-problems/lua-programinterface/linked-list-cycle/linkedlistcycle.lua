tests = {
   {name="A list with two elements",command="java TestCycle test1", points=5},
   {name="A list with five elements",command="java TestCycle test2", points=5}
   
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-list-cycle","LList.java","javac *.java",10,tests)
