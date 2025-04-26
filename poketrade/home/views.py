from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after successful signup
            return redirect('index')  # Redirect to the home page or another page
    else:
        form = CustomUserCreationForm()  # Instantiate an empty form for GET requests

    return render(request, 'accounts/Signup.html', {'form': form})

def login_view(request):
    template_data = {}

    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/Login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
            username = request.POST.get('username'),
            password = request.POST.get('password'),
            user = authenticate(request, username = username, password = password)
            if user is None:
                template_data['error'] = 'The username or password is incorrect.'
                return render(request, 'accounts/templates/accounts/login.html',
                {'template_data': template_data})
    else:
            auth_login(request, user)
            return redirect('home.index')