
public class TestLEquals {
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
	public static void initLists() {
		//Initializing
		List1.clear();
		List2.clear();
		List3.clear();
		List4.clear();
		List5.clear();
		List6.clear();
		List7.clear();
		List8.clear();
		
		//Both Lists empty
		List1.clear();
		List2.clear();
		
		//One List empty, other with elements
		List3.clear();
		
		int[] a1 = {1,2,3,4,5};
		for (int i = 0; i < a1.length;i++)
		{
			List4.add(a1[i]);
		}
		
		//Both Lists with elements, not matching
		int[] a2 = {6,7,8,9,10};
		for (int i = 0; i < a1.length;i++)
		{
			List5.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			List6.add(a2[i]);
		}
		//Both Lists with elements, matching
		for (int i = 0; i < a2.length;i++)
		{
			List7.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			List8.add(a1[i]);
		}
	}
	
	public static void runTest1()
	{//Compares Two Empty Lists
		
		if(List1.equals(List2))
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	
	public static void runTest2()
	{//Compares one empty list, another with elements
		if(!List3.equals(List4)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	
	public static void runTest3()
	{ //Compares two lists with different elements
		if(!List5.equals(List6)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	public static void runTest4()
	{ //Compares two lists with the same elements
		if(List7.equals(List8)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		}
}
		
				
		
	
	


