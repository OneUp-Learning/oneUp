'''
Created on Oct 23, 2019

@author: cmickle
'''
from django.shortcuts import render
from Instructors.models import FlashCardGroup,FlashCardGroupCourse,FlashCardToGroup,FlashCards
from Instructors.views import utils
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
import pprint

pp = pprint.PrettyPrinter(indent=4)

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def groupListView(request):
  
    context_dict,currentCourse = utils.initialContextDict(request)   
           
    groupID = []      
    groupName = []
    groupPos = []
    all_cards_in_group=[]
    #for JSON data containing group/cards info
    cards=[]
    

    flash_ID=[]
    flash_Name=[]
    if not FlashCardGroup.objects.filter(groupName="Unassigned").exists():
        unassigned_flashgroup = FlashCardGroup()
        unassigned_flashgroup.groupName = "Unassigned"
        unassigned_flashgroup.save()
        course_group = FlashCardGroupCourse()
        course_group.groupID = unassigned_flashgroup
        course_group.courseID = currentCourse
        course_group.save()

    cgroups = FlashCardGroupCourse.objects.filter(courseID=currentCourse).order_by("groupPos")
    #FlashCardGroup.objects.all().delete()
    '''
    [
        {
            'id': , 
            'fname' : , 
            'front': , 
            'back': , 
            'groups': [
                {
                    'id': ,
                    'name' ,
                },
                {
                    'id': ,
                    'name' ,
                }
            ]
        },
        {
            'id': , 
            'fname' : , 
            'front': , 
            'back': , 
            'groups': [
                {
                    'id': ,
                    'name' ,
                },
            ]
        }
    ]
    '''
    # {123: 0, 32: 1, }
    # a, b, c
    # 1:a, 1:b, 2:b
    # {1: 0}
    flash_card_index_map = {}
    for cg in cgroups:
        gId = cg.groupID.groupID
        group = FlashCardGroup.objects.get(groupID=gId)
        groupID.append(gId)
        groupName.append(group.groupName)
        groupPos.append(cg.groupPos)
        #print(group.groupName)
        cardGroup=FlashCardToGroup.objects.filter(groupID=gId)
        temp=[]
        all_groups_of_card=[]
        for card in cardGroup:
            flash_card_json = {}
            edit_groups_only = False
            if card.flashID in flash_card_index_map.keys():
                flash_card_json = cards[flash_card_index_map[card.flashID]]
                edit_groups_only = True
            
            if not edit_groups_only:
                flash_card_json['id'] = card.flashID.pk
                flash_card_json['name'] = card.flashID.flashName
                flash_card_json['front'] = card.flashID.front
                flash_card_json['back'] = card.flashID.back
                flash_card_json['groups'] = []
            
            # load groups
            flash_card_json['groups'].append({'id': cg.groupID.pk, 'name': cg.groupID.groupName})

            if not edit_groups_only:
                cards.append(flash_card_json)
                flash_card_index_map[card.flashID] = len(cards)-1

            temp.append(card.flashID)
            # cards.append([{"groupName":group.groupID.groupName, "groupID" : group.groupID.pk}
            #     for group in FlashCardToGroup.objects.filter(flashID=card.flashID)])

            # cards.append(cards.append([{"flashID" : flashcard.flashID.pk,
            #     "flashName" : flashcard.flashID.flashName, "front" : flashcard.flashID.front, "back" : flashcard.flashID.back }
            #     for flashcard in cardGroup]))

            #print("****************************",card.flashID)
        all_cards_in_group.append(temp)

    pp.pprint(cards)
    #context entry for displaying groups in modal create
    groups=[ {"name":group.groupID.groupName, "id" : group.groupID.pk } for group in FlashCardGroupCourse.objects.filter(courseID=currentCourse).exclude( groupID__groupName="Unassigned")]
    context_dict['groups']=groups
    context_dict['cards'] = cards

    context_dict['group_range'] = zip(range(cgroups.count()),groupID,groupName,groupPos,all_cards_in_group)
    
    return render(request,'Instructors/flashCardGroupList.html', context_dict)