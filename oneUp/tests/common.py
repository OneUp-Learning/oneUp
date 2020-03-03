from django.test import TestCase

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

import time

class CommonTestCase(object):
    @classmethod
    def init_common(cls):
        # Set up data for the whole TestCase. Model instances created cannot be modified
        cls.printb("---------- Setting up Common ---------")
        cls.create_permissions()

    @classmethod
    def create_permissions(cls):
        user_content_type = ContentType.objects.get_for_model(User)

        cls.create_teachers_permission, created = Permission.objects.get_or_create(name='Create Teachers', codename='cr_teacher', content_type=user_content_type)
        cls.create_students_permission, created = Permission.objects.get_or_create(name='Create Students', codename='cr_student', content_type=user_content_type)
        cls.create_admins_permission, created = Permission.objects.get_or_create(name='Create Admins', codename='cr_admin', content_type=user_content_type)

        cls.admin_group, created = Group.objects.get_or_create(name='Admins')
        cls.admin_group.permissions.add(cls.create_teachers_permission, cls.create_students_permission, cls.create_admins_permission)

        cls.teacher_group, created = Group.objects.get_or_create(name='Teachers')
        cls.teacher_group.permissions.add(cls.create_students_permission)
    
    @classmethod
    def printb(*text, split=False):
        text = text[1:]
        print("".join(list(map(lambda x: f"\033[1m{x}\033[0m" if text.index(x) % 2 == 0 or split == False else f"{x}", text))) + f" \033[1m[{time.perf_counter():.3f}s]\033[0m")
