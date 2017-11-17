tests = {
   {name="One empty bag",command="java LinkedBag test1", points=3.34},
   {name="A bag with one element",command="java LinkedBag test2", points=3.33},  
   {name="A bag with multiple elements",command="java LinkedBag test3", points=3.33}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-reference","LinkedBag.java","javac *.java",10,tests)
