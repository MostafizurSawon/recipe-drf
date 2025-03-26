
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import ContactUs
from .serializers import ContactUsSerializer
from users.permissions import role_based_permission_class

# API to create a new contact message (accessible to all)
class ContactUsAPIView(APIView):
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API to list all contact messages (accessible only to admins)
class ContactUsListAPIView(generics.ListAPIView):
    queryset = ContactUs.objects.all().order_by('-created_at')
    serializer_class = ContactUsSerializer
    permission_classes = [IsAuthenticated, role_based_permission_class(allowed_roles=['Admin'])]