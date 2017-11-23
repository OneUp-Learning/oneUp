
public class TestPeek {
	
	private static LinkedStack<Integer> stack1 = new LinkedStack<Integer>();
	private static LinkedStack<Integer> stack2 = new LinkedStack<Integer>();
	private static LinkedStack<Integer> stack3 = new LinkedStack<Integer>();
	
	
	
	public static void main(String[] args){
		
		initStacks();
		
		if("test1".equals(args[0])){
			runTest1();
		}
		
		else if ("test2".equals(args[0])){
			runTest2();
		}
		
		else {
			runTest3();
		}
		
		
	}
	
	public static void initStacks(){
		//Initializing
		stack1.clear();
		stack2.clear();
		stack3.clear();
		
		//One empty stack
		stack1.clear();
		
		
		//A stack with at least one element
		stack2.push(3);
		
		//A stack with multiple elements
		int[] a1 = {1,2,3,4,5};
		for (int i = 0; i < a1.length; i++)
		{
			stack3.push(a1[i]);
		}
		
	}
	
	//Checks an empty stack if it's empty
		//Peek should return null if empty
		public static void runTest1(){
			if(stack1.peek() == null && stack1.isEmpty()){
				System.out.println("Success");
	            System.out.println(3.34);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
		//Checks a stack with one element
		//Also checks if is empty after operation
		public static void runTest2(){
			if(stack2.peek() == 3 && !stack2.isEmpty()){
				System.out.println("Success");
	            System.out.println(3.33);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
		//Checks a stack with multiple elements
		//Also checks if it is empty
		public static void runTest3(){
			if(!stack3.isEmpty() && stack3.peek() == 5){
				System.out.println("Success");
	            System.out.println(3.33);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}

}
