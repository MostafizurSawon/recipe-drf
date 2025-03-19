# from django.shortcuts import render
# from rest_framework import viewsets
# from . import models
# from . import serializers

# class ContactusViewset(viewsets.ModelViewSet):
#     queryset = models.ContactUs.objects.all()
#     serializer_class = serializers.ContactUsSerializer
    

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ContactUs
from .serializers import ContactUsSerializer

class ContactUsAPIView(APIView):
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Message sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)