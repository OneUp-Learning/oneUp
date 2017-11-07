public class TestEquals {
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue4 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue5 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue6 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue7 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue8 = new LinkedQueue<Integer>();
	
	public static void main (String[] args)
	{
		initQueue();
		//Testing Part
		
			runTest1();
		
			runTest2();
		
			runTest3();
		
			runTest4();
		
	}
	public static void initQueue() {
	//Initializing
	queue1.clear();
	queue2.clear();
	queue3.clear();
	queue4.clear();
	queue5.clear();
	queue6.clear();
	queue7.clear();
	queue8.clear();
	
	//Both queues empty
	queue1.clear();
	queue2.clear();
	
	//One queue empty, other with elements
	queue3.clear();
	
	int[] a1 = {1,2,3,4,5};
	for (int i = 0; i < a1.length;i++)
	{
		queue4.enqueue(a1[i]);
	}
	
	//Both queues with elements, not matching
	int[] a2 = {6,7,8,9,10};
	for (int i = 0; i < a1.length;i++)
	{
		queue5.enqueue(a1[i]);
	}
	for (int i = 0; i < a2.length;i++)
	{
		queue6.enqueue(a2[i]);
	}
	//Both queues with elements, matching
	for (int i = 0; i < a2.length;i++)
	{
		queue7.enqueue(a1[i]);
	}
	for (int i = 0; i < a2.length;i++)
	{
		queue8.enqueue(a1[i]);
	}
}
	public static void runTest1()
	{
		boolean result = queue1.equals(queue2);
		if(result == true)
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	public static void runTest2()
	{
		boolean result = queue3.equals(queue4);
		if(result == false)
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	public static void runTest3()
	{
		boolean result = queue5.equals(queue6);
		if(result == false)
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	public static void runTest4()
	{
		boolean result = queue7.equals(queue8);
		if(result == true)
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
}