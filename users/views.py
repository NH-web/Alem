from django.shortcuts import render, redirect
from .forms import RegisterForm, EntryForm
from django.contrib.auth import login
import random
from datetime import datetime, timedelta
from .models import TemporaryMemory
from django.contrib import messages
from django.contrib.auth.models import User
import time
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
                user = form.save(commit=False)
                user.email = quary.email
                print (user.email)
                form.save()
                login(request, user)  # log in after registration
                quary.delete()
                return redirect('/')  # redirect to homepage
        else:
            form = RegisterForm()
    else:
        quary.delete()
        return redirect('/accounts/joinAlem/')
    return render(request, 'register.html', {'form': form,"email":quary.email})

def joinAlem(request):
    if request.user.is_authenticated:
        return redirect('/')
    print ("Entered")
    key = random.randint(10000,99999)
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request,"The email is already registered. please use a different email")
                return redirect("/accounts/login/")
                #return redirect("/accounts/login/")
            
            q = TemporaryMemory.objects.filter(email=email).first()
            if q:
                if not q.code_expired:
                    request.session['temp_email'] = email
                    return redirect('/accounts/verify/')
                else:
                    q.delete()
            user = form.save(commit=False)
            user.code = key
            form.save()
            request.session['temp_email'] = email
            return redirect(f'/accounts/verify/')
    else:
        form = EntryForm()
        print ("error")
    return render(request, 'join.html', {"form":form})

def otp_verify(request):
    if request.user.is_authenticated:
        return redirect('/')
    temp_email = request.session.get('temp_email')
    try:
        quary = TemporaryMemory.objects.get(email=temp_email)
    except:
        messages.error(request, "Invalid Verification Attempt")
        return redirect('/accounts/joinAlem/')
    print (f"Stored: {quary.code}")

    if request.method == 'POST':
        if quary.code_expired:
            messages.error(request,'Verification Code expired, please try again. ')
            quary.delete()
            return redirect('/accounts/joinAlem/')
        
        print (f"request: {request.POST.get('verification_code')}")
        if int(request.POST.get('verification_code')) == int(quary.code):
            quary.code_verified = True
            quary.save()
            request.session['temp_id'] = quary.id
            return redirect(f'/accounts/register/')
        else:
            messages.error(request, 'Wrong Verification Code')
            

    return render(request, 'verify.html')
