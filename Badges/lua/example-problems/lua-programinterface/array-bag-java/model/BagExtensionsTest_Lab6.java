
/**
 * This class performs tests on the extensions to the ArrayBag<String> class.
 * 
 * 
 * 
 * @author Charles Hoot
 * @version 3.0
 */
public class BagExtensionsTest_Lab6 {

    private static ArrayBag<String> testBag1 = new ArrayBag<String>();
    private static ArrayBag<String> testBag2 = new ArrayBag<String>();
    private static ArrayBag<String> testBag3 = new ArrayBag<String>();
    private static ArrayBag<String> testBag4 = new ArrayBag<String>();
    private static ArrayBag<String> testBag5 = new ArrayBag<String>();
    private static ArrayBag<String> testBag6 = new ArrayBag<String>();
    private static ArrayBag<String> testBag7 = new ArrayBag<String>();
    private static ArrayBag<String> testBag8 = new ArrayBag<String>();
    private static ArrayBag<String> testBag9 = new ArrayBag<String>();
    private static ArrayBag<String> testBag10 = new ArrayBag<String>();
    private static ArrayBag<String> testBag11 = new ArrayBag<String>(35);
    private static ArrayBag<String> testBag12 = new ArrayBag<String>(35);
    private static ArrayBag<String> testBag13 = new ArrayBag<String>();
    private static ArrayBag<String> testBag14 = new ArrayBag<String>();
    private static ArrayBag<String> testBag15 = new ArrayBag<String>();
    private static ArrayBag<String> testBag16 = new ArrayBag<String>();
    private static ArrayBag<String> testBag17 = new ArrayBag<String>();
    private static ArrayBag<String> testBag18 = new ArrayBag<String>();
    private static ArrayBag<String> testBag19 = new ArrayBag<String>();
    private static ArrayBag<String> testBag20 = new ArrayBag<String>();
    private static ArrayBag<String> testBag21 = new ArrayBag<String>();
    private static ArrayBag<String> testBag22 = new ArrayBag<String>();
    private static ArrayBag<String> testBag23 = new ArrayBag<String>();
    private static ArrayBag<String> testBag24 = new ArrayBag<String>();
    private static ArrayBag<String> testBag25 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag26 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag27 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag28 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag29 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag30 = new ArrayBag<String>(10);
    private static ArrayBag<String> testBag31 = new ArrayBag<String>();
    private static ArrayBag<String> testBag32 = new ArrayBag<String>();
    private static ArrayBag<String> testBag33 = new ArrayBag<String>();
    private static ArrayBag<String> testBag34 = new ArrayBag<String>();
    private static ArrayBag<String> testBag35 = new ArrayBag<String>(50);
    private static ArrayBag<String> testBag36 = new ArrayBag<String>();
    private static ArrayBag<String> testBag37 = new ArrayBag<String>(50);
    private static ArrayBag<String> testBag39 = new ArrayBag<String>(50);

    public static void main(String args[]) {

    	checkRemoveAllEntriesOf(args[0]);
        
    }
   public static void initializeBags() {
   
	    // A couple empty bags
        testBag15.clear();
        testBag16.clear();

        // A bag with a single item
        testBag31.clear();
        testBag31.add("A");

        // A bag with some items duplicated
        testBag35.clear();
        testBag35.add("G");
        testBag35.add("H");
        testBag35.add("G");
        testBag35.add("H");
        testBag35.add("A");
        testBag35.add("B");
        testBag35.add("C");
        testBag35.add("D");
        testBag35.add("G");
        testBag35.add("A");
        testBag35.add("B");
        testBag35.add("C");
        testBag35.add("D");
        testBag35.add("G");
        testBag35.add("H");
        testBag35.add("A");
        testBag35.add("B");
        testBag35.add("C");
        testBag35.add("I");
        testBag35.add("D");
        testBag35.add("G");
        testBag35.add("H");
        testBag35.add("A");
        testBag35.add("B");
        testBag35.add("C");
        testBag35.add("D");
        testBag35.add("E");
        testBag35.add("F");
        testBag35.add("G");
        testBag35.add("H");
       
        // The previous bag with all instances of "A" removed
        testBag39.clear();
        testBag39.add("G");
        testBag39.add("H");
        testBag39.add("G");
        testBag39.add("H");
        testBag39.add("B");
        testBag39.add("C");
        testBag39.add("D");
        testBag39.add("G");
        testBag39.add("B");
        testBag39.add("C");
        testBag39.add("D");
        testBag39.add("G");
        testBag39.add("H");
        testBag39.add("B");
        testBag39.add("C");
        testBag39.add("I");
        testBag39.add("D");
        testBag39.add("G");
        testBag39.add("H");
        testBag39.add("B");
        testBag39.add("C");
        testBag39.add("D");
        testBag39.add("E");
        testBag39.add("F");
        testBag39.add("G");
        testBag39.add("H");

    }
 
    public static void checkRemoveAllEntriesOf(String test) {
	
        initializeBags();

	if ("empty".equals(test)) {
	    testBag15.removeAllEntriesOf("A");
	    if (testBag15.equals(testBag16)) {
		System.out.println("Success\n5\n");
	    } else {
		System.out.println("*** Failed test\n0\n");

	    }
	} else if ("single".equals(test)) {

	    testBag31.removeAllEntriesOf("A");
	    if (testBag31.isEmpty()) {
		System.out.println("Success\n5\n");
	    } else {
		System.out.println("*** Failed test\n0\n");
		
	    }
	} else if ("multiple".equals(test)) {
		testBag35.removeAllEntriesOf("A");
		if (testBag35.equals(testBag39)) {
		    System.out.println("Success\n5\n");
		} else {
		    System.out.println("*** Failed test\n0\n");
		}
	}
    }
}
