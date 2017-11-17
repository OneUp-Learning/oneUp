tests = {
   {name="One empty bag",command="java TestDuplicateAll test1", points=2},
   {name="A single element bag",command="java TestDuplicateAll test2", points=2},  
   {name="A bag with a few elements",command="java TestDuplicateAll test3", points=2}, 
   {name="A bag with non-sequential elements",command="java TestDuplicateAll test4", points=2}
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-bag-duplicate","LinkedBag.java","javac *.java",8,tests)
