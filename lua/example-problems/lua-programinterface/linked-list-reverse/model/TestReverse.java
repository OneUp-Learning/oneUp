
public class TestReverse {
	private static LList<Integer> List1 = new LList<Integer>();
	private static LList<Integer> List2 = new LList<Integer>();
	private static LList<Integer> List3 = new LList<Integer>();
	private static LList<Integer> List4 = new LList<Integer>();
	
	
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
		List3.clear();
		List4.clear();
		
		//A list with only two elements
		List1.add(5);
		List1.add(6);
		
		//A list with 6 elements
		//Non-sequential just in case
		
		int[] a1 = {5,3,8,6,17,6};
		for(int i = 0; i < a1.length; i++){
			List2.add(a1[i]);
		}
		
		//Comparison list for List1
		List3.add(6);
		List3.add(5);
		
		//A reverse version of List2 for comparison
		int[] a2 = {6,17,6,8,3,5};
		for (int i = 0; i < a2.length; i++){
			List4.add(a2[i]);
		}
		
	}
	public static void runTest1(){
		//Reverses a list with only two elements
		//Compares to another list
		List1.reverse();
		if (List1.equals(List3)){
			
				System.out.println("Success");
	            System.out.println(5);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	public static void runTest2(){
		//Reverses a list with multiple elements
		//Compares to list in correct reverse order
		List2.reverse();
		if (List2.equals(List4)){
			
				System.out.println("Success");
	            System.out.println(5);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	}
	
	


