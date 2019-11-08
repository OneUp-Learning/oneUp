
public class TestDuplicateAll {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag5 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag6 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag7 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag8 = new LinkedBag<Integer>();
	
	
	
	public static void main(String[] args){
		
		initBags();
		
		if("test1".equals(args[0])){
			runTest1();
		}
		
		else if ("test2".equals(args[0])){
			runTest2();
		}
		
		else if ("test3".equals(args[0])){
			runTest3();
		}
		else {
			runTest4();
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
		
		//A bag with no entries
		bag1.clear();
		//Bag to compare with bag1
		bag2.clear();
		
		//A bag with only one element
		bag3.add(3);
		//Bag to compare with bag2
		bag4.add(3);
		bag4.add(3);
		
		//A bag with a few elements
		int[] b1 = {1,2,3,4,5};
		for (int i = 0; i < b1.length; i++){
			bag5.add(b1[i]);
		}
		//Bag for comparison with bag4
		int[] b2 = {1,2,3,4,5,1,2,3,4,5};
		for (int i = 0; i < b2.length; i++)
		{
			bag6.add(b2[i]);
		}
			
		//Bag with non-sequential elements
		int[] b3 = {123, 436, 238, 910, 493};
		for (int i = 0; i < b3.length; i++)
		{
			bag7.add(b3[i]);
		}
		//Bag for comparison with bag 6
		int[] b4 = {123,436,238,910,493,123,436,238,910,493};
		for (int i = 0; i < b4.length; i++)
		{
			bag8.add(b4[i]);
		}
	}
	//Checks an empty bag and compares
	//it to another empty bag
	public static void runTest1(){
		bag1.duplicateAll();
		if(bag1.equals(bag2)){
			System.out.println("Success");
			System.out.println(2);
		}
		else{
			System.out.println("*** Failed Test");
		}
	}
	//Checks a bag with one element and
	//compares it to the desired result bag
	public static void runTest2(){
		bag3.duplicateAll();
		if(bag3.equals(bag4)){
			System.out.println("Success");
			System.out.println(2);
		}
		else{
			System.out.println("*** Failed Test");
		}
	}
	//Checks a bag with multiple elements
	public static void runTest3(){
		bag5.duplicateAll();
		if(bag5.equals(bag6)){
			System.out.println("Success");
			System.out.println(3);
		}
		else{
			System.out.println("*** Failed Test");
		}
	}
	//Checks a bag with non-sequential elemetns
	public static void runTest4(){
		bag7.duplicateAll();
		if(bag7.equals(bag8)){
			System.out.println("Success");
			System.out.println(3);
		}
		else{
			System.out.println("*** Failed Test");
		}
	}

}
