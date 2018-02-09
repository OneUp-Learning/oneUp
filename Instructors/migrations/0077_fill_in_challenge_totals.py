from django.db import migrations

def fill_in_challenge_totals(apps,schema_editor):
    Challenges = apps.get_model("Instructors","Challenges")
    ChallengesQuestions = apps.get_model("Instructors","ChallengesQuestions")
    for chall in Challenges.objects.all():
        challQuests = ChallengesQuestions.objects.filter(challengeID = chall)
        total = 0
        for cq in challQuests:
            total += cq.points
        chall.totalScore = total
        chall.save()

class Migration(migrations.Migration):
    
    dependencies = [
        ('Instructors', '0076_auto_20180209_1514'),
    ]

    operations = [
        migrations.RunPython(fill_in_challenge_totals),
    ]
