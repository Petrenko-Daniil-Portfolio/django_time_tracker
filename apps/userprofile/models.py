from django.db import models

from django.db.models.signals import pre_save, post_delete
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from tinymce import models as tiny_mce_models

# Create your models here.

#USER 

class UserprofileManager(BaseUserManager):
    def create_user(self, email, name, surname, date_of_birth, password, avatar):
        if not email:
            raise ValueError("Email is not set")
        if not name:
            raise ValueError("Name is not set")
        if not surname:
            raise ValueError("Surname is no set")
        if not date_of_birth:
            raise ValueError("Surname is not set")
        if not password:
            raise ValueError("Password is not set")

        user = self.model(
            email = self.normalize_email(email),
            name = name,
            surname = surname,
            date_of_birth = date_of_birth,
            avatar = avatar,
        )

        print("avatar in model: "+str(avatar))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, date_of_birth, password, avatar=None):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            name = name,
            surname = surname, 
            date_of_birth = date_of_birth,
            avatar=avatar,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user

class Userprofile(AbstractBaseUser):
    
    email = models.EmailField(verbose_name='email', unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=50) 
    surname = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    position = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to='images/', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'date_of_birth']


    objects = UserprofileManager()

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

@receiver(post_delete, sender=Userprofile)
def submission_delete(sender, instance, **kwargs):
    instance.avatar.delete(False)



#PROJECT
class Project(models.Model):

    slug = models.SlugField(unique=True, blank=True) #Universally Unique Identifier or Slug
    name = models.CharField(max_length=50, null=False) 
    description = tiny_mce_models.HTMLField()

    REQUIRED_FIELDS = [name, description]

    def __str__(self):
        return self.name

#TASK
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Task(models.Model):

    type_choice = (
        ('bag', 'bag'),
        ('feature', 'feature')
    )

    priority_choice = (
        ('high', 'high'),
        ('medium', 'medium'),
        ('low', 'low')
    )

    name = models.CharField(max_length=30)
    description = tiny_mce_models.HTMLField()
    date_of_start = models.DateField()
    date_of_end = models.DateField()
    type = models.CharField(max_length=10, choices=type_choice)
    priority = models.CharField(max_length=10, choices=priority_choice)
    hours_to_solve = models.DecimalField(max_digits=7, decimal_places=2)# 99999.99
    creator = models.ForeignKey(Userprofile, related_name='user_creator', on_delete=models.CASCADE)
    executor = models.ForeignKey(Userprofile, related_name='user_executor', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
       return self.name

    def save(self, *args, **kwargs):
        if self.id:
            old_task = Task.objects.get(pk=self.id)
            subject = self.name+' Task Update'
            
            html_message = render_to_string('mail_template.html', {'old_task': old_task, 'new_task': self})
            text_message = strip_tags(html_message)

            if old_task.creator == old_task.executor: 
                email_receivers = [old_task.executor]
            else:
                email_receivers = [old_task.creator, old_task.executor]


            send_mail(subject, text_message, 'vremennyja71@gmail.com', email_receivers, html_message=html_message)
            
        
        super().save(*args, **kwargs)

#COMMENT
class Comment(models.Model):
    comment = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Userprofile, on_delete=models.CASCADE)


#TIMELOG
from django.utils import timezone
from datetime import datetime
class Timelog(models.Model):
    hours_spent = models.DecimalField(max_digits=7, decimal_places=2)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    comment = models.CharField(max_length=50, null=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)

    creation_date = models.DateTimeField(auto_now=True)

    # def __init__(self, task_id, comment=None, hours_spent=0):
    #     self.hours_spent=hours_spent
    #     self.task_id=task_id,
    #     self.comment=comment