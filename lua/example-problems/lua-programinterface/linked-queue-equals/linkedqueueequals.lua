tests = {
   {name="Both queues are empty",command="java TestEquals test1", points=2}
   {name="One queue empty, the other not",command="java TestEquals test2", points=2}
   {name="Both queues have elements, but different",command="java TestEquals test3", points=2}
   {name="Both queues have same elements",command="java TestEquals test4", points=2}

}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-queue-equals","LinkedQueue.java","javac *.java",8,tests)
