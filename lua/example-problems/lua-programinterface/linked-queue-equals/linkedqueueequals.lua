tests = {
   {name="Both queues are empty",command="java TestEquals test1", points=1},
   {name="First queue empty, second with elements",command="java TestEquals test2", points=1},
   {name="First queue with elements, second queue empty",command="java TestEquals test3", points=1},
   {name="Two queues equal size but different elements",command="java TestEquals test4", points=2},
   {name="Two queues with different sizes : the first shorter",command="java TestEquals test5", points=2},
   {name="Two queues with different sizes : the first longer",command="java TestEquals test6", points=2},
   {name="Two equal queues",command="java TestEquals test7", points=3}
}
   

checker = programinterface.program_checker("/home/dichevad/workspace/oneUpNew/lua/example-problems/lua-programinterface/linked-queue-equals","LinkedQueue.java","javac *.java",12,tests)
