
public class TestCycle{
	private static LList<Integer> List1 = new LList<Integer>();
	private static LList<Integer> List2 = new LList<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize Lists
		initLists();
		
		runTest1();
		
		runTest2();
		
		
	}
	public static void initLists(){
		//Initializing
		List1.clear();
		List2.clear();
		
		
		//A list with two elements
		List1.add(2);
		List1.add(4);
		
		//A list with 5 elements
		int[] a1 = {1,2,3,4,5};
		
		for (int i = 0; i < a1.length; i++)
		{
			List2.add(a1[i]);
		}
		
	}
	public static void runTest1(){
		
		//Cycles a list with only two elements
		//Checks their positions
		List1.cycle();
		if(List1.getEntry(1) == 4 && List1.getEntry(2) == 2){
				System.out.println("Success");
	            System.out.println(5);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	public static void runTest2(){
		//Cycles a list with multiple elements
		//Checks positions of first and last elements
		List2.cycle();
		if(List2.getEntry(1) == 2 && List2.getEntry(5) == 1){
			
				System.out.println("Success");
	            System.out.println(5);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	
	

}
