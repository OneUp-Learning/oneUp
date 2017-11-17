tests = {
   {name="Both lists are empty",command="java TestLEquals test1", points=1},
   {name="First list empty, second with elements",command="java TestLEquals test2", points=1},
   {name="First list with elements, second list empty",command="java TestLEquals test3", points=1},
   {name="Two lists equal size but different elements",command="java TestLEquals test4", points=2},
   {name="Two lists with different sizes : the first shorter",command="java TestLEquals test5", points=2},
   {name="Two lists with different sizes : the first longer",command="java TestLEquals test6", points=2},
   {name="Two equal lists",command="java TestLEquals test7", points=3}

}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-list-equals","LList.java","javac *.java",12,tests)
