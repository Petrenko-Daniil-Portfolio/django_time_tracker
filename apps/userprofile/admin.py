from django.contrib import admin
from django.forms import fields
from django.http import request

# Register your models here.
from .models import Userprofile, Project, Task, Comment, Timelog

#Register your forms here.
from .forms import *

#USERPROFILE
class UserprofileAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'date_of_birth')
    form = UserProfileForm

#PROJECT
from django import forms
class ProjectAdminForm(forms.ModelForm):

    class Meta:
        fields = [
            'name',
            'description'
        ]

    def __init__(self, *args, **kwargs):
        self.slug = "-"+str(self.current_user_id)
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        # print("_____________________________")
        # print(self.instance)
        self.instance.slug = self.instance.name + self.slug
        project = super(ProjectAdminForm, self).save(*args, **kwargs)
        return project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    form = ProjectAdminForm


    def get_form(self, request, obj=None, **kwargs):
        form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
        form.current_user_id = request.user.id
        return form

#TASK
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'priority', 'date_of_start', 'date_of_end')

    list_filter = ('project', 'priority', 'executor')

    form = TaskCreateForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj,  **kwargs)
        form.user = request.user
        return form
    
    def project(self, obj):
        project = Project.objects.get(id=self.project)
        return project

#COMMENT
from datetime import datetime
class CommentAdminForm(forms.ModelForm):
    comment = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'placeholder': 'Type your comment', 'class': 'form-control', 'rows':"3"}))
    class Meta:
        model = Comment
        fields = [
            'comment',
            'task_id'
        ]

    def __init__(self, *args, **kwargs):
        
        self.date = datetime.now()
        self.user_id = self.user

        super(CommentAdminForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.date = self.date
        self.instance.user_id = self.user_id
        task = super(CommentAdminForm, self).save(*args, **kwargs)
        return task

class CommentAdmin(admin.ModelAdmin):

    list_display = ('task_id', 'user_id', 'date')

    list_filter = ('task_id', 'user_id')

    form = CommentAdminForm


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj,  **kwargs)
        form.user = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('comment', 'task_id')
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

#TIMELOG
class TimelogAdminForm(forms.ModelForm):
    hours_spent = forms.DecimalField(max_digits=7, decimal_places=2, min_value=0)
    date = forms.DateTimeField(initial=datetime.now())

    class Meta:
        model = Timelog
        fields = [
            'comment',
            'hours_spent',
            'date',
            'task'
        ]
    
class TimelogAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'task', 'task_executor', 'hours_spent',  'date', 'creation_date')

    list_filter = ('date', 'task')

    
    form = TimelogAdminForm

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def project_name(self, obj):        
        return obj.task.project.name

    def task_executor(self, obj):
        return obj.task.executor

    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('comment',)
        return self.readonly_fields
    

admin.site.register(Userprofile, UserprofileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Timelog, TimelogAdmin)
