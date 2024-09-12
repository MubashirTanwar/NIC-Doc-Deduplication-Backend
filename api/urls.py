from django.urls import path
from . import views

urlpatterns = [
    path('text/', views.ProcessPDF.as_view(), name='get_text'),
    path('ocr/', views.OCR.as_view(), name='ocr'),
    path('es/', views.ES.as_view(), name='es'), 
    path('user/', views.CreateUserView.as_view(), name='create_user'),
    path('apikey/', views.CreateApiKey.as_view(), name='apikey'),  
        path('users/', views.user_list, name='user_list'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
      path('users/toggle_active/<int:user_id>/', views.toggle_active, name='toggle_active'),
]