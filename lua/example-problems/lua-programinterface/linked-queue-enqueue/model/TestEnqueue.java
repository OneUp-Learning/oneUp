public class TestEnqueue {
	private static QueueInterface<Integer> queue1 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue2 = new LinkedQueue<Integer>();
	
	public static void main (String[] args)
	{
		initQueue();
		//Testing Part
		if ("test1".equals(args[0])) {
			runTest1();
		}
		else {
			runTest2();
		}
	}
	public static void initQueue();
	{
	//Initializing
	queue1.clear();
	queue2.clear();
	
	//One queue that is empty
	queue1.clear();
	
	//One queue with elements
	int[] a1 = {1,2,3,4,5}
	
	for (int = 0; i < a1.length;i++)
	{
		queue2.enqueue(a1[i]);
	}
	
	}
	public static void runTest1() {
		
		queue1.enqueue(2);
		if (queue1.getFront() = 2)
		{
			System.out.println("Success");
            System.out.println(5);
        }
        else
            System.out.println("*** Failed test");
	}
	public static void runTest2() {
		
		queue2.enqueue(18);
		for (int i = 0; i < queue2.size(); i++)
		{
		if(queue2.dequeue() = 18)
			{
			System.out.println("Success");
            System.out.println(5);
            return "";
        	}
		}
        else
            System.out.println("*** Failed test");
		}
	}
}