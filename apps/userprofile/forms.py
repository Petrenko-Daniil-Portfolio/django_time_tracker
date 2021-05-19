from .models import Userprofile, Project, Task, Comment, Timelog

from django import forms

from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate

from tinymce import models as tiny_mce_models

#User creation and auth forms
class UserProfileForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    position = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    avatar = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control-file'}), required=False)

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control-file'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = Userprofile

        fields = [
            'email',
            'name',
            'surname',
            'date_of_birth',
            'position',
            'avatar',
            'password1',
            'password2',
        ]

class UserAuthenticationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Userprofile
        fields =[
            'email',
            'password',
        ]

    def clean(self):

        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']

            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid email or password")

#PROJECT
# creat form
class ProjectCreateForm(forms.ModelForm):

    name = forms.CharField(max_length=50, required=True)
    #description = tiny_mce_models.HTMLField()
    # slug = forms.SlugField(max_length=50)

    class Meta: 
        model = Project
        fields = [
            'name',
            'description',
            # 'slug',
        ]
    
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('project_name').replace(" ", "_")+"-"+str(kwargs.pop('user_id'))
        super(ProjectCreateForm, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.instance.slug = self.slug
        super(ProjectCreateForm, self).save(*args, **kwargs)

#update form
class ProjectUpdateForm(forms.ModelForm):

    name = forms.CharField(max_length=50, required=True)
    description = forms.Textarea()

    class Meta:
        model = Project
        fields = [
            'name',
            'description',
        ]

#TASK
#creat task form

class TaskCreateForm(forms.ModelForm):
    type_choice = (
        ('bag', 'bag'),
        ('feature', 'feature')
    )

    priority_choice = (
        ('high', 'high'),
        ('medium', 'medium'),
        ('low', 'low')
    )

    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Task name'}))

    date_of_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control','placeholder': 'Date of start'}))
    date_of_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control','placeholder': 'Date of end'}))
    
    type = forms.CharField(widget = forms.Select(attrs={'class': 'form-control'}, choices=type_choice))
    priority = forms.CharField(widget = forms.Select(attrs={'class': 'form-control'}, choices=priority_choice))

    hours_to_solve = forms.DecimalField(max_digits=7, decimal_places=2, min_value=0)

    

    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'date_of_start',
            'date_of_end',
            'type',
            'priority',
            'hours_to_solve',
            'executor',
            'project'
        ]

    def __init__(self, *args, **kwargs):
        self.creator = self.user
        super(TaskCreateForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.creator = self.creator
        task = super(TaskCreateForm, self).save(*args, **kwargs)
        return task

    # def clean_executor(self):
    #     if self.is_valid():
    #         executor_email = self.cleaned_data['executor']
    #         try:
    #             executor = Userprofile.objects.get(email=executor_email)
    #         except Userprofile.DoesNotExist:
    #             raise forms.ValidationError("There is no user with '"+executor_email+"' email")
    #     else:
    #         raise forms.ValidationError("Self is not valid")

    #     return executor

    # def clean_project(self):
    #     if self.is_valid():
    #         slug = self.cleaned_data['project']
    #         # creator
    #         try:
    #             project = Project.objects.get(slug=slug)
    #             return project

    #         except Project.DoesNotExist:                      
    #             raise forms.ValidationError("There is no project with '"+slug+"' slug")

class TaskUpdateForm(forms.ModelForm):
    type_choice = (
        ('bag', 'bag'),
        ('feature', 'feature')
    )

    priority_choice = (
        ('high', 'high'),
        ('medium', 'medium'),
        ('low', 'low')
    )

    date_of_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_of_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    
    type = forms.CharField(widget = forms.Select(attrs={'class': 'form-control'}, choices=type_choice))
    priority = forms.CharField(widget = forms.Select(attrs={'class': 'form-control'}, choices=priority_choice))

    hours_to_solve = forms.DecimalField(max_digits=7, decimal_places=2, min_value=0)

    class Meta:
        model = Task
        fields = [
            'name',
            'description',
            'date_of_start',
            'date_of_end',
            'type',
            'priority',
            'hours_to_solve'
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        self.creator = Userprofile.objects.get(email=instance.creator)
        self.project = instance.project
        super(TaskUpdateForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.creator = self.creator
        self.instance.project = self.project
        task = super(TaskUpdateForm, self).save(*args, **kwargs)
        return task

#COMMENT
class CommentCreateForm(forms.ModelForm):
    comment = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'placeholder': 'Type your comment', 'class': 'form-control', 'rows':"3"}))
    class Meta:
        model = Comment
        fields = [
            'comment'
        ]

    def __init__(self, *args, **kwargs):
        
        self.date = kwargs.pop('date') 
        self.task_id = kwargs.pop('task_id') 
        self.user_id = kwargs.pop('user_id') 
        super(CommentCreateForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.date = self.date
        self.instance.task_id = self.task_id
        self.instance.user_id = self.user_id
        task = super(CommentCreateForm, self).save(*args, **kwargs)
        return task

from datetime import datetime
class TimelogCreationForm(forms.ModelForm):
    hours_spent = forms.DecimalField(max_digits=7, decimal_places=2, min_value=0)
    date = forms.DateTimeField(initial=datetime.now())

    class Meta:
        model = Timelog
        fields = [
            'comment',
            'hours_spent',
            'date'
        ]
    
    def __init__(self, *args, **kwargs): 
        self.task = kwargs.pop('task') 

        super(TimelogCreationForm, self).__init__(*args, **kwargs)

    def save (self, *args, **kwargs):
        self.instance.task = self.task

        timelog = super(TimelogCreationForm, self).save(*args, **kwargs)
        return timelog


