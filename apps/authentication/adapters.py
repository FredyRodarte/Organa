from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class CustomAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, *, email_verification, signal_kwargs, email, signup, redirect_url):
        if signup:
            # Add success message in Spanish
            messages.success(request, "Tu cuenta ha sido creada exitosamente. Por favor, inicia sesión con tus credenciales.")
            # Return the redirect response directly. This short-circuits the login flow, 
            # preventing automatic login and sending the user to the login screen.
            return redirect(reverse('account_login'))
        
        return super().pre_login(
            request,
            user,
            email_verification=email_verification,
            signal_kwargs=signal_kwargs,
            email=email,
            signup=signup,
            redirect_url=redirect_url
        )
