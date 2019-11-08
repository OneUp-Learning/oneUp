
public class TestRemoveDuplicate {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag5 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag6 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag7 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag8 = new LinkedBag<Integer>();
	
	public static void main(String[] args)
	{
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
		bag6.clear();
		bag7.clear();
		bag8.clear();
		
		//An empty bag
		bag1.clear();
		
		//A bag with only one element
		bag2.add(3);
		//Bag to compare with bag2
		bag3.add(3);
		
		//A bag with two of the same elements
		bag4.add(4);
		bag4.add(4);
		//Bag to compare with bag4
		bag5.add(4);
		
		//A bag with variety of dissimilar elements
		//With bag7 as a comparison bag
		int[] b1 = {1,2,3,4,5};
		for(int i = 0; i < b1.length; i++)
		{
			bag6.add(b1[i]);
			bag7.add(b1[i]);
		}
		
		//A bag with some similar elements
		//With should be equivalent to bag6
		//After removing duplicates
		int[] b2 = {1,2,2,3,4,4,5,5,5};
		for(int i = 0; i < b2.length; i++){
			bag8.add(b2[i]);
		}
	}
	//Checks an empty bag
	//The bag should still be empty
	public static void runTest1(){
		bag1.removeDuplicates();
		if (bag1.isEmpty()){
			System.out.println("Success");
        	System.out.println(2);
   		}
		else{
        System.out.println("*** Failed test");
	
		}
	}
	//Checks a bag with one element
	//Should still have that element
	public static void runTest2(){
		bag2.removeDuplicates();
		if (bag2.equals(bag3)){
			System.out.println("Success");
            System.out.println(2);
        }
        else{
            System.out.println("*** Failed test");
		}
		
	}
	//Checks a bag with two of the same elements
	//Should only have one element
	public static void runTest3(){
		bag4.removeDuplicates();
		if (bag4.equals(bag5)){
			System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
		}
	//Checks a bag with multiple elements
	//but none repeat
	public static void runTest4(){
		bag6.removeDuplicates();
		if (bag6.equals(bag7)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	
	}
	//Checks a bag with multiple repeating elements
	public static void runTest5(){
		bag8.removeDuplicates();
		if (bag8.equals(bag6)){
			System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
		}
		
	}