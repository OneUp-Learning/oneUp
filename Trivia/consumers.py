from cgitb import text
from re import M
from Students.models import Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict
from Trivia.models import TriviaSession
from Trivia.serializers import UserSerializer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
import json

from Instructors.views.utils import initialContextDict
from Instructors.models import Courses, InstructorRegisteredCourses, Trivia, TriviaAnswer, TriviaQuestion

# @ensure_csrf_cookie
class TriviaConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        context_dict, currentCourse = initialContextDict(None, self.scope['user'], self.scope['session'])
        user = self.scope['user']
        if (user.groups.filter(name='Teachers').exists() or user.groups.filter(name='Admins').exists()):
            context_dict["is_teacher"] = True
        else:
            context_dict["is_teacher"] = False
        
        user = UserSerializer(self.scope['user'])
        self.user = user
        self.isInstructor = context_dict["is_teacher"];
        
        trivia_id = self.scope['url_route']['kwargs']['trivia_id']
        
        self.trivia = Trivia.objects.get(triviaID=trivia_id)
        
        # print('trivia_%d_%s' % (currentCourse.courseID, self.trivia.triviaName))
        self.room_group_name = 'trivia_%d_%s' % (currentCourse.courseID, self.trivia.triviaName.replace(" ", "_"))
        # Set channel group name
        
        if not self.room_group_name in self.groups:
            self.groups.append(self.room_group_name)
        
        self.send(text_data=json.dumps({
            'event': 'init_data',
            'trivia_name': self.trivia.triviaName,
            'course_name': currentCourse.courseName,
            'name': user.data['first_name'],
            'id': user.data['id'],
        })) # Send the name of the trivia game to the instructor
        
        if self.isInstructor:
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': 'host-join',
                        'name': user.data['first_name'],
                        'id': user.data['id'],
                        'avatarurl':''
                    }
                )
            # give the questions to the host
            requested_questions = TriviaQuestion.objects.filter(triviaID=self.trivia)
            
            def buildQuestion(question):
                question_dict = {
                    'question': question.questionText,
                    'answer1': '',
                    'answer2': '',
                    'answer3': '',
                    'answer4': '',
                    'correctanswer': 0,
                }
                answers = TriviaAnswer.objects.filter(questionID=question)
                
                answer_count = 1
                for answer in answers:
                    if answer.isCorrect: # Update the correct answer
                        question_dict['correctanswer'] = answer_count
                    # append the answer to the question
                    question_dict['answer' + str(answer_count)] = answer.answerText
                    answer_count+=1 # increment the answer count
                return question_dict
            
            question_array = []
            
            for question in requested_questions:
                question_array.append(buildQuestion(question))
                
            # Send the questions to the instructor
            self.send(text_data=json.dumps({
                'event': 'trivia-questions',
                'questions': question_array,
            }))
        else:
            student_object = Student.objects.get(user=self.scope['user'])
            src_object = StudentRegisteredCourses.objects.filter(studentID=student_object, courseID=currentCourse.courseID)
            if src_object.exists():
                avatarurl = src_object[0].avatarImage 
            else:
                avatarurl='/static/images/avatars/anonymous.png'
                
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': 'room-joined',
                        'name': user.data['first_name'],
                        'id': user.data['id'],
                        'avatarurl': avatarurl,
                    }
                )
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    def disconnect(self, close_code):
        # Leave room group
        if self.room_group_name in self.groups:
            self.groups.remove(self.room_group_name)
            
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        
        async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'event': 'room-left',
                    'name': self.user.data['first_name'],
                    'id': self.user.data['id']
                }
            )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)        
        context_dict, currentCourse = initialContextDict(None, self.scope['user'], self.scope['session'])
        message_type = text_data_json['event']
        
        if message_type == "player-joined": # Send player data to the host
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'name': text_data_json['name'],
                    }
                )
        elif message_type == "room-joined": # Send player data to the host
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'name': text_data_json['name'],
                    }
                )
        elif message_type == "question-over": # When the instructor ends the question
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                    }
                )
        elif message_type == "next-question": # Instructor is ready to start the next question
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'question_count': text_data_json['question_count'],
                    }
                )
        elif message_type == "question-answered": # Player answered a question
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': 'player-answer',
                        'name': text_data_json['name'],
                        'answer': text_data_json['answer'],
                    }
                )
        elif message_type == "sent-info": # Data sent from instructors
            async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': 'sent-info',
                        'player_id': text_data_json['player_id'],
                        'score': text_data_json['score'],
                        'answeredCorrect': text_data_json['answeredCorrect'],
                    }
                )
        
        if not 'trivia_%d_%s' % (currentCourse.courseID, self.trivia.triviaName.replace(" ", "_")) in self.groups:
            self.disconnect()
        

    # Receive message from room group
    def broadcast(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))