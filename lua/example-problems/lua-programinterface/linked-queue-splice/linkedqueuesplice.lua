tests = {
   {name="Two empty queues",command="java TestSplice test1", points=2},
   {name="First queue empty, second queue not empty",command="java TestSplice test2", points=2},   
   {name="First queue not empty, second queue empty",command="java TestSplice test3", points=2},
   {name="Both queues not empty",command="java TestSplice test4", points=2}     
}
   
checker = programinterface.program_checker("/home/codepotato/workspacee/oneUp/lua/example-problems/lua-programinterface/linked-queue-splice","LinkedQueue.java","javac *.java",8,tests)
