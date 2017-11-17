
public class TestContains {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag5 = new LinkedBag<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize bags
		initBags();
		
		if ("test1".equals(args[0])) {
            runTest1();
		}
	 	else if ("test2".equals(args[0])) {
           runTest2();
	 	}
	 	else if ("test3".equals(args[0])) {
            runTest3();
	 	}
		else if ("test4".equals(args[0])) {
            runTest4();
		}
		else {
			runTest5();
		}
		
		
	}
	
	public static void initBags(){
		//Initializing
		bag1.clear();
		bag2.clear();
		bag3.clear();
		bag4.clear();
		bag5.clear();
		
		
		//One empty bag
		bag1.clear();
		
		//A bag with only one element
		bag2.add(17);
		
		//A bag with two elements
		bag3.add(27);
		bag3.add(18);
		
		//A bag with multiple elements
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			bag4.add(a1[i]);
		}
		
		//Another bag with multiple elements, but without
		//The desired number
		
		int[] a2 = {5,3,6,8,0,3};
		for(int i = 0; i < a2.length; i++){
			bag5.add(a2[i]);
		}
	}
	//Checks an empty bag for an element
	//Should return false
	public static void runTest1(){
		
		if (!bag1.contains(1))
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a single element bag
	//Should return true
	public static void runTest2(){
		
		if (bag2.contains(17)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Checks a two element bag
	//Should return true
	public static void runTest3(){
		
		if (bag3.contains(18)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a bag with multiple elements
	//Should return true
	public static void runTest4(){
		if (bag4.contains(4)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a bag with multiple elements for an element it doesn't have
	//Should return false
	public static void runTest5(){
		
		if (!bag5.contains(37)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	
	

}
