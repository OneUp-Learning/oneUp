
public class TestPush {

	private static ArrayStack<Integer> stack1 = new ArrayStack<Integer>();
	private static ArrayStack<Integer> stack2 = new ArrayStack<Integer>();
	private static ArrayStack<Integer> stack3 = new ArrayStack<Integer>();

	public static void main(String[] args) {

		initStacks();

		if ("test1".equals(args[0])) {
			runTest1();
		}

		else if ("test2".equals(args[0])) {
			runTest2();
		}

		else {
			runTest3();
		}

	}

	public static void initStacks() {
		// Initializing
		stack1.clear();
		stack2.clear();
		stack3.clear();

		// One empty stack
		stack1.clear();

		// A stack with at least one element
		stack2.push(4);

		// A stack with multiple elements
		int[] a1 = { 1, 2, 3, 4, 5 };
		for (int i = 0; i < a1.length; i++) {
			stack3.push(a1[i]);
		}

	}

	// Checks an empty stack
	public static void runTest1() {
		stack1.push1(14);
		if (stack1.peek() == 14 && !stack1.isEmpty()) {
			System.out.println("Success");
			System.out.println(3.34);
		} else {
			System.out.println("*** Failed test");
		}
	}

	// Checks a stack with one element
	// Pops the added element and checks if empty to ensure
	// It didn't simply replace the first one
	public static void runTest2() {
		stack2.push1(13);
		if (stack2.pop() == 13 && !stack2.isEmpty()) {
			System.out.println("Success");
			System.out.println(3.33);
		} else {
			System.out.println("*** Failed test");
		}
	}

	// Checks a stack with multiple elements
	public static void runTest3() {
		stack3.push1(57);
		if (stack3.pop() == 57 && !stack3.isEmpty()) {
			System.out.println("Success");
			System.out.println(3.33);
		} else {
			System.out.println("*** Failed test");
		}
	}

}
