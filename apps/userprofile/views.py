#
# Import djungo shortcuts and models

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from django.http import HttpResponse

from django.db.models import Q

from datetime import datetime
import json
import smtplib #delete

#
# Import models

from .models import *

from .forms import *

# Create your views here.

def signup_view(request):
    
    if request.POST:
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():

            form.save()
            
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name') 
            surname = form.cleaned_data.get('surname')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            position = form.cleaned_data.get('position')
            avatar = form.cleaned_data.get('avatar')
            password = form.cleaned_data.get('password1')

            

            userprofile = authenticate(email=email, password=password)
            
            login(request, userprofile)

            return redirect('index')
    else:
        form = UserProfileForm()
    
    return render(request, 'signup.html', {'form':form})

#ACCAUNT & Autentification 
def logout_user_view(request, account):
    logout(request)
    return redirect('index')

def login_user_view(request):

    user = request.user
    if user.is_authenticated:
        return redirect('index')
    
    form = UserAuthenticationForm(request.POST or None)
    if request.POST:
         email = request.POST['email']
         password = request.POST['password']

         user = authenticate(email = email, password = password)

         if user:
            login(request, user)
            return redirect('account', account = request.user)

    
    return render(request, 'login.html', {'form':form})

def user_account_view(request, account):
    user = request.user
    
    if not user.is_authenticated:
        return redirect('index')

    user = Userprofile.objects.get(email = user)    

    try:
        tasks = Task.objects.filter(executor = user)
    except Task.DoesNotExist:
        tasks = None
    context = {
        'user': user,
        'tasks': tasks
    }

    return render(request, 'account.html', context)


#MY_PROJECTS
def user_projects_view(request, account):
    user = request.user   
    if not user.is_authenticated:
        return redirect('index')

    user = Userprofile.objects.get(email = user)

    try:
        user_tasks  = Task.objects.filter(executor__exact=user).exclude(creator__exact = user).distinct("project")

        user_projects = []

        for task in user_tasks:
            user_project = task.project
            user_projects.append(user_project)

    except Task.DoesNotExist:
        user_projects = None
        print("user_projects is none")

    
    context = {
        'user': user,
        'user_projects': user_projects,
    }

    return render(request, 'user_projects.html', context)

def user_project_view(request, account, project_slug):
    user = request.user   
    if not user.is_authenticated:
        return redirect('index')

    try:
        project = Project.objects.get(slug=project_slug)

        tasks = Task.objects.filter(project=project)

        hours_spent = []
        for task in tasks:
            time_log_recs = Timelog.objects.filter(task_id=task)
            hours = 0
            for rec in time_log_recs:
                hours += float(rec.hours_spent)
            hours_spent.append(hours)

    except Project.DoesNotExist:
        return HttpResponse('Could not find project with slug: '+project_slug)
    except Task.DoesNotExist:
        return HttpResponse('Could not find tasks in project: '+project.name)

    context = {
        'project': project,
        'tasks': tasks,
        'hours_spent': hours_spent
    }
    
    return render(request, "user_project.html", context)


#TASKS
def task_view(request, account, project_slug, task_id):
    if not request.user.is_authenticated:
        return redirect('index')

    try:
        task = Task.objects.get(id=task_id)
        comments = Comment.objects.filter(task_id=task).order_by('-date')
        time_log_recs = Timelog.objects.filter(task_id = task)
        hours_spent = 0

        for rec in time_log_recs:
            hours_spent += float(rec.hours_spent)

    except Task.DoesNotExist:
        redirect('index')
    except Timelog.DoesNotExist:
        redirect('index')
    except Comment.DoesNotExist:
        comments = None


    if request.POST:
        form = CommentCreateForm(request.POST, task_id=task, user_id=request.user, date=datetime.now())
        if form.is_valid():
            form.save()
            return redirect('task', account = request.user, project_slug=project_slug, task_id=task.id)

    form = CommentCreateForm(task_id=task, user_id=Userprofile.objects.get(id=request.user.id), date=datetime.now())
    context = {
        'form': form,
        'task': task,
        'comments': comments,
        'hours_spent': hours_spent
    }
    return render(request, 'task.html', context)


def update_task(request, account, project_slug=None, task_id=None):
    if not request.user.is_authenticated:
        return redirect('index') 
    try:
        project = Project.objects.get(slug = project_slug)
        task = Task.objects.get(id=task_id, project=project)

    except Project.DoesNotExist:
        return redirect('index')
    except Task.DoesNotExist:
        return redirect('index')

    if request.POST:
        old_form = TaskUpdateForm(instance=task)
        form = TaskUpdateForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect('task', account = request.user, project_slug=project_slug, task_id=task_id)
        else:
            print("Task "+task_id+" update failed.")
    
    else:
        form = TaskUpdateForm(instance=task)
    
    return render(request, 'update_task.html', {'form': form})



#TIME TRACKER
def track_time_view(request, account, project_slug, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return HttpResponse("Task "+task_id+" does not exist!")

    creation_date = datetime.now()
    if request.POST:

        form = TimelogCreationForm(request.POST, task=task)

        if form.is_valid():
            form.save()
            return redirect('timelog', account = request.user, project_slug=project_slug, task_id = task_id)
    else:

        form = TimelogCreationForm(task=task)

    context = {
        'form':form
    }
    
    return render(request, 'track_time.html', context)

def timelog_view(request, account, project_slug, task_id):
    if not request.user.is_authenticated:
        return redirect('index') 

    try:
        project = Project.objects.get(slug = project_slug)
        task = Task.objects.get(id=task_id, project=project)
        timelog_recs = Timelog.objects.filter(task_id=task).order_by("-date")
    except Project.DoesNotExist:
        return redirect('index')
    except Task.DoesNotExist:
        return redirect('index')
    except Timelog.DoesNotExist:
        timelog_recs = None

    context = {
        'project': project,
        'task': task,
        'timelog_recs': timelog_recs
    }

    return render(request, "timelog.html", context)
#set session with time track start ckick/end tracking
    # if 'time_track' not in request.session:
    #     request.session['time_track'] = {
    #         'task_id': task_id,
    #         'start_time': datetime.now().timestamp()
    #     }
    # else:  
    #     time_spent = datetime.now().timestamp() - request.session['time_track']['start_time']
        

    #     minutes = ((time_spent/60)%60)/60.0
    #     hours = time_spent/3600

    #     time_spent = hours+minutes
    #     time_spent = float("{:.2f}".format(time_spent))

    #     try:
    #         time_log = Timelog.objects.get(task_id=task)

    #         time_log.hours_spent = time_spent + float(time_log.hours_spent)

    #         time_log.save()
    #     except Timelog.DoesNotExist:
    #         del request.session['time_track']
    #         return HttpResponse("Timelog for "+task.name+" does not exist!")
            
    #     del request.session['time_track']










#DEPRECATED
#MY_PROJECTS
# def user_my_projects(request, account):
#     user = request.user   
#     if not user.is_authenticated:
#         return redirect('index')

#     user = Userprofile.objects.get(email = user)

#     try:
#         user_projects = Project.objects.filter(slug__regex=r'.*-'+str(user.id))

#     except Project.DoesNotExist:
#         user_projects = None

#     context = {
#         'user': user,
#         'projects': user_projects,
#     }

#     return render(request, 'my_projects.html', context)

# def create_project(request, account):
#     if not request.user.is_authenticated:
#         return redirect('index')

    
#     if request.method == "POST":
#         form = ProjectCreateForm(request.POST, project_name=request.POST['name'], user_id=request.user.id)

#         #if form.is_valid():
#         form.save()
#         return redirect('my_projects', account = request.user,)
#     else:
#         form = ProjectCreateForm(project_name='', user_id='')

#     return render(request, 'create_project.html', {'form': form})

# def update_project(request, account, project_slug=None):
#     if not request.user.is_authenticated or project_slug==None:
#         return redirect('index')

#     project = Project.objects.get(slug=project_slug)

#     if request.POST:
#         form = ProjectCreateForm(request.POST, instance=project, project_name=request.POST['name'], user_id=request.user.id)
#         if form.is_valid():
#             form.save()
#             return redirect('my_projects', account = request.user)
#     else:
#         form = ProjectCreateForm(instance=project, project_name='', user_id='')

#     #get all tasks of project
#         tasks = Task.objects.filter(project=project) 

#         hours_spent = []
#         for task in tasks:
#             hours_spent.append(Timelog.objects.get(task_id=task).hours_spent)

#         context = {
#             'form': form,
#             'project_slug': project_slug,
#             'tasks': tasks,
#             'hours_spent': hours_spent
#             }

#     return render(request, 'update_project.html', context)


# #TASKS
# def create_task(request, account, project_slug=None):

#     if not request.user.is_authenticated or project_slug==None:
#         return redirect('index')

    
#     if request.POST:
#         form = TaskCreateForm(request.POST,creator=Userprofile.objects.get(id=request.user.id), project=Project.objects.get(slug=project_slug))
        
#         if form.is_valid():
            
#             task = form.save()
        
#             time_log = Timelog()
#             time_log.hours_spent = 0
#             time_log.task_id = task
#             time_log.comment = ''

#             time_log.save()
                       
#             return redirect('update_project', account = request.user, project_slug=project_slug)

#         print(form)
#     else:
#         form = TaskCreateForm(creator=Userprofile.objects.get(id=request.user.id), project=Project.objects.get(slug=project_slug))
    
#     project_name = Project.objects.get(slug=project_slug).name

#     return render(request, 'create_task.html', {'form':form, 'project_name': project_name})

# def delete_task(request, account, project_slug=None, task_id=None):
#     if not request.user.is_authenticated:
#         return redirect('index')

    
#     #check if project with task id exists
#     try:
#         project = Project.objects.get(slug = project_slug)
#         task = Task.objects.get(id=task_id, project=project )
#         task.delete()
#     except Project.DoesNotExist:
#         print(f"Could not delete {task_id}. Project DoesNotExist")
#     except Task.DoesNotExist:
#         print(f"Could not delete {task_id}. Task DoesNotExist")

#     return redirect('update_project', account = request.user, project_slug=project_slug)

# def update_task(request, account, project_slug=None, task_id=None):
#     if not request.user.is_authenticated:
#         return redirect('index')
    
#     try:
#         project = Project.objects.get(slug = project_slug)
#         task = Task.objects.get(id=task_id, project=project)

#     except Project.DoesNotExist:
#         return redirect('index')
#     except Task.DoesNotExist:
#         return redirect('index')

#     if request.POST:
#         form = TaskUpdateForm(request.POST, instance=task)

#         if form.is_valid():
#             form.save()
#             return redirect('update_project', account = request.user, project_slug=project_slug)
#         else:
#             print("Task "+task_id+" update failed.")
    
#     else:
#         form = TaskUpdateForm(instance=task)
    
#     return render(request, 'update_task.html', {'form': form})


