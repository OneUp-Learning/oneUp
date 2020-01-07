# Generated by Django 2.2.4 on 2019-10-30 06:16

from django.db import migrations, models
import django.db.models.deletion

def migrate_student_challenge_questions(apps, schema_editor):
    # Update the student challenges to include the related challenge question id 
    StudentChallengeQuestions = apps.get_model("Students","StudentChallengeQuestions")
    ChallengesQuestions = apps.get_model("Instructors","ChallengesQuestions")

    defaultCQ = ChallengesQuestions.objects.all()[0]
    student_challenge_questions = StudentChallengeQuestions.objects.all()
    for student_challenge_question in student_challenge_questions:
        challenge_question = ChallengesQuestions.objects.filter(challengeID=student_challenge_question.studentChallengeID.challengeID, questionID=student_challenge_question.questionID)
        
        if not challenge_question:
            print("[ERROR] No challenge question can be found for student challenge question instance :(")
            # This is a fairly broken case, so we're just assigning a value
            # so the DB won't complain.
            student_challenge_question.challengeQuestionID = defaultCQ
            student_challenge_question.save()
            continue

        student_challenge_question.challengeQuestionID = challenge_question[0]
        student_challenge_question.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0108_auto_20190827_1458'),
        ('Students', '0090_auto_20191115_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentchallengequestions',
            name='challengeQuestionID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Instructors.ChallengesQuestions', verbose_name='the related challenge_question'),
        ),
        migrations.RunPython(migrate_student_challenge_questions),
        migrations.AlterField(
            model_name='studentchallengequestions',
            name='challengeQuestionID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.ChallengesQuestions', verbose_name='the related challenge_question'),
        ),
    ]
