from django.shortcuts import render,redirect, get_object_or_404
from .models import TravelInfo, Notification, Follow, Comments
from .forms import TravelFormCreate, SearchForm, UserProfile, SearchUsers, EditProfileForm, EditPostForm
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseForbidden
# Create your views here.

def homepage(request):
    if request.user.is_authenticated:
        return home(request)
    else:
        return render(request, 'homepage.html')
@login_required
def home(request):
    title = "Homepage"
    username = request.user
    my_pp = UserProfile.objects.get(user_name=username)

    users_list = User.objects.all().count()
    
    verified_users_list = User.objects.filter(userprofile__is_verified=True).count()
    initial_data = {
        'departure_country':'Afghanistan',
        'destination_country':'Afghanistan'
    }
    quarysets = TravelInfo.objects.filter(Q(departure_date__gte=timezone.now().date())).order_by('-created_at')[:15]
    if request.method == 'POST':
        form = SearchForm(request.POST)
        today = date.today()
        initial_data = {
            'departure_country':f"{form['departure_country'].value()}",
            'destination_country':f"{form['destination_country'].value()}"
        }
        try:
            max_date = datetime.strptime(form['departure_date'].value(), "%Y-%m-%d").date()
            quarysets = TravelInfo.objects.filter(departure_country__icontains=form['departure_country'].value(),destination_country__icontains=form['destination_country'].value(),departure_date__range=[today, max_date])
        except:
            quarysets = TravelInfo.objects.filter(Q(departure_date__gte=timezone.now().date()),departure_country__icontains=form['departure_country'].value(),destination_country__icontains=form['destination_country'].value())
        
    if my_pp.is_verified:
        is_verified = "verified"
    else:
        is_verified = "unverified"
    form = SearchForm(initial=initial_data)
    context = {
        "quaryset":quarysets,
        "users_count":users_list,
        "verified_count":verified_users_list,

        "title":title,
        "today":timezone.now().date(),
        "username":username,
        "form":form,
        "my_pp":my_pp,
        "is_verified":is_verified,
        
    }
    return render(request,'home3.html',context)
@login_required
def new_travel(request):
    title = "New Travel Info"
    username = request.user
    today = timezone.now().date()
    my_pp = UserProfile.objects.get(user_name=username)
    if request.method == 'POST':
        today = timezone.now().date()
        upload_count = TravelInfo.objects.filter(
            user=username,
            created_at__date=today
        ).count()
        if my_pp.is_verified == False and upload_count >= 2:
            return HttpResponseForbidden(
                render(request, 'free_user.html',{'messages':'You have reached the Limit of 2 posts/day for free users.','my_pp':my_pp,'today':today})
                )
        
        form = TravelFormCreate(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            print ("Done")
            return redirect('/')
    else:
        form = TravelFormCreate()
        

    return render(request, 'add2.html', {"form":form, "today":today, "my_pp":my_pp})

@login_required
def search(request):
    username = request.user
    my_pp = UserProfile.objects.get(user_name=username)
    if request.method == "POST":
        form = SearchForm(request.POST)
        today = date.today()
        try:
            max_date = datetime.strptime(form['departure_date'].value(), "%Y-%m-%d").date()
            quaryset = TravelInfo.objects.filter(departure_country__icontains=form['departure_country'].value(),destination_country__icontains=form['destination_country'].value(),max_weight__gte=form['max_weight'].value(),departure_date__range=[today, max_date])
        except:
            quaryset = TravelInfo.objects.filter(Q(departure_date__gte=timezone.now().date()),departure_country__icontains=form['departure_country'].value(),destination_country__icontains=form['destination_country'].value(),max_weight__gte=form['max_weight'].value())
        
        context = {
            "form":form,
            "quaryset":quaryset,
            "my_pp":my_pp,
            "today":timezone.now().date(),
        }
    else:
        form = SearchForm()
        context = {
        "form":form,
        "my_pp":my_pp,
        "today":timezone.now().date(),
        }
    return render(request, 'fflight.html', context)

@login_required
def profile(request, pk):
    user = User.objects.get(username=pk)
    profile = user.userprofile
    is_following = profile.followers.filter(id=request.user.id).exists()
    my_pp = UserProfile.objects.get(user_name=request.user)
    quarysets = TravelInfo.objects.filter(user=user).order_by('-created_at')
    if my_pp.is_verified:
        is_verified = "verified"
    else:
        is_verified = "unverified"
    
    context = {
        'usern':user,
        'username':request.user,
        'profile':profile,
        'is_following':is_following,
        'is_verified':is_verified,
        'quarysets':quarysets,
        'my_pp':my_pp,
        'today':date.today(),
    }
    
    return render(request, 'profileig.html', context)

@login_required
def search_user(request):
    uname = request.user
    results = []
    my_pp = UserProfile.objects.get(user_name=uname)
    if request.method == 'POST':
        form = SearchUsers(request.POST)
        if form.is_valid():
            username_quary = form.cleaned_data.get('username')
            results = User.objects.filter(Q(username__icontains=username_quary))
    else:
        form = SearchUsers()
        
    context = {
        "form":form,
        "my_pp":my_pp,
        "results":results,
    }
    
    return render(request, 'fusers.html', context)

        


@login_required
def track_follow(request,pk,opp):
    user = User.objects.get(username=pk)
    my_pp = UserProfile.objects.get(user_name=request.user)
    profile = user.userprofile
    if opp == "followers":
        title = "Followers"
        is_following = profile.followers.all()
        print (is_following)
    else:
        title = "Following"
        is_following = user.following.all()
        for i in is_following:
            print (i.user_name)
    
    return render(request,'toggle_follow2.html', {"usern":user,"title":title, "is_following":is_following, "my_pp":my_pp,"profile":profile})


@login_required
def notifiy(request):
    username = request.user
    my_pp = UserProfile.objects.get(user_name=username)
    notification = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, 'notifi.html', {'notifications':notification,'my_pp':my_pp})

@login_required
def get_unread_notifications(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread})

@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.userprofile

    if request.user in profile.followers.all():
        profile.followers.remove(request.user)

    else:
        profile.followers.add(request.user)


    return redirect(f'/profile/{username}')


@login_required
def edit_profile(request):
    username =request.user
    initaial_data = {
        "bio":request.user.userprofile.bio,
    }
    my_pp = UserProfile.objects.get(user_name=username)
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.userprofile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/profile/{request.user.username}')
    else:
        form = EditProfileForm(instance=request.user.userprofile, user=request.user)
    return render(request, 'edit_profile.html', {"form":form,"my_pp":my_pp})    

@login_required
def edit_post(request, post_id):
    today = timezone.now().date()
    post = get_object_or_404(TravelInfo, id=post_id, user=request.user)
    initial_data = {
        "departure_country": f"{post.departure_country}",
        "destination_country":f"{post.destination_country}",
    }
    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'post updated successfully')
            return redirect(f'/profile/{request.user.username}')
    else:
        form = EditPostForm( initial=initial_data, instance=post)
    return render(request, 'edit_post.html',{'form':form, 'post':post, 'today':today})

@login_required
def delete_post(request,post_id):
    post = get_object_or_404(TravelInfo, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request,"post deleted successfully")
        return redirect(f'/profile/{request.user.username}')
    return render(request, 'confirm_delete.html',{"post":post})
def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

