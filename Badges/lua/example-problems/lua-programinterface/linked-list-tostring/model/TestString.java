
public class TestString {
	private static LList<Integer> List1 = new LList<Integer>();
	private static LList<Integer> List2 = new LList<Integer>();
	private static LList<Integer> List3 = new LList<Integer>();
	private static LList<Integer> List4 = new LList<Integer>();
	private static LList<Integer> List5 = new LList<Integer>();
	private static LList<Integer> List6 = new LList<Integer>();
	private static LList<Integer> List7 = new LList<Integer>();
	private static LList<Integer> List8 = new LList<Integer>();
	
	public static void main(String[] args) {
		//Initialize Lists
		initLists();
		
		runTest1();
		
		runTest2();
		
		runTest3();
		
		runTest4();
		
	}
	public static void initLists(){
		//Initializing
		List1.clear();
		List2.clear();
		List3.clear();
		List4.clear();
		List5.clear();
		List6.clear();
		List7.clear();
		List8.clear();
		
		//Two empty Lists
		List1.clear();
		List2.clear();
		
		
		//Two lists with the same elements and size
		
		int[] a1 = {1,2,3,4,5,6};
		
		for (int i = 0; i < a1.length; i++){
			List3.add(a1[i]);
			List4.add(a1[i]);
		}
		//Two lists with different elements, but same size
		int[] a2 = {6,7,8,9,0,1};
		for (int i = 0; i < a2.length; i++){
			List5.add(a1[i]);
			List6.add(a2[i]);
		}
		
		//Two list with different sizes
		List7.add(1);
		List7.add(2);
		
		List8.add(1);
		List8.add(2);
		List8.add(3);
	}
	public static void runTest1(){
		//Compares two toString() methods of empty lists
		if(List1.toString().equals(List2.toString())){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest2(){
		//Compares two toString() methods of lists with the same elements
		if(List3.toString().equals(List4.toString())){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	
	public static void runTest3(){
		//Compares two toString() methods of lists with different elements
		if(!List5.toString().equals(List6.toString())){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest4(){
		//Compares two toString() methods of lists with different sizes
		if(!List7.toString().equals(List8.toString())){
			System.out.println("Success");
			System.out.println(2);
		}
		else{
			System.out.println("*** Failed test");
		}
	}

}
