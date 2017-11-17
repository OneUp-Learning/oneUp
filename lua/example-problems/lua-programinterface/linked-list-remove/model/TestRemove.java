public class TestRemove {
	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
	private static LList<Integer> list5 = new LList<Integer>();
	private static LList<Integer> list6 = new LList<Integer>();
	private static LList<Integer> list7 = new LList<Integer>();
	private static LList<Integer> list8 = new LList<Integer>();
	private static LList<Integer> list9 = new LList<Integer>();
	
	
	
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
		} else {
			runTest5();
		}
				
	}
	public static void initlists(){    
		
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
		
		
		//One list that is empty
		list1.clear();
		
		//Empty list for comparison
		list9.clear();
		
		//One list with one element
		list2.add(4);
		
		//Original elements
		int[] a1 = {1,2,3,4,5};
		
		//Initializing lists with original values
		for (int i = 0; i < a1.length; i++)
		{
			list3.add(a1[i]);
			list4.add(a1[i]);
			list5.add(a1[i]);
		}
		
		//Array with list removed from front
		int[] a2 = {2,3,4,5};
		//Array with item removed from middle
		int[] a3 = {1,2,4,5};
		//Array with item removed from end
		int[] a4 = {1,2,3,4};
		//
		for (int i = 0; i < a2.length; i++)
		{
			list6.add(a2[i]);
			list7.add(a3[i]);
			list8.add(a4[i]);
		}
		
		
	}
	//Checks an Empty list
	public static void runTest1(){
		
		if(list1.remove(1) == null && list1.equals(list9)){
			System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
		}
	
	
	
	//Checking a list with only one entry
	public static void runTest2(){
			int result = list2.remove(1);
			{
				if(list2.equals(list9) && result == 4){
					System.out.println("Success");
		            System.out.println(2);
		        }
		        else
		            System.out.println("*** Failed test");
				}
			}
	//Checking a list after removing the first entry,
	public static void runTest3(){
		
		LList<Integer> result = new LList<Integer>();
		result.add(list3.remove(1));
		if(list3.equals(list6) && result.contains(1)){
			System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
			
		}
	//Checking a list after removing an entry from the middle
	public static void runTest4(){
		LList<Integer> result = new LList<Integer>();
		result.add(list4.remove(3));
		if(list4.equals(list7)){
			System.out.println("Success");
            System.out.println(2);
        }
        else
            System.out.println("*** Failed test");
			
		}
	//Checking a list after removing an entry from the end
	public static void runTest5(){
		LList<Integer> result = new LList<Integer>();
		result.add(list5.remove(5));
		if(list5.equals(list8)){
			System.out.println("Success");
			System.out.println(2);
		}
		else
			System.out.println("*** Failed test");
	}
		
	}
