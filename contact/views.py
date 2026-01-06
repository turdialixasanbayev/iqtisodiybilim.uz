from django.shortcuts import render, redirect
from django.views import View
from .models import Contact
from django.contrib import messages


class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')
    
    def post(self, request):
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not all([full_name, email, message]):
            messages.error(request, "Please fill in all required fields before submitting the form")
            return redirect('contact')

        Contact.objects.create(full_name=full_name, email=email, message=message)

        messages.success(request, "Your message has been sent successfully. We'll get back to you as soon as possible")

        return redirect('contact')
