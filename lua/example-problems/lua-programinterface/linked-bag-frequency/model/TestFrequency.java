
public class TestFrequency {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	
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
		
		//An empty bag
		bag1.clear();
		
		//A bag with only one element
		bag2.add(5);
		
		//A bag with a few elements
		int[] b1 = {1,2,2,2,3,5,6,7,8,4,2};
		for(int i = 0; i < b1.length; i++)
		{
			bag3.add(b1[i]);
		}
		//A bag with a few elements, but not the desired element
		int[] b2 = {1,3,4,5,7,4,3,6,8,1,6};
		for (int i = 0; i < b2.length; i++){
			bag4.add(b2[i]);
		}
	}
	//Checks an empty bag
	//Result should be 0
	public static void runTest1(){
		int result;
		result = bag1.getFrequencyOf(1);
		if(bag1.isEmpty() && result == 0)
		{
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Checks a bag with one element
	public static void runTest2(){
		int result;
		result = bag2.getFrequencyOf(5);
		if (result == 1){
			System.out.println("Success");
			System.out.println(2);
    	}
		else {
			System.out.println("*** Failed test");
		}
	}
	//Checks a bag with multple elements
	//The number 2 repeats 4 times in the bag
	public static void runTest3(){
		int result;
		result = bag3.getFrequencyOf(2);
		if (result == 4){
			System.out.println("Success");
        	System.out.println(3);
		}
		else {
			System.out.println("*** Failed test");
	}
	}
	//Checks a bag that lacks the desired entry
	//result should be 0
	public static void runTest4(){
		int result;
		result = bag4.getFrequencyOf(2);
		if (result == 0){
			System.out.println("Success");
        	System.out.println(3);
        }
        else {
        	System.out.println("*** Failed test");
		}
		
	}

}
