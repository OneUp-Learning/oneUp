tests = {
   {name="One empty list",command="java TestRemove test1", points=3.34},
   {name="A single element list",command="java TestRemove test2", points=3.33},  
   {name="Element added at end of list",command="java TestRemove test3", points=3.33}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-remove","LinkedBag.java","javac *.java",10,tests)
