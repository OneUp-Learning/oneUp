tests = {
   {name="Queue is empty",command="java TestSize test1", points=3.34},
   {name="Queue is not empty",command="java TestSize test2", points=3.33},   
   {name="Queue have 4 elements",command="java TestSize test3", points=3.33}

}
   
checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-queue-size","LinkedQueue.java","javac *.java",10,tests)
