from django.urls import path

from . import views

urlpatterns = [
    path('', views.TodoListView.as_view(), name='home'),
    path('todos/<int:pk>/edit/', views.TodoUpdateView.as_view(), name='todo_edit'),
    path('todos/<int:pk>/delete/', views.TodoDeleteView.as_view(), name='todo_delete'),
    path('todos/<int:pk>/toggle/', views.toggle_resolved, name='todo_toggle'),
]

