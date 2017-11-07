tests = {
   {name="List with two elements",command="java TestReverse test1", points=5},
   {name="A non-sequential list",command="java TestReverse test2", points=5}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-list-reverse","LList.java","javac *.java",10,tests)
