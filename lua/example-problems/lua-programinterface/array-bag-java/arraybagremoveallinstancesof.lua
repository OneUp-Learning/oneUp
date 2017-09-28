tests = {
   {name="test1",command="java ArrayBag test1", points=5},
   {name="test2",command="java ArrayBag test1", points=5},
   {name="test3",command="java ArrayBag test1", points=5}   
}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/array-bag-java","ArrayBag.java","javac *.java",15,tests)
