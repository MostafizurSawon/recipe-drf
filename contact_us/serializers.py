# contact_us/serializers.py
from rest_framework import serializers
from .models import ContactUs

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty or whitespace.")
        return value

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty or whitespace.")
        return value