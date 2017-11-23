
public class TestAdd {
	private static LinkedBag<Integer> bag1 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag2 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag3 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag4 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag5 = new LinkedBag<Integer>();
	private static LinkedBag<Integer> bag6 = new LinkedBag<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize bags
		initbags();
		
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
	public static void initbags(){
		//Initializing
		bag1.clear();
		bag2.clear();
		bag3.clear();
		bag4.clear();
		bag5.clear();
		
		//One Empty bag
		bag1.clear();
		
		//Comparison bag for bag1
		bag2.add(1);
		
		//Bag with only one element
		bag3.add(2);
		
		//Comparison bag for bag3
		bag4.add(3);
		bag4.add(2);
		
		
		//Bag with multiple elements
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			bag5.add(a1[i]);
		}
		//Comparison bag for bag5
		int[] a2 = {6,1,2,3,4,5};
		for (int i = 0; i < a2.length; i++){
			bag6.add(a2[i]);
		}
	}
	public static void runTest1(){
		//Adds to an empty bag
		bag1.add1(1);
		if(bag1.equals(bag2)){
			System.out.println("Success");
            System.out.println(3.34);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest2(){
		//Adds to a bag with only one element
		bag3.add1(3);
		if(bag3.equals(bag4)){
			System.out.println("Success");
            System.out.println(3.33);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest3(){
		//Adds element at the end of the bag
		bag3.add1(6);
		if(bag3.contains(6)){
			System.out.println("Success");
            System.out.println(3.33);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	
	

}
