
public class TestRemove {
	private static LList<Integer> List1 = new LList<Integer>();
	private static LList<Integer> List2 = new LList<Integer>();
	private static LList<Integer> List3 = new LList<Integer>();
	private static LList<Integer> List4 = new LList<Integer>();
	
	public static void main(String[] args) {
		//Initialize Lists
		initLists();
		
		runTest1();
		
		runTest2();
		
		runTest3();
				
	}
	public static void initLists(){
		
		//Initializing
		List1.clear();
		List2.clear();
		List3.clear();
		
		//One List that is empty
		List1.clear();
		
		//One List with elements
		int[] a1 = {1,2,3,4,5};
		
		for (int i = 0; i < a1.length; i++)
		{
			List2.add(a1[i]);
		}
		int[] a2 = {2,3,4,5};
		
		for (int i = 0; i < a2.length; i++)
		{
			List3.add(a2[i]);
		}
		
		//One List with one element
		List4.add(4);
		
		}
	
	public static void runTest1(){
		//Checks an Empty List
		if(List1.remove(1) == null){
			System.out.println("Success");
            System.out.println(3.34);
        }
        else
            System.out.println("*** Failed test");
		}
	
	public static void runTest2(){
		//Checking a list after removing the first entry,
		//Then comparing to a similar list
		LList<Integer> result = new LList<Integer>();
		result.add(List2.remove(1));
		if(List2.equals(List3) && result.contains(1)){
			System.out.println("Success");
            System.out.println(3.33);
        }
        else
            System.out.println("*** Failed test");
			
		}
		
	
	public static void runTest3(){
		//Checking a List with only one entry
		LList<Integer> result = new LList<Integer>();
		result.add(List4.remove(1));
		{
			if(result.contains(4)){
				System.out.println("Success");
	            System.out.println(3.33);
	        }
	        else
	            System.out.println("*** Failed test");
			}
		}
		
	}

	


