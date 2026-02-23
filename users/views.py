from django.shortcuts import render, redirect
from .forms import RegisterForm, EntryForm
from django.contrib.auth import authenticate, login
import random
from datetime import datetime, timedelta
from .models import TemporaryMemory
from mainapp.models import UserProfile
from django.contrib import messages
from django.contrib.auth.models import User
import time
from .twilio_service import send_sms

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    temp_id = request.session.get('temp_id')
    try:
        quary = TemporaryMemory.objects.get(id=temp_id)
    except:
        return redirect('/accounts/joinAlem/')

    if quary.code_verified and not quary.code_expired:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                existing_profile = UserProfile.objects.filter(phone=quary.phone).first()

                if existing_profile:
                    login(request, existing_profile.user_name)
                    quary.delete()
                    return redirect('/')
                
                user = form.save(commit=False)
                user.username = form.cleaned_data['username']
                user.is_active = True
                user.set_unusable_password()
                user.save()
                print("USER ID:", user.id)
                print("PROFILE EXISTS:", UserProfile.objects.filter(user_name=user).exists())
                print (quary.phone)
                if UserProfile.objects.filter(phone=quary.phone).exclude(user_name=user).exists():
                    messages.error(request, "Phone already registered")
                    return redirect('/accounts/login/')
                profile = user.userprofile
                profile.phone = quary.phone
                profile.save()
                login(request, user)
                quary.delete()
                return redirect('/')
            else:
                print (form.errors)
        else:
            form = RegisterForm()
    else:
        quary.delete()
        return redirect('/accounts/joinAlem/')

    return render(request, 'registers.html', {'form': form, "phone": quary.phone})

def joinAlem(request):
    print("VIEW HIT", request.method)
    if request.user.is_authenticated:
        return redirect('/')

    key = random.randint(10000, 99999)

    if request.method == 'POST':
        print ("POST RECEIVED", request.POST)
        data = request.POST.copy()
        data['phone'] = data.get("full_phone")

        form = EntryForm(data)
        print("FORM ERRORS:", form.errors)
        if form.is_valid():
            phone = form.cleaned_data["phone"]

            q = TemporaryMemory.objects.filter(phone=phone).first()
            if q and not q.code_expired:
                request.session['temp_phone'] = phone
                return redirect('/accounts/verify/')

            if q:
                q.delete()

            if User.objects.filter(userprofile__phone=phone).exists():
                messages.error(request, "This phone number is already registered.")
                return redirect('/accounts/login/')
            temp = TemporaryMemory.objects.create(
                phone=phone,
                code=key
            )

            send_sms(phone, key)

            request.session['temp_phone'] = phone
            return redirect('/accounts/verify/')
    else:
        form = EntryForm()

    return render(request, 'join.html', {"form": form})

def login_view(request):
    print ("sup")
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        print (f"POST DATA :{request.POST}" )
        phone = request.POST.get("full_phone")
        print(phone)
        if not phone:
            messages.error(request, "Enter phone number")
            return redirect('/accounts/login/')

        key = random.randint(10000, 99999)
        
        if not User.objects.filter(userprofile__phone=phone).exists():
            messages.error(request, "This phone number is not registered.")
            return redirect('/accounts/register/')
        
        q = TemporaryMemory.objects.filter(phone=phone).delete()

        TemporaryMemory.objects.create(
            phone=phone,
            code=key
        )

        send_sms(phone, key)

        request.session['temp_phone'] = phone

        return redirect('/accounts/login_verify/')

    return render(request, "login.html")

def login_verify(request):

    if request.user.is_authenticated:
        return redirect('/')

    temp_phone = request.session.get('temp_phone')

    if not temp_phone:
        return redirect('/accounts/login/')

    quary = TemporaryMemory.objects.filter(phone=temp_phone).order_by('-created_at').first()

    if not quary:
        return redirect('/accounts/login/')

    if request.method == "POST":

        code_input = request.POST.get('verification_code')

        if quary.code_expired:
            quary.delete()
            messages.error(request, "Code expired")
            return redirect('/accounts/login/')
        if quary.attempts >= 5:
            quary.delete()
            messages.error(request, "Too many attempts, request a new code")
        if code_input.isdigit() and int(code_input) == quary.code:

            try:
                user = User.objects.get(userprofile__phone=temp_phone)

                login(request, user)

                quary.delete()

                return redirect('/')

            except User.DoesNotExist:

                # new user → go register
                request.session['temp_id'] = quary.id
                return redirect('/accounts/register/')

        else:
            messages.error(request, "Wrong code")
            quary.attempts += 1
            quary.save()
        

    return render(request, "login_verify.html")
def otp_verify(request):
    if request.user.is_authenticated:
        return redirect('/')

    temp_phone = request.session.get('temp_phone')
    print (temp_phone)
    try:
        quary = TemporaryMemory.objects.filter(phone=temp_phone).order_by('-created_at').first()
        print (quary.code)
    except:
        messages.error(request, "Invalid Verification Attempt")
        return redirect('/accounts/joinAlem/')

    if request.method == 'POST':
        if quary.code_expired:
            messages.error(request, 'Code expired')
            quary.delete()
            return redirect('/accounts/joinAlem/')
        code_input = request.POST.get('verification_code', '').strip()
        quary.attempts += 1
        if quary.attempts >= 5:
            quary.delete()
            messages.error(request, "Too many attempts")
            return redirect('/accounts/joinAlem/')
        if code_input.isdigit() and int(code_input) == quary.code:

            quary.code_verified = True
            quary.save()
            request.session['temp_id'] = quary.id
            return redirect('/accounts/register/')
        else:
            messages.error(request, 'Wrong code')

    return render(request, 'verify.html')