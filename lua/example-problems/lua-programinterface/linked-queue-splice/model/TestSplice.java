public class TestSplice{

	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();	
	private static LinkedQueue<Integer> queue4 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue5 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue6 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue7 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue8 = new LinkedQueue<Integer>();
	
	public static void main(String[] args) 
	{
		initQueue();
		// Testing Part

		    runTest1();

		    runTest2();

		    runTest3();

		    runTest4();

	}
 
	public static void initQueue() {
		//Two empty queues
		queue1.clear();
		queue2.clear();
		queue7.clear();
		
		//Two queues with elements
		int[] a1 = {1, 2, 3, 4, 5};	
		int[] a2 = {6,7,8,9,10};
		
		for (int i = 0; i < a1.length; i++) {
			queue3.enqueue(a1[i]);
		}
		
		for (int i=0; i < a2.length; i++) {
			queue4.enqueue(a2[i]);
		}

		for (int i = 0; i < a1.length; i++) {
			queue5.enqueue(a1[i]);
		}
		

		int[] a6 = {1,2,3,4,5,6,7,8,9,10};
		for (int i = 0; i < a6.length; i++) {	
			queue6.enqueue(a6[i]);
		}
		
	}	
    	// Trying two empty queues
   	public static void runTest1() {	
	       
   		LinkedQueue<Integer> result = queue1.splice(queue2); 
        if(result.equals(queue7)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	
   	//Trying first empty second not empty queues
   	public static void runTest2() {	
	       
   		LinkedQueue<Integer> result = queue1.splice(queue3); 
        if(result.equals(queue5)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	//Trying first not empty second empty
   	public static void runTest3() {	
	       
   		LinkedQueue<Integer> result = queue3.splice(queue1); 
        if(result.equals(queue5)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}
   	//Trying both not empty
   	public static void runTest4() {	
	       
   		LinkedQueue<Integer> result = queue3.splice(queue4); 
        if(result.equals(queue6)) {
            System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
   	}		   	
}