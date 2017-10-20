/**
 * Test the recursive maximum.
 * 
 * @author Charles Hoot 
 * @version 3.0
 */
public class TestMaxArray {

    public static void main(String args[]) {
 
        RecursiveMaxOfArray rm = new RecursiveMaxOfArray();
        
        int array7[] = {10, 113, 25, 10, 35, 14, 29, 13, 14, 110, 13, 17, 34, 83, 9, 32, 44, 12, 90, 200};
        
		// Testing Part
		if ("test1".equals(args[0])) {
		    runTest1(rm);
		} else if ("test2".equals(args[0])) {
		    runTest2(rm);
		} else if ("test3".equals(args[0])) {
		    runTest3(rm);
		} else if ("test4".equals(args[0])) {
		    runTest4(rm);
		} else if ("test5".equals(args[0])) {
		    runTest5(rm);
		} else if ("test6".equals(args[0])) {
		    runTest6(rm);
		} else if ("test7".equals(args[0])) {
		    runTest7(rm, array7);
		} else if ("test8".equals(args[0])) {
		    runTest8(rm, array7);
		} else if ("test9".equals(args[0])) {
		    runTest9(rm, array7);
		} else {
		    runTest10(rm, array7);
		}
    }
	// Trying an array of size 1
   	public static void runTest1(RecursiveMaxOfArray rm) {	
	       
        int array[] = {4};
        int result;
        result = rm.max(array, 0, 0);        
        if(result==4) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
            System.out.println("*** Failed test");
   	}

    // Trying an array of size 2, first is largest
  	public static void runTest2(RecursiveMaxOfArray rm) {	
	               
        int array2[] = {3, 2};
        int result = rm.max(array2, 0, 1);        
        if(result==3) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
  	}

  	// Trying an array of size 2, second is largest
  	public static void runTest3(RecursiveMaxOfArray rm) {	
        
        int array3[] = {3, 4};
        int result = rm.max(array3, 0, 1);        
        if(result==4) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");

  	}
        
  	// Trying an array of size 3, first is largest"
  	public static void runTest4(RecursiveMaxOfArray rm) {	

        int array4[] = {10, 3, 4};
        int result = rm.max(array4, 0, 2);        
        if(result==10) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");

  	}
  	
    // Trying an array of size 3, second is largest
 	public static void runTest5(RecursiveMaxOfArray rm) {
        int array5[] = {10, 13, 4};
        int result = rm.max(array5, 0, 2);        
        if(result==13) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
 	}
 	
    // Trying an array of size 3, third is largest
 	public static void runTest6(RecursiveMaxOfArray rm) {
        int array6[] = {10, 13, 14};
        int result = rm.max(array6, 0, 2);        
        if(result==14) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
 	}

    // Trying an array of size 20 (look at all values)
 	public static void runTest7(RecursiveMaxOfArray rm, int[] array7) {
        int result = rm.max(array7, 0, 19);        
        if(result==200) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");     		
     }
 	
    // Trying an array of size 20 (look at first third
 	public static void runTest8(RecursiveMaxOfArray rm, int[] array7) {
        int result = rm.max(array7, 0, 6);        
        if(result==113) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
 	}
 	
    // Trying an array of size 20 (look at second third)
 	public static void runTest9(RecursiveMaxOfArray rm, int[] array7) {
        int result = rm.max(array7, 7, 13);        
        if(result==110) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
 	}
        
 	// Trying an array of size 20 (look at last third excluding the last value)
 	public static void runTest10(RecursiveMaxOfArray rm, int[] array7) {
        int result = rm.max(array7, 13, 18);        
        if(result==90) {
            System.out.println("Success");
            System.out.println(1);
        }
        else
        	System.out.println("*** Failed test");
        
    }

}
