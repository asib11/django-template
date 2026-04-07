from rest_framework import serializers
from .models import Terms, Policy, FAQ, ContactUs



class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': False}
        }


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': False}
        }


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'full_name', 'email', 'phone_number', 'message', 'is_replied', 'created_at']
        read_only_fields = ['id', 'is_replied', 'created_at']
        extra_kwargs = {
            'phone_number': {'required': False}
        }