tests = {
   {name="One empty bag",command="java TestFrequency test1", points=2},
   {name="A bag with one element",command="java TestFrequency test2", points=2},  
   {name="A bag with a few elements",command="java TestFrequency test3", points=3}, 
   {name="A bag with elements, but not the desired one",command="java TestFrequency test4", points=3}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-frequency","LinkedBag.java","javac *.java",10,tests)
