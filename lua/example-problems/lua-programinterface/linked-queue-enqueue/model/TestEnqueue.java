public class TestEnqueue {
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue4 = new LinkedQueue<Integer>();
	
	public static void main (String[] args)
	{
		initQueue();
		//Testing Part
		
			runTest1();
		
			runTest2();
		
	}
	public static void initQueue()
	{
	//Initializing
	queue1.clear();
	queue2.clear();
	queue3.clear();
<<<<<<< HEAD
=======
	queue4.clear();
>>>>>>> branch 'master' of /var/gitrepos/oneUp
	
	//One queue that is empty
	queue1.clear();
	
	//One queue with elements
	int[] a1 = {1,2,3,4,5};
	
	for (int i = 0; i < a1.length;i++)
	{
		queue2.enqueue(a1[i]);
	}
<<<<<<< HEAD
	//Comparison queue
	int[] a2 = {1,2,3,4,5,18};
	for (int i = 0; i < a2.length; i++)
	{
		queue3.enqueue(a2[i]);
	}
=======
	//First Comparison Queue
    queue4.enqueue(2);
    
	//Second Comparison queue
	int[] a2 = {1,2,3,4,5,18};
	for (int i = 0; i < a2.length; i++)
	{
		queue3.enqueue(a2[i]);
	}
	
	
>>>>>>> branch 'master' of /var/gitrepos/oneUp
	
	}
	public static void runTest1() {
		
<<<<<<< HEAD
		queue1.enqueue(2);
		if (!queue1.isEmpty())
=======
		queue1.enqueue1(2);
		if (queue1.equals(queue4))
>>>>>>> branch 'master' of /var/gitrepos/oneUp
		{
			System.out.println("Success");
            System.out.println(5);
        }
        else
            System.out.println("*** Failed test");
	}
	public static void runTest2() {
		
<<<<<<< HEAD
		queue2.enqueue(18);
		if(queue2.size() == queue3.size())
=======
		queue2.enqueue1(18);
		if(queue2.equals(queue3))
>>>>>>> branch 'master' of /var/gitrepos/oneUp
			{
			System.out.println("Success");
            System.out.println(5);
            
        	}
		
        else {
            System.out.println("*** Failed test");
		}
	}
}