
public class TestAdd {

	private static LList<Integer> list1 = new LList<Integer>();
	private static LList<Integer> list2 = new LList<Integer>();
	private static LList<Integer> list3 = new LList<Integer>();
	private static LList<Integer> list4 = new LList<Integer>();
	private static LList<Integer> list5 = new LList<Integer>();
	
	
	public static void main(String[] args) {
		//Initialize Lists
		initLists();
		
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
	public static void initLists(){
		//Initializing
		list1.clear();
		list2.clear();
		list3.clear();
		list4.clear();
		list5.clear();
		
		//One Empty list
		list1.clear();
		
		//One list with only one element
		list2.add(2);
		
		//Lists with multiple elements
		//Element will be added at the end
		list3.clear();
		//Element will be added in the middle
		list4.clear();
		//Element will be added at the beginning
		list5.clear();
		
		int[] a1 = {1,2,3,4,5};
		for(int i = 0; i < a1.length; i++){
			list3.add(a1[i]);
			list4.add(a1[i]);
			list5.add(a1[i]);
		}
	}
	public static void runTest1(){
		//Adds to an empty list
		list1.add1(1,1);
		if(list1.contains(1)){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest2(){
		//Adds to a list with only one element
		list2.add1(2,3);
		if(list2.contains(3) && list2.getEntry(2) == 3){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest3(){
		//Adds element at the end of the list
		list3.add1(6, 6);
		if(list3.contains(6) && list3.getEntry(6) == 6){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest4(){
		//Adds element at the middle of the list
		list4.add1(3, 6);
		if(list4.contains(6) && list4.getEntry(3) == 6){
			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	public static void runTest5(){
		//Adds element at the beginning of the list
		list5.add1(1, 6);
		if(list5.contains(6) && list5.getEntry(1) == 6){

			System.out.println("Success");
            System.out.println(2);
        }
        else {
            System.out.println("*** Failed test");
		}
		
	}
	

}
