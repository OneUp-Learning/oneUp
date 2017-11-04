
public class TestReverse {
	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
	private static LList<Integer> list5 = new LList<Integer>();
	private static LList<Integer> list6 = new LList<Integer>();
	
	public static void main(String[] args) {
		//Initialize lists
		initlists();
		
		if ("test1".equals(args[0])) {
			runTest1();
		} else if ("test2".equals(args[0])) {
			runTest2();
		} else if ("test3".equals(args[0])) {
			runTest3();
		} else {
			runTest4();
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
		
		//An empty list
		list1.clear();
		
		//A list with only one element
		list2.add(3);
		
		//A list with only two elements
		list3.add(5);
		list3.add(6);
		
		//A list with 6 elements
		//Non-sequential just in case
		
		int[] a1 = {5,3,8,6,17,6};
		for(int i = 0; i < a1.length; i++){
			list4.add(a1[i]);
		}
		
		//Comparison list for list1
		list5.add(6);
		list5.add(5);
		
		//A reverse version of list2 for comparison
		int[] a2 = {6,17,6,8,3,5};
		for (int i = 0; i < a2.length; i++){
			list6.add(a2[i]);
		}
		
	}
	//Testing an empty list
	//Should still be empty
	public static void runTest1(){
		list1.reverse();
		
		if(list1.isEmpty()){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
	}
	//Testing a list with only one element
	//Should have no effect
	public static void runTest2(){
		list2.reverse();
		if (!list2.isEmpty() && list2.getEntry(1) == 3){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	//Reverses a list with only two elements
	//Compares to another list
	public static void runTest3(){
		
		list3.reverse();
		if (list3.equals(list5)){
			
				System.out.println("Success");
	            System.out.println(3);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	//Reverses a list with multiple elements
	//Compares to list in correct reverse order
	public static void runTest4(){
		list4.reverse();
		if (list4.equals(list6)){
			
				System.out.println("Success");
	            System.out.println(3);
	        }
	        else {
	            System.out.println("*** Failed test");
			}
		}
	}
	
	