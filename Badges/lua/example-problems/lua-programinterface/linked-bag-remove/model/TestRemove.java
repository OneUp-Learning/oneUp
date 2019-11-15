
public class TestRemove {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	
	public static void main(String[] args)
	{
		initBags();
		
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
	
	public static void initBags()
	{
		//Initializing
		bag1.clear();
		bag2.clear();
		bag3.clear();
		
		//An empty bag
		bag1.clear();
		
		//A bag with only one element
		bag2.add(7);
		
		//A bag with multiple elements
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++)
		{
			bag3.add(a1[i]);
		}
		
		
	}
	//Checks a bag that is empty
	public static void runTest1()
	{
		
		if(bag1.isEmpty() && bag1.remove() == null)
		{
			System.out.println("Success");
            System.out.println(3.34);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Checks a bag with only one element
	//Also checks if the bag is empty afterwords
	public static void runTest2()
	{
		if(bag2.remove() != null && bag2.isEmpty())
		{
			System.out.println("Success");
            System.out.println(3.33);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Checks a bag with multiple elements
	//Also checks if the size is reduced
	public static void runTest3()
	{
		if(bag3.remove() != null && bag3.getCurrentSize() == 4)
		{
			System.out.println("Success");
            System.out.println(3.33);
        }
        else {
            System.out.println("*** Failed test");
        }
	}

}
