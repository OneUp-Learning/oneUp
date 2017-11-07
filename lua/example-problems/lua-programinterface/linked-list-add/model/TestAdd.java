
public class TestAdd {
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
		
		//One Empty list
		List1.clear();
		
		//One list with only one element
		List2.add(2);
		
		//Lists with multiple elements
		//Element will be added at the end
		List3.clear();
		//Element will be added in the middle
		List4.clear();
		//Element will be added at the beginning
		List5.clear();
		
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			List3.add(a1[i]);
			List4.add(a1[i]);
			List5.add(a1[i]);
		}
	}
	public static void runTest1(){
		//Adds to an empty list
		List1.add1(1,1);
		if(List1.contains(1)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest2(){
		//Adds to a list with only one element
		List2.add1(3,2);
		if(List2.contains(3) && List2.getEntry(2) == 3){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest3(){
		//Adds element at the end of the list
		List3.add1(6, 6);
		if(List3.contains(6) && List3.getEntry(6) == 6){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest4(){
		//Adds element at the middle of the list
		List4.add1(3, 6);
		if(List4.contains(6) && List4.getEntry(3) == 6){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest5(){
		//Adds element at the beginning of the list
		List5.add1(1, 6);
		if(List5.contains(6) && List5.getEntry(1) == 6){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	

}
