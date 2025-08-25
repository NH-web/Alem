from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid
import random
import pycountry
# Create your models here.

class TravelInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=False, blank=False)
    
    departure_country = models.CharField(max_length=100, blank=False, null=False)
    destination_country = models.CharField(max_length=100, blank=False, null=False)
    departure_date = models.DateField()
    max_weight = models.IntegerField(default=0, null=False, blank=False)
    note = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def get_departure_country_name(self):
        country = pycountry.countries.get(alpha_2=self.departure_country)
        return country.name if country else self.departure_country

    def get_destination_country_name(self):
        country = pycountry.countries.get(alpha_2=self.destination_country)
        return country.name if country else self.destination_country
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.user.username}-{self.created_at}")
            slug = base_slug
            while TravelInfo.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = slug
        super().save(*args, **kwargs)
    def __str__(self):
        return self.user.username + ' ' + self.departure_country + ' -> ' + self.destination_country + ' Created : ' + str(self.created_at)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_set")
    created_at = models.DateTimeField(auto_now_add=True)



@receiver(post_save, sender=TravelInfo)
def update_notification(sender, instance, created, *args, **kwargs):
    if created:
        usern = instance.user
        try:
            profile = usern.userprofile
        except UserProfile.DoesNotExist:
            return
        
        followers = profile.followers.all()
        q = User.objects.get(username=instance.user)
        for follower in followers:

            Notification.objects.create(user=follower, sender=q, message=f"{instance.user} Posted New Travel Info")
    
class Comments(models.Model):
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=300, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
class UserProfile(models.Model):
    dp = ['darkyellowduck_7G9vUMD','monkeypink_k36Pd79','monkeypinkblack_ajymkIP','skull_godDg1m','monkeypink']
    user_name = models.OneToOneField(User, on_delete=models.CASCADE)
    #user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50,null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to="images/", default=f"images/{random.choice(dp)}.jpg")
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)


    def __str__(self):
        return self.user_name.username
    def is_followed_by(self, user):
        return self.followers.filter(id=user.id).exists()

   
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user_name=instance)
    else:
        #instance.UserProfile.save()
        profile, _ = UserProfile.objects.get_or_create(user_name=instance)
        profile.save()

@receiver(m2m_changed, sender=UserProfile.followers.through)
def notify_on_follow(sender, instance, action, reverse, pk_set, **kwargs):
    """
    This will send a notification to the user being followed when someone follows them.
    """
    if action == "post_add":
        followed_user_profile = instance  # This is the profile being followed
        for follower_id in pk_set:
            try:
                follower_user = User.objects.get(pk=follower_id)
                Notification.objects.create(
                    user=followed_user_profile.user_name,  # The one being followed
                    sender=follower_user,
                    message=f"{follower_user.username} started following you!"
                )
            except User.DoesNotExist:
                continue

