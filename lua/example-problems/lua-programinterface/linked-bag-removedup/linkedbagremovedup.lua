tests = {
   {name="One empty bag",command="java TestRemoveDuplicate test1", points=2},
   {name="A bag with one element",command="java TestRemoveDuplicate test2", points=2},  
   {name="A bag with two of the same elements",command="java TestRemoveDuplicate test3", points=2}, 
   {name="A bag with no similar elements",command="java TestRemoveDuplicate test4", points=2},
   {name="A bag with multiple similar elements",command="java TestRemoveDuplicate test5", points=2} 
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-bag-removedup","LinkedBag.java","javac *.java",10,tests)
