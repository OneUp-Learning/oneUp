tests = {
   {name="test1",command="java ArrayBag test1", points=3},
   {name="test2",command="java ArrayBag test2", points=3},
   {name="test3",command="java ArrayBag test3", points=4}   
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/array-bag-java","ArrayBag.java","javac *.java",10,tests)
