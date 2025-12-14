from django.urls import path
from . import views_api

urlpatterns = [
    # Authentication
    path('auth/register/', views_api.register, name='register'),
    path('auth/login/', views_api.login, name='login'),
    path('auth/logout/', views_api.logout, name='logout'),
    path('auth/me/', views_api.current_user, name='current_user'),
    
    # Complaints - Citizen
    path('complaints/create/', views_api.ComplaintCreateView.as_view(), name='complaint_create'),
    path('complaints/all/', views_api.AllComplaintsView.as_view(), name='all_complaints'),
    path('complaints/my/', views_api.MyComplaintsView.as_view(), name='my_complaints'),
    path('complaints/<int:pk>/', views_api.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaints/<int:pk>/upvote/', views_api.upvote_complaint, name='upvote_complaint'),
    path('complaints/<int:pk>/logs/', views_api.complaint_logs, name='complaint_logs'),
    
    # Complaints - Department Admin
    path('department/complaints/', views_api.department_complaints, name='department_complaints'),
    path('complaints/<int:pk>/assign/', views_api.assign_to_worker, name='assign_to_worker'),
    path('complaints/<int:pk>/update-status/', views_api.update_complaint_status, name='update_complaint_status'),
    path('complaints/<int:pk>/reject/', views_api.reject_complaint, name='reject_complaint'),
    path('complaints/<int:pk>/delete/', views_api.delete_complaint, name='delete_complaint'),
    
    # Worker
    path('worker/assignments/', views_api.worker_assignments, name='worker_assignments'),
    
    # Attendance
    path('attendance/mark/', views_api.mark_attendance, name='mark_attendance'),
    path('attendance/', views_api.get_attendance, name='get_attendance'),
    
    # Categories & Departments
    path('categories/', views_api.get_categories, name='get_categories'),
    path('departments/', views_api.get_departments, name='get_departments'),
    path('offices/', views_api.get_offices, name='get_offices'),
    
    # Dashboard
    path('dashboard/stats/', views_api.dashboard_stats, name='dashboard_stats'),
]
