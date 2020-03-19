'''
Created on Aprial 27, 2018

@author: Joel Evans
'''

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required,  user_passes_test
from Instructors.models import Activities, Courses, ActivitiesCategory
from Students.models import StudentRegisteredCourses, StudentActivities
from Instructors.views.utils import initialContextDict
from Instructors.constants import uncategorized_activity
from django.template.defaultfilters import default
from django.template.context_processors import request
from oneUp.decorators import instructorsCheck


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityCatList(request):
    context_dict, currentCourse = initialContextDict(request)
    categories = ActivitiesCategory.objects.filter(
        courseID=currentCourse).exclude(name=uncategorized_activity).order_by("catPosition")
    print("cats")
    print(categories)
    context_dict['cats'] = categories
    context_dict['use_xp_weights'] = context_dict['ccparams'].xpWeightAPoints > 0

    return render(request, 'Instructors/ActivityCategories.html', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityCatCreate(request):
    context_dict, currentCourse = initialContextDict(request)

    if request.POST:
        # Check the category exists and has to be edited
        if 'catID'in request.POST:
            currentCat = ActivitiesCategory.objects.get(
                categoryID=int(request.POST['catID']))
        else:
            currentCat = ActivitiesCategory()

        currentCat.name = request.POST['catName']
        currentCat.courseID = currentCourse
        currentCat.xpWeight = request.POST['xpWeight']
        currentCat.save()

        if 'activityList' in request.POST:
            return redirect('/oneUp/instructors/activitiesList')

        return redirect('/oneUp/instructors/activityCats')

    if 'catID' in request.GET:
        catID = request.GET['catID']
        cat = ActivitiesCategory.objects.filter(
            courseID=currentCourse, pk=catID).first()

        context_dict['catID'] = catID
        context_dict['catName'] = cat.name
        context_dict['xpWeight'] = cat.xpWeight
    else:
        context_dict['acts'] = Activities.objects.filter(
            courseID=currentCourse)
        context_dict['xpWeight'] = 1

    return render(request, 'Instructors/ActivityCategoryCreateForm.html', context_dict)


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def activityCatDelete(request):
    if request.POST:
        cat = ActivitiesCategory.objects.filter(
            pk=request.POST['catID']).first()
        if cat is not None:
            defaultCat = ActivitiesCategory.objects.filter(
                name=uncategorized_activity, courseID=cat.courseID)
            if not defaultCat.exists():
                defaultCat = ActivitiesCategory()
                defaultCat.name = uncategorized_activity
                defaultCat.courseID = cat.courseID
                defaultCat.save()
            else:
                defaultCat = defaultCat.first()

            linkedActs = Activities.objects.filter(category=cat)
            for act in linkedActs:
                act.category = defaultCat
                act.save()
            cat.delete()

    return redirect('/oneUp/instructors/activityCats')
