from django.urls import path, include
from . import views

urlpatterns = [
    path('terms/', views.TermsRetrieveUpdateAPIView.as_view()),
    path('policy/', views.PolicyRetrieveUpdateAPIView.as_view()),
    path('faqs/', views.FAQListCreateAPIView.as_view()),
    path('faqs/<int:pk>/', views.FAQRetrieveUpdateDestroyAPIView.as_view()),
    path('contacts/form/', views.ContactUsCreateAPIView.as_view()),
    path('contacts/', views.ContactUsListAPIView.as_view()),

]