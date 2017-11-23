
public class TestContains {
	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
	private static LList<Integer> list5 = new LList<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize lists
		initLists();
		
		if ("test1".equals(args[0])) {
			runTest1();
		} else if ("test2".equals(args[0])) {
			runTest2();
		} else if ("test3".equals(args[0])) {
			runTest3();
		} else if ("test4".equals(args[0])) {
			runTest4();
		} else {
			runTest5();
		}
	}
	
	public static void initLists(){
		//Initializing
		list1.clear();
		list2.clear();
		list3.clear();
		list4.clear();
		list5.clear();
				
		//One empty list
		list1.clear();
		
		//A list with only one element
		list2.add(17);
		
		//A list with two elements
		list3.add(27);
		list3.add(18);
		
		//A list with multiple elements
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			list4.add(a1[i]);
		}
		
		//Another list with multiple elements, but without
		//The desired number
		
		int[] a2 = {5,3,6,8,0,3};
		for(int i = 0; i < a2.length; i++){
			list5.add(a2[i]);
		}
	}
	//Checks an empty list for an element
			//Should return false
	public static void runTest1(){
		
		if (!list1.contains(1))
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a single element list
	//Should return true
	public static void runTest2(){
		
		if (list2.contains(17)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Checks a two element list
	//Should return true
	public static void runTest3(){
		
		if (list3.contains(18)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a list with multiple elements
	//Should return true
	public static void runTest4(){
		if (list4.contains(4)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a list with multiple elements for an element it doesn't have
	//Should return false
	public static void runTest5(){
		
		if (!list5.contains(37)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}		
	}	
}

