
public class TestContains {
	private static LList<Integer> List1 = new LList<Integer>();
	private static LList<Integer> List2 = new LList<Integer>();
	private static LList<Integer> List3 = new LList<Integer>();
	private static LList<Integer> List4 = new LList<Integer>();
	private static LList<Integer> List5 = new LList<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize Lists
		initLists();
		
		runTest1();
		
		runTest2();
		
		runTest3();
		
		runTest4();
		
		runTest5();
		
		
	}
	
	public static void initLists(){
		//Initializing
		List1.clear();
		List2.clear();
		List3.clear();
		List4.clear();
		List5.clear();
		
		
		//One empty list
		List1.clear();
		
		//A list with only one element
		List2.add(17);
		
		//A list with two elements
		List3.add(27);
		List3.add(18);
		
		//A list with multiple elements
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			List4.add(a1[i]);
		}
		
		//Another list with multiple elements, but without
		//The desired number
		
		int[] a2 = {5,3,6,8,0,3};
		for(int i = 0; i < a2.length; i++){
			List5.add(a2[i]);
		}
	}
	
	public static void runTest1(){
		//Checks an empty list for an element
		//Should return false
		if (!List1.contains(1))
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest2(){
		//Checks a single element list
		//Should return true
		if (List2.contains(17)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	public static void runTest3(){
		//Checks a two element list
		//Should return true
		if (List3.contains(18)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest4(){
		//Checks a list with multiple elements
		//Should return true
		if (List4.contains(4)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest5(){
		//Checks a list with multiple elements for an element it doesn't have
		//Should return false
		if (!List5.contains(37)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	
	

}
