
from time import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Projects(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    OCCUPATION_CHOICES = (
        ('undergraduate', 'Undergraduate'),
        ('staff', 'Staff'),
        ('postgraduate', 'Postgraduate'),
    )

    POSTGRADUATE_CHOICES = (
        ('masters', 'Masters'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=70)
    title = models.CharField(max_length=100)
    description = models.TextField(default="")
    image = models.ImageField(upload_to='projects_images/',default="", blank=True, null=True)
    email = models.EmailField(default="", blank=True, null=True)
    Github_link = models.URLField(max_length=200, blank=True, null=True, default="")
    project_url = models.URLField(max_length=200, blank=True, null=True, default="")
    date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, default='undergraduate')
    postgraduate_type = models.CharField(max_length=20, choices=POSTGRADUATE_CHOICES, blank=True, null=True)
    is_secure = models.BooleanField(default=False)

    def __str__(self):
        return self.name if self.name else f"Project ID {self.pk}"



class Collaborator(models.Model):
    project = models.ForeignKey(Projects, related_name='collaborators', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to='collaborator_images/', blank=True, null=True)

    def __str__(self):
     return f"{self.name} - {self.project}" or 'Unnamed collaborator'


class ProjectFile(models.Model):
    project = models.ForeignKey(Projects, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"File for {self.project.name} - {self.description}"




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
    

class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    news_item = models.BooleanField(default=False)
    event_item = models.BooleanField(default=False)

    def __str__(self):
        return self.title

 # models.py
# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class PayPalPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_id} - {self.user.username}"

import datetime
from django.utils import timezone

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True,blank=True)

    def is_active(self):
        today = timezone.now().date()
        return self.start_date.date() <= today <= self.end_date.date()

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"


class FeaturedResearcher(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='researchers/')
    specialization = models.CharField(max_length=200)

    def __str__(self):
        return self.name