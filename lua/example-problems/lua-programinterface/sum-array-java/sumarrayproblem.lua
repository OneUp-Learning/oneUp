tests = {
   {name="test1",command="java SumArray test1", points=5},
   {name="test2",command="java SumArray test2", points=5},
   {name="test3",command="java SumArray test3", points=5}}

checker = programinterface.program_checker("/home/kirwin/workspace/oneUp-GIT/lua/example-problems/lua-programinterface/sum-array-java","SumArray.java","javac *.java",15,tests)

