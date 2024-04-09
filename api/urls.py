from django.urls import path
from . import views

urlpatterns = [
    path('text/', views.ProcessPDF.as_view(), name='get_text'),
    path('ocr/', views.OCR.as_view(), name='ocr'),
    path('es/', views.ES.as_view(), name='es'),
]