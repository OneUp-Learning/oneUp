public class TestDequeue {
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();

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
	
	//One queue that is empty
	queue1.clear();
	
	//One queue with elements
	int[] a1 = {1,2,3,4,5};
	
	for (int i = 0; i < a1.length; i++)
	{
		queue2.enqueue(a1[i]);
	}
	int[] a2 = {2,3,4,5};
	
	for (int i = 0; i < a2.length; i++)
	{
		queue3.enqueue(a2[i]);
	}
	
	}
	public static void runTest1() {
		
		
		if (queue1.dequeue() == null)
		{
			System.out.println("Success");
            System.out.println(5);
        }
        else
            System.out.println("*** Failed test");
	}
	public static void runTest2() {
		
<<<<<<< HEAD
		
		if(queue2.dequeue() != null)
=======
		queue2.dequeue();
		if(queue2.equals(queue3))
>>>>>>> branch 'master' of /var/gitrepos/oneUp
		{
			System.out.println("Success");
            System.out.println(5);
        }
        else
            System.out.println("*** Failed test");
		}
	}