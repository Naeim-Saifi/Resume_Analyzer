from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .forms import SignUpForm, LoginForm
from .models import CustomUser


class SignUpView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'authentication/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'authentication/login.html'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        try:
            user_obj = CustomUser.objects.get(email=email)
            # user = authenticate(self.request, username=user_obj.username, password=password)
            user = authenticate(self.request, email=email, password=password)
            
            if user:
                login(self.request, user)
                messages.success(self.request, f'Welcome back, {user.first_name}!')
                
                # Role-based redirect
                if user.role == 'admin':
                    return redirect('jobs:admin_dashboard')
                else:
                    return redirect('dashboard')
            else:
                messages.error(self.request, 'Invalid credentials.')
                return self.form_invalid(form)
        except CustomUser.DoesNotExist:
            messages.error(self.request, 'Invalid credentials.')
            return self.form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard_view(request):
    """Main dashboard after login"""
    context = {
        'user': request.user,
        'recent_applications': None  # Will be populated later
    }
    return render(request, 'authentication/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')