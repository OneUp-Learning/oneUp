tests = {
   {name="Queue is empty",command="java TestEnqueue test1", points=5},
   {name="Queue is not empty",command="java TestEnqueue test2", points=5}  
  

}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-queue-enqueue","LinkedQueue.java","javac *.java",10,tests)
