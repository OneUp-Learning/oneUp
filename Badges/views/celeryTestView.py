from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
from uuid import uuid4
from django.shortcuts import render
from Badges.models import CeleryTestResult
from Badges.tasks import testTask

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def celeryTestView(request):
    number = int(request.GET["number"])
    uniqid = str(uuid4())
    contextdict = {
        "uniqid":uniqid,
        "expected":number
    }
    for i in range(0,number):
        testTask.delay(uniqid,i)
    return render(request,'Badges/celeryTestView.html',contextdict)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def celeryTestResultsView(request):
    uniqid = request.GET["uniqid"]
    db_results = CeleryTestResult.objects.filter(uniqid=uniqid)
    db_set = set(x.sequence for x in db_results)
    expected = int(request.GET['expected'])
    results = []
    for i in range(0,expected):
        results.append({"num":i,"present":i in db_set})
    contextdict = {
        "results":results
    }
    return render(request,'Badges/celeryTestResultView.html',contextdict)