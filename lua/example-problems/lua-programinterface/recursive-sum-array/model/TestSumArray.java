/**
 * Test the recursive sum.
 * 
 */
public class TestSumArray {

   public static void main(String args[]) {
	   
        RecursiveSumArray rm = new RecursiveSumArray();
                
		// Testing Part
		if ("test1".equals(args[0])) {
		    runTest1(rm);
		} else if ("test2".equals(args[0])) {
		    runTest2(rm);
		} else if ("test3".equals(args[0])) {
		    runTest3(rm);
		} else if ("test4".equals(args[0])) {
		    runTest4(rm);
		} else {
		    runTest5(rm);
		}
    }
	// Trying an array of size 1
   	public static void runTest1(RecursiveSumArray rm) {	
	       
        int array[] = {4};
        int result;
        result = rm.sum(array, 0, 0);        
        if(result==4) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
            System.out.println("*** Failed test");
   	}

    // Trying an array of size 2
  	public static void runTest2(RecursiveSumArray rm) {	
	               
        int array2[] = {3, 2};
        int result = rm.sum(array2, 0, 1);        
        if(result==5) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
  	}
        
  	// Trying an array of size 3
  	public static void runTest3(RecursiveSumArray rm) {	

        int array3[] = {10, 3, 4};
        int result = rm.sum(array3, 0, 2);        
        if(result==17) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");

  	}
  	
    // Trying an array of size 5
 	public static void runTest4(RecursiveSumArray rm) {
        int array5[] = {10, 25, 10, 35, 14};
        int result = rm.sum(array5, 0, 4);        
        if(result==94) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");     		
     }
 	
    // Trying an array of size 6 (look at first third
 	public static void runTest5(RecursiveSumArray rm) {
        int array6[] = {10, 25, 10, 35, 14, 19};
        int result = rm.sum(array6, 0, 5);        
        if(result==113) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
 	}
}
 