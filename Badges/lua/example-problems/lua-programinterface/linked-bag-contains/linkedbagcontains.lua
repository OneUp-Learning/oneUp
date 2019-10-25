tests = {
   {name="One empty bag",command="java TestContains test1", points=2},
   {name="A single element bag",command="java TestContains test2", points=2},  
   {name="A bag with two elements",command="java TestContains test3", points=2}, 
   {name="A bag with multiple elements",command="java TestContains test4", points=2},
   {name="A bag without the desired element",command="java TestContains test5", points=2} 
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-contains","LinkedBag.java","javac *.java",10,tests)
