tests = {
   {name="Queue is empty",command="java TestDequeue test1", points=5},
   {name="Queue is not empty",command="java TestDequeue test2", points=5}  
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-queue-dequeue","LinkedQueue","javac *.java",10,tests)
