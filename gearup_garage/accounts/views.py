from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegistration
from .models import account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    
    if request.user.is_authenticated:
        # Redirect the user to the home page (or any other appropriate page)
        return redirect('home')
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')
            username = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            username = email.split("@")[0]
            
            user = account.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.phone_number = phone_number
            user.save()
            
            # user activation
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_mail.html',{
                'user'  : user,
                'domain': current_site,
                'uid'   : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
                
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
                    
            messages.success(request, 'Activation link has been sent to mail, please verify to finish registration process')
            return redirect('register')
    
    else:
        form = UserRegistration()
    context = {
        'form' : form
        }
    return render (request, 'accounts/register.html', context)

def login(request):
   
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")

    return render(request, 'accounts/login.html')

@login_required(login_url= login  )
def logout(request):
    auth.logout(request)
    messages.success(request, "You are Logged out")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been verifed, Welcome to gearup garage ')
        return redirect('login')
    else:
        messages.error(request, 'invalid activation link, please try again')
        return redirect('register')