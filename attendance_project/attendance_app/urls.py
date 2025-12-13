from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.teacher_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.teacher_logout, name='logout'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('student_login/',views.student_login,name='student_login'),
    path('view/', views.view_attendance, name='view_attendance'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('student_logout/', views.student_logout, name='student_logout'),

]
