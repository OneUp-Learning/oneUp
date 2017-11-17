
public class TestLEquals {
	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
	private static LList<Integer> list5 = new LList<Integer>();
	private static LList<Integer> list6 = new LList<Integer>();
	private static LList<Integer> list7 = new LList<Integer>();
	private static LList<Integer> list8 = new LList<Integer>();
	private static LList<Integer> list9 = new LList<Integer>();
	private static LList<Integer> list10 = new LList<Integer>();
	private static LList<Integer> list11 = new LList<Integer>();
	private static LList<Integer> list12 = new LList<Integer>();
	private static LList<Integer> list13 = new LList<Integer>();
	private static LList<Integer> list14 = new LList<Integer>();
	
	public static void main(String[] args) {
		//Initialize lists
		initlists();
		
		if ("test1".equals(args[0])) {
			runTest1();
		} else if ("test2".equals(args[0])) {
			runTest2();
		} else if ("test3".equals(args[0])) {
			runTest3();
		} else if ("test4".equals(args[0])) {
			runTest4();
		} else if ("test5".equals(args[0])) {
			runTest5();
		} else if ("test6".equals(args[0])) {
			runTest6();
		} else {
			runTest7();
		}
	}
	
	public static void initlists() {
		//Initializing
		list1.clear();
		list2.clear();
		list3.clear();
		list4.clear();
		list5.clear();
		list6.clear();
		list7.clear();
		list8.clear();
		list9.clear();
		list10.clear();
		list11.clear();
		list12.clear();
		list13.clear();
		list14.clear();
		
		//Both lists empty
		list1.clear();
		list2.clear();
		
		//First list with elements, the other empty
		list3.clear();
		
		int[] a1 = {1,2,3,4,5};
		for (int i = 0; i < a1.length;i++)
		{
			list4.add(a1[i]);
		}
		
		//First list empty, other with elements
		list5.clear();
		for (int i = 0; i < a1.length; i++)
		{
			list6.add(a1[i]);
		}
		
		//Both lists with elements, not matching
		int[] a2 = {6,7,8,9,10};
		for (int i = 0; i < a1.length;i++)
		{
			list7.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			list8.add(a2[i]);
		}
		//Both lists with elements, matching
		for (int i = 0; i < a2.length;i++)
		{
			list9.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			list10.add(a1[i]);
		}
		//Both lists with elements, first one smaller
		int[] a3 = {1,2,3};
		for (int i = 0; i < a1.length; i++)
		{
			list11.add(a1[i]);
		}
		for (int i = 0; i < a3.length; i++)
		{
			list12.add(a3[i]);
		}
		//Both lists with elements, second one smaller
		for (int i = 0; i < a3.length; i++)
		{
			list13.add(a3[i]);
		}
		for (int i = 0; i < a1.length; i++)
		{
			list14.add(a1[i]);
		}
	}
	//Compares Two Empty lists
	public static void runTest1()
	{
		
		if(list1.equals(list2))
		{
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Compares two lists where the first is empty
	public static void runTest2()
	{
		if(!list3.equals(list4)){
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Compares two lists where the second one is empty
	public static void runTest3()
	{
		if(!list5.equals(list6)){
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Compares two lists equal size but different elements
	public static void runTest4()
	{ 
		if(!list7.equals(list8)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}

	//Compares two lists with the first being smaller
	public static void runTest5()
	{
		if(!list13.equals(list14)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}		
	}

	//Compares two lists with the first being bigger
	public static void runTest6()
	{
		if(!list11.equals(list12)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	
	//Compares two lists equal size, same elements
	public static void runTest7()
	{ 
		if(list9.equals(list10)){
			System.out.println("Success");
            System.out.println(3);
        }
        else {
            System.out.println("*** Failed test");
		}
	}	
}
		
		
				
		
	
	


