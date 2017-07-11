from django.shortcuts import render


def conditionTestView(request):
    context_dict = {}
    
    return render(request,'Instructors/conditionInterface.html', context_dict)
