tests = {
   {name="Compares two empty bags",command="java TestEquals test1", points=1},
   {name="First bag empty, second one not",command="java TestEquals test2", points=1},  
   {name="First bag with elements, second bag empty",command="java TestEquals test3", points=1}, 
   {name="Two bags with different elements",command="java TestEquals test4", points=1},
   {name="Two bags with the same elements",command="java TestEquals test5", points=2},
   {name="Two bags where the first is bigger",command="java TestEquals test6", points=2},
   {name="Two bags where the second is bigger",command="java TestEquals test7", points=2} 
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-equals","LinkedBag.java","javac *.java",10,tests)
