public class TestSize{
	
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();
	
	public static void main(String[] args)
	{
		// Testing Part
		initQueue();
		if ("test1".equals(args[0])) {
		    runTest1();
		} else if ("test2".equals(args[0])){
		    runTest2(); 
		}
		else {
	    	runTest3();
	    }
	}
	
	public static void initQueue() {
		
		queue1.clear();
		queue2.clear();
		queue3.clear();
		
		//One queue with no elements
		queue1.clear();
		
		//One queue with  1 element
		int[] a1 = {1};
		
		for(int i = 0; i < a1.length;i++)
		{
			queue2.enqueue(a1[i]);
		}
		//One queue with 5 elements
		
		int[] a2 = {1,2,3,4,5};
		
		for(int i = 0; i < a2.length;i++)
		{
			queue3.enqueue(a2[i]);
		}
	}
	// empty queue
	public static void runTest1() {
		int result = queue1.size();
		if(queue1.size() == 0)
		{
			System.out.println("Success");
			System.out.println(3.34);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	
	// queue with 1 element
	public static void runTest2() {
		if(queue2.size() == 1)
		{
			System.out.println("Success");
			System.out.println(3.33);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	// queue with 5 elements
	public static void runTest3() {
		if(queue3.size() == 5)
		{
			System.out.println("Success");
			System.out.println(3.33);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	
}