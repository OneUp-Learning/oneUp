tests = {
   {name="Two empty lists",command="java TesttoString test1", points=2},
   {name="Two lists with the same elements",command="java TesttoString test2", points=2},  
   {name="Two lists with different elements",command="java TesttoString test3", points=2}, 
   {name="Two lists with different sizes",command="java TesttoString test4", points=2} 
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-list-string","LList.java","javac *.java",8,tests)
