public class TestSplice{

	private static QueueInterface<Integer> queue1 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue2 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue3 = new LinkedQueue<Integer>();	
	private static QueueInterface<Integer> queue4 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue5 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue6 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue7 = new LinkedQueue<Integer>();
	private static QueueInterface<Integer> queue8 = new LinkedQueue<Integer>();
	
	public static void main(String[] args) 
	{
		initQueue();
		// Testing Part
		if ("test1".equals(args[0])) {
		    runTest1(queue2);
		} else if ("test2".equals(args[0])) {
		    runTest2(queue2);
		} else if ("test3".equals(args[0])) {
		    runTest3(queue2);
		} else {
		    runTest4(queue2);
		}
    }
 
	public static void initQueue() {
		//Two empty queues
		queue1.clear();
		queue2.clear();
		
		//Two queues with elements
		queue3.clear();
		queue4.clear();
		int[] a1 = {1, 2, 3, 4, 5};	
		int[] a2 = {6,7,8,9,10};
		for (int i = 0; i < a1.length; i++) {
			queue3.enqueue(a1[i]);
		}
		for (int i=0; i < a2.length; i++)
		{
			queue4.enqueue(a2[i]);
		}
		
		queue5.clear();
		int a3 = {1,2,3,4,5,6,7,8,9,10};
		for (int i = 0; i < a3.length; i++) {
	
			queue5.enqueue(a3[i]);
		}
		
	}	
    	// Trying two empty queues
   	public static void runTest1() {	
	       
        QueueInterface<Integer> result = queue1.splice(queue2); 
        if(result.equals(queue7)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	
   	//Trying first empty second not empty queues
   	public static void runTest2() {	
	       
        QueueInterface<Integer> result = queue1.splice(queue3); 
        if(result.equals(queue3)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	//Trying first not empty second empty
   	public static void runTest3() {	
	       
        QueueInterface<Integer> result = queue3.splice(queue1); 
        if(result.equals(queue3)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	//Trying both not empty
   	public static void runTest4() {	
	       
        QueueInterface<Integer> result = queue3.splice(queue4); 
        if(result.equals(queue5)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
    
    

		
   	
}