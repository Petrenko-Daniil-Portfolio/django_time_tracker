"""time_tracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from apps.core.views import index
from apps.userprofile.views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('tinymce/', include('tinymce.urls')),

    path('', index, name='index'),

    #accaunt
    path('account/signup/', signup_view, name='signup'),  
    path('account/login/', login_user_view, name='login'),  
    path('<account>/logout/', logout_user_view, name='logout'),
    path('<account>/', user_account_view, name='account'),

    #project
    path('<account>/my_projects', user_projects_view, name='user_projects'),
    path('<account>/my_project/<project_slug>', user_project_view, name='user_project'),

    #task
    path('<account>/<project_slug>/tasks/<task_id>', task_view, name='task'),
    path('<account>/<project_slug>/update_task/<task_id>', update_task, name='update_task'),

    #time tracking
    path('<account>/<project_slug>/<task_id>/track_time', track_time_view, name='track_time'),
    path('<account>/<project_slug>/<task_id>/timelog', timelog_view, name='timelog')

    # DEPRECATED
    #admin functionality
    # path('<account>/<project_slug>/create_task', create_task, name='create_task'),
    # path('<account>/<project_slug>/delete_task/<task_id>', delete_task, name='delete_task'),
    

    # path('<account>/my_projects/', user_my_projects, name='my_projects'),
    # path('<account>/create_project/', create_project, name='create_project'),

    # path('<account>/update_project/', update_project, name='update_project'),
    # path('<account>/update_project/<project_slug>/', update_project, name='update_project'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
