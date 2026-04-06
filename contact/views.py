from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from common.permissions import IsAdminOrReadOnly
from helpers.response import response, error_response
from .models import Terms, Policy, FAQ, ContactUs
from .serializers import TermsSerializer, PolicySerializer, FAQSerializer, ContactUsSerializer

# Create your views here.



class TermsRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Terms.objects.all()
    serializer_class = TermsSerializer
    http_method_names = ['get','patch']
    permission_classes = [IsAdminOrReadOnly]
    
    def get_object(self):
        terms, created = Terms.objects.get_or_create(pk=1)
        return terms
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response(details="Terms retrieved successfully", data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return response(details="Terms updated successfully", data=serializer.data)
        return error_response(details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class PolicyRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    http_method_names = ['get', 'patch']
    permission_classes = [IsAdminOrReadOnly]
    
    def get_object(self):
        policy, created = Policy.objects.get_or_create(pk=1)
        return policy
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response(details="Policy retrieved successfully", data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return response(details="Policy updated successfully", data=serializer.data)
        return error_response(details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class FAQListCreateAPIView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return response(details="FAQs retrieved successfully", data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return response(details="FAQ created successfully", data=serializer.data, status_code=status.HTTP_201_CREATED)
        return error_response(details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class FAQRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    lookup_field = 'pk'
    http_method_names = ['get', 'patch', 'delete']
    permission_classes = [IsAdminOrReadOnly]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response(details="FAQ retrieved successfully", data=serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return response(details="FAQ updated successfully", data=serializer.data)
        return error_response(details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response(details="FAQ deleted successfully", status_code=status.HTTP_204_NO_CONTENT)


class ContactUsCreateAPIView(generics.CreateAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            contact = serializer.save()
            
            try:
                context = {
                    'full_name': contact.full_name,
                    'email': contact.email,
                    'phone_number': contact.phone_number or 'Not provided',
                    'message': contact.message,
                    'timestamp': contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                admin_subject = f"New Contact Us Message from {contact.full_name}"
                admin_html_message = render_to_string('emails/contact_admin_notification.html', context)
                admin_plain_message = strip_tags(admin_html_message)
                
                send_mail(
                    subject=admin_subject,
                    message=admin_plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['asibahmed4@gmail.com'],
                    html_message=admin_html_message,
                    fail_silently=False,
                )
                
                # User auto-reply email
                user_subject = "Thank you for contacting Port A Vacation"
                user_html_message = render_to_string('emails/contact_user_confirmation.html', context)
                user_plain_message = strip_tags(user_html_message)
                
                send_mail(
                    subject=user_subject,
                    message=user_plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[contact.email],
                    html_message=user_html_message,
                    fail_silently=True,
                )
                
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
            
            return response(
                details="Your message has been sent successfully. We will get back to you soon.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response(details=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class ContactUsListAPIView(generics.ListAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return response(details="Contact messages retrieved successfully", data=serializer.data, status_code=status.HTTP_200_OK)