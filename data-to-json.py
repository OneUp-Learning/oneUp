from Students.models import StudentActions, StudentActionsLoop, Student
from Instructors.models import Courses
import json
import pprint
from datetime import datetime
from collections import defaultdict

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

pp = pprint.PrettyPrinter(indent=1)

json_data = defaultdict()
student_actions_all = StudentActions.objects.all().order_by('timestamp')
# Timestamp Group (1st week) -> Course -> Student -> list 1hr data
# Timestamp Group (2nd week) -> Course -> Student -> list 1hr data
if student_actions_all:
    current_date = student_actions_all.first().timestamp.date().strftime("%m/%d/%Y")
    current_course = student_actions_all.first().courseID.pk
    current_student = student_actions_all.first().studentID.pk
    course_dict = defaultdict()
    student_dict = defaultdict()

    for student_action in student_actions_all:
        if current_date != student_action.timestamp.date().strftime("%m/%d/%Y"):
            current_date = student_action.timestamp.date().strftime("%m/%d/%Y")
        if current_course != student_action.courseID.pk:
            current_course = student_action.courseID.pk
        if current_student != student_action.studentID.pk:
            current_student = student_action.studentID.pk

        if not current_date in json_data:
            json_data[current_date] = defaultdict()
        if not current_course in json_data[current_date]:
            json_data[current_date][current_course] = defaultdict()
        if not current_student in json_data[current_date][current_course]:
            json_data[current_date][current_course][current_student] = []

        loops = StudentActionsLoop.objects.filter(studentActionsID=student_action.pk)
        for loop in loops:
            data = defaultdict()
            data['warmups_attempted'] = loop.warmups_attempted
            data['serious_attempted'] = loop.serious_attempted
            data['duels_sent'] = loop.duels_sent
            data['duels_accepted'] = loop.duels_accepted
            data['callouts_sent'] = loop.callouts_sent
            data['callouts_participated'] = loop.callouts_participated

            data['high_score_challenges'] = loop.high_score_challenges
            data['vc_earned'] = loop.vc_earned
            data['badges_earned'] = loop.badges_earned
            data['on_leaderboard'] = loop.on_leaderboard
            data['duels_won'] = loop.duels_won
            data['callouts_won'] = loop.callouts_won

            data['low_score_challenges'] = loop.low_score_challenges
            data['duels_lost'] = loop.duels_lost
            data['callouts_lost'] = loop.callouts_lost

            data['timestamp'] = loop.timestamp.strftime("%m/%d/%Y %H:%M:%S")
            json_data[current_date][current_course][current_student].append(data)





d = dict(json_data)
for k, v in d.items():
    d[k] = dict(v)
    for a, b in d[k].items():
        d[k][a] = dict(b)


with open("data.json", "w+") as out:
    json.dump(d, out, indent=4)

pp.pprint(d)
