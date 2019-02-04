
public class TestPop {
	
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
	
	//Checks an empty stack
		//pop should be null if empty
		public static void runTest1(){
			
			if(stack1.pop() == null){
				System.out.println("Success");
	            System.out.println(3.34);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
		//Checks a stack with only one element
		//Stack should be empty after operation
		public static void runTest2(){
			
			if(stack2.pop() == 3 && stack2.isEmpty()){
				System.out.println("Success");
	            System.out.println(3.33);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
		//Checks a stack with multiple elements
		//Stack should not be empty after operation
		public static void runTest3(){
			if(stack3.pop() == 5 && !stack3.isEmpty()){
				System.out.println("Success");
	            System.out.println(3.33);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}

}
