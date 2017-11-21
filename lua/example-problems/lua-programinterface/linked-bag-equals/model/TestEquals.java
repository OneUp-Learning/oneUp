
public class TestEquals {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag5 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag6 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag7 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag8 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag9 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag10 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag11 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag12 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag13 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag14 = new LinkedBag<Integer>();
	
	public static void main(String[] args) {
		//Initialize bags
		initbags();
		
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
	public static void initbags() {
		//Initializing
		bag1.clear();
		bag2.clear();
		bag3.clear();
		bag4.clear();
		bag5.clear();
		bag6.clear();
		bag7.clear();
		bag8.clear();
		bag9.clear();
		bag10.clear();
		bag11.clear();
		bag12.clear();
		bag13.clear();
		bag14.clear();
		
		//Both bags empty
		bag1.clear();
		bag2.clear();
		
		//First bag with elements, the other empty
		bag3.clear();
		
		int[] a1 = {1,2,3,4,5};
		for (int i = 0; i < a1.length;i++)
		{
			bag4.add(a1[i]);
		}
		
		//First bag empty, other with elements
		bag5.clear();
		for (int i = 0; i < a1.length; i++)
		{
			bag6.add(a1[i]);
		}
		
		//Both bags with elements, not matching
		int[] a2 = {6,7,8,9,10};
		for (int i = 0; i < a1.length;i++)
		{
			bag7.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			bag8.add(a2[i]);
		}
		//Both bags with elements, matching
		for (int i = 0; i < a2.length;i++)
		{
			bag9.add(a1[i]);
		}
		for (int i = 0; i < a2.length;i++)
		{
			bag10.add(a1[i]);
		}
		//Both bags with elements, first one smaller
		int[] a3 = {1,2,3};
		for (int i = 0; i < a1.length; i++)
		{
			bag11.add(a1[i]);
		}
		for (int i = 0; i < a3.length; i++)
		{
			bag12.add(a3[i]);
		}
		//Both bags with elements, second one smaller
		for (int i = 0; i < a3.length; i++)
		{
			bag13.add(a3[i]);
		}
		for (int i = 0; i < a1.length; i++)
		{
			bag14.add(a1[i]);
		}
	}
	//Compares Two Empty bags
	public static void runTest1()
	{
		
		if(bag1.equals(bag2))
		{
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Compares two bags where the first is empty
	public static void runTest2()
	{
		if(!bag3.equals(bag4)){
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Compares two bags where the second one is empty
	public static void runTest3()
	{
		if(!bag5.equals(bag6)){
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Compares two bags with different elements
	public static void runTest4()
	{ 
		if(!bag7.equals(bag8)){
			System.out.println("Success");
            System.out.println(1);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Compares two bags with the same elements
	public static void runTest5()
	{ 
		if(bag9.equals(bag10)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Compares two bags with the first being bigger
	public static void runTest6()
	{
		if(!bag11.equals(bag12)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Compares two bags with the first being smaller
	public static void runTest7()
	{
		if(!bag13.equals(bag14)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
}
		
				
		
	
	


