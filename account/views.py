from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import EmailOTP
from django.contrib.auth.hashers import make_password
from .utils import generate_otp 
from django.contrib.auth import update_session_auth_hash


def home_view(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        
        user = authenticate(request, email=email, password=password)
        
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")

        next_url = request.GET.get('next')
        if next_url:
            next_url = next_url.strip()
        else:
            next_url = "home" #home
        return redirect(next_url)
    return render(request, 'account/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
            return render(request, 'account/register.html')
    

        user = User.objects.create_user(username=username, email=email, password=password)
        
        #add utils.py file
        generate_otp(email)

        return redirect(f'/verify-otp/?email={email}')

    return render(request, 'account/register.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('home') 


@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            # password change korle django sesson ke inactive kore dei, tokhn abr login korte hoi but eta use korle session ke refresh kore and active theke
            update_session_auth_hash(request, request.user)  
            messages.success(request, "Password changed successfully.")
            return redirect('home') #home

    return render(request, 'account/change_password.html')



def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            generate_otp(email)  # Generate and send OTP
            messages.success(request, "OTP has been sent to your email.")
            return redirect('request_otp')
        else:
            messages.error(request, "No account found with this email.")
    return render(request, 'account/forgot_password.html')



def reset_password_view(request):
    email = request.GET.get('email')
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate password match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'account/reset_password.html', {'email': email})

        # Check OTP validity
        otp_obj = EmailOTP.objects.filter(email=email, code=otp).order_by('-created_at').first()
        if otp_obj and not otp_obj.is_expired():
            user = User.objects.filter(email=email).first()
            if user:
                user.password = make_password(new_password)  # Hash password
                user.save()
                otp_obj.delete()
                messages.success(request, "Password reset successful! Please log in.")
                return redirect('user_login')
            else:
                messages.error(request, "User not found.")
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'account/reset_password.html', {'email': email})

           

#OTP Verification
def request_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        generate_otp(email)
        return redirect('verify_otp')
    


def verify_otp_view(request):
    email = request.GET.get('email')
    print(email)
    print("++++++++++++===============================otp=")

    if request.method == 'POST':
        otp = request.POST.get('otp')
        print(otp)
        otp_obj = EmailOTP.objects.filter(email=email, code=otp).order_by('-created_at').first()
        print(otp_obj)

        if otp_obj and not otp_obj.is_expired():
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "User not found. Please register first.")
                return redirect('register')

            user.is_active = True
            user.save()
            login(request, user)
            otp_obj.delete()

            messages.success(request, "OTP verified successfully! You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'account/verify_otp.html', {'email': email})

    
           
               
       

           