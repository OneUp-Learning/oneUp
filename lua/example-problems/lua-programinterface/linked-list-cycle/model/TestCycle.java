public class TestCycle{
	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
		
	public static void main(String[] args) {
		//Initialize lists
		initlists();		

		if ("test1".equals(args[0])) {
			runTest1();
		} else if ("test2".equals(args[0])) {
			runTest2();
		} else if ("test3".equals(args[0])) {
			runTest3();
		} else {
			runTest4();
		}
	}
	
	public static void initlists(){
		//Initializing
		list1.clear();
		list2.clear();
		list3.clear();
		list4.clear();
		
		//An Empty list
		list1.clear();
		
		//A list with only one element
		list2.add(3);
		
		
		//A list with two elements
		list3.add(2);
		list3.add(4);
		
		//A list with 5 elements
		int[] a1 = {1,2,3,4,5};
		
		for (int i = 0; i < a1.length; i++)
		{
			list4.add(a1[i]);
		}
		
	}
	//Testing a list with no entries
	public static void runTest1(){
		list1.cycle();
		if(list1.isEmpty()){
			System.out.println("Success");
			System.out.println(2);
		}
	}
	//Testing a list with only one entry
	public static void runTest2(){
		list2.cycle();
		if(list2.getEntry(1) == 3){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}		
	}
	
	//Cycles a list with only two elements
	//Checks their positions
	public static void runTest3(){
		list3.cycle();
		if(list3.getEntry(1) == 4 && list3.getEntry(2) == 2){
			System.out.println("Success");
	        System.out.println(2);
	    }
	    else {
	        System.out.println("*** Failed test");
	    }
	}
	
	//Cycles a list with multiple elements
	//Checks positions of first and last elements
	public static void runTest4(){
		list4.cycle();
		if(list4.getEntry(1) == 2 && list4.getEntry(5) == 1){
			
			System.out.println("Success");
	        System.out.println(2);
	    }
	    else {
	        System.out.println("*** Failed test");
		}
	}
}