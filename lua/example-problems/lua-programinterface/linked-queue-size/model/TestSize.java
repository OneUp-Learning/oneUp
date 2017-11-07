public class TestSize{
	
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();
	
	public static void main(String[] args)
	{
		// Testing Part
		initQueue();
		
		    runTest1();
		
		    runTest2(); 
		
	    	runTest3();
	  
	}
	
	public static void initQueue() {
		
		queue1.clear();
		queue2.clear();
		queue3.clear();
		
		//One queue with no elements
		queue1.clear();
		
		//One queue with elements
		int[] a1 = {1,2,3,4,5};
		
		for(int i = 0; i < a1.length;i++)
		{
			queue2.enqueue(a1[i]);
		}
		//One queue with 4 elements
		
		int[] a2 = {1,2,3,4};
		
		for(int i = 0; i < a2.length;i++)
		{
			queue3.enqueue(a2[i]);
		}
	}
	
	public static void runTest1() {
		LinkedQueue<Integer> result = new LinkedQueue<Integer>();
		result.enqueue(queue1.size())
		if(result.dequeue().equals(0))
		{
			System.out.println("Success");
			System.out.println(3.34);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	public static void runTest2() {
		int result = queue2.size();
		if(result == 5)
		{
			System.out.println("Success");
			System.out.println(3.33);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	public static void runTest3() {
		int result = queue3.size();
		if(result == 4)
		{
			System.out.println("Success");
			System.out.println(3.33);
		}
		else {
			System.out.println("*** Failed test");
		}
	}
	
}