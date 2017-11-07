tests = {
   {name="Two empty lists",command="java TestLEquals test1", points=2},
   {name="One list empty, the other not",command="java TestLEquals test2", points=2},  
   {name="Two lists with non-matching elements",command="java TestLEquals test3", points=2}, 
   {name="Two lists with matching elements",command="java TestLEquals test4", points=2} 
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-list-equals","LList.java","javac *.java",8,tests)
