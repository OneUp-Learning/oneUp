public class TestEquals {
	private static LinkedQueue<Integer> queue1 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue2 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue3 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue4 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue5 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue6 = new LinkedQueue<Integer>();
	private static LinkedQueue<Integer> queue7 = new LinkedQueue<Integer>();
<<<<<<< HEAD
	private static LinkedQueue<Integer> queue8 = new LinkedQueue<Integer>();
	
	public static void main (String[] args)
	{
=======

	public static void main(String[] args) {
>>>>>>> branch 'master' of /var/gitrepos/oneUp
		initQueue();
<<<<<<< HEAD
		//Testing Part
		
=======
		// Testing Part
		if ("test1".equals(args[0])) {
>>>>>>> branch 'master' of /var/gitrepos/oneUp
			runTest1();
<<<<<<< HEAD
		
=======
		} else if ("test2".equals(args[0])) {
>>>>>>> branch 'master' of /var/gitrepos/oneUp
			runTest2();
<<<<<<< HEAD
		
=======
		} else if ("test3".equals(args[0])) {
>>>>>>> branch 'master' of /var/gitrepos/oneUp
			runTest3();
<<<<<<< HEAD
		
=======
		} else if ("test4".equals(args[0])) {
>>>>>>> branch 'master' of /var/gitrepos/oneUp
			runTest4();
<<<<<<< HEAD
		
=======
		} else if ("test5".equals(args[0])) {
			runTest5();
		} else if ("test6".equals(args[0])) {
			runTest6();
		} else {
			runTest7();
		}
>>>>>>> branch 'master' of /var/gitrepos/oneUp
	}
<<<<<<< HEAD
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
=======

	public static void initQueue() {
		// Initializing
		queue1.clear();
		queue2.clear();
		queue3.clear();
		queue4.clear();
		queue5.clear();
		queue6.clear();
		queue7.clear();

		// A queue with 5 elements: queue4
		int[] a1 = { 1, 2, 3, 4, 5 };
		for (int i = 0; i < a1.length; i++) {
			queue4.enqueue(a1[i]);
		}

		// Another queue with the same 5 elements: queue5
		for (int i = 0; i < a1.length; i++) {
			queue5.enqueue(a1[i]);
		}

		// Another queue with 5 but different elements: queue6
		int[] a2 = { 6, 7, 8, 9, 10 };
		for (int i = 0; i < a2.length; i++) {
			queue6.enqueue(a2[i]);
		}

		// A queues with 7 elements: queue7
		int[] a7 = { 1, 2, 3, 4, 5 , 6, 7};
		for (int i = 0; i < a7.length; i++) {
			queue7.enqueue(a7[i]);
		}

>>>>>>> branch 'master' of /var/gitrepos/oneUp
	}

	// Both queues empty
	public static void runTest1() {
		boolean result = queue1.equals(queue2);
		if(result) {
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
	}

	// First queue empty, second with elements
	public static void runTest2() {
		boolean result = queue3.equals(queue4);
		if (!result) {
			System.out.println("Success");
<<<<<<< HEAD
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
=======
			System.out.println(1);
		} else
			System.out.println("*** Failed test");
>>>>>>> branch 'master' of /var/gitrepos/oneUp
	}

	// First queue with elements, second queue empty
	public static void runTest3() {
		boolean result = queue4.equals(queue3);
		if (!result) {
			System.out.println("Success");
<<<<<<< HEAD
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
=======
			System.out.println(1);
		} else
			System.out.println("*** Failed test");
>>>>>>> branch 'master' of /var/gitrepos/oneUp
	}

	// Two queues equal size but different elements
	public static void runTest4() {
		boolean result = queue4.equals(queue6);
		if (!result) {
			System.out.println("Success");
<<<<<<< HEAD
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
=======
			System.out.println(2);
		} else
			System.out.println("*** Failed test");
	}

	// Two queues with different sizes : the first shorter
	public static void runTest5() {
		boolean result = queue4.equals(queue7);
		if (!result) {
			System.out.println("Success");
			System.out.println(1);
		} else
			System.out.println("*** Failed test");
	}
	
	// Two queues with different sizes : the first longer
	public static void runTest6() {
		boolean result = queue7.equals(queue4);
		if (!result) {
			System.out.println("Success");
			System.out.println(1);
		} else
			System.out.println("*** Failed test");
	}
	
	// Two equal queues 
	public static void runTest7() {
		boolean result = queue4.equals(queue5);
		if (result) {
			System.out.println("Success");
			System.out.println(3);
		} else
			System.out.println("*** Failed test");
	}
	
>>>>>>> branch 'master' of /var/gitrepos/oneUp
}