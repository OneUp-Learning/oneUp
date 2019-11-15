programinterface.initialize("test",0,"bob")
tests = {{name="test1",command="python3 sumarrayproblem.py test1",points=5},
    {name="test2",command="python3 sumarrayproblem.py test2",points=5},
    {name="test3",command="python3 sumarrayproblem.py test3",points=5}}

checker = programinterface.program_checker("lua/example-problems/lua-programinterface/sum-array-python","sumarrayproblem.py","",15,tests)
