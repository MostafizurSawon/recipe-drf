from django.urls import path
from .views import ContactUsAPIView, ContactUsListAPIView

urlpatterns = [
    path('', ContactUsAPIView.as_view(), name='contact-us'),  # POST to create a message
    path('messages/', ContactUsListAPIView.as_view(), name='contact-us-messages'),  # GET to list messages
]