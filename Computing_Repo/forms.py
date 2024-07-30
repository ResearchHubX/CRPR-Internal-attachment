from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        
        # Disable the postgraduate_type field
        self.fields['postgraduate_type'].widget.attrs['disabled'] = 'disabled'
        
        # Add onchange attribute to the occupation field
        self.fields['occupation'].widget.attrs['onchange'] = 'handleOccupationChange()'

        # Mark required fields
        for field_name in self.Meta.required_fields:
            self.fields[field_name].required = True
    
    class Meta:
        model = Projects
        fields = ['occupation', 'postgraduate_type', 'name', 'title', 'description', 'image', 'email', 'Github_link', 'project_url']
        widgets = {
            'occupation': forms.Select(attrs={'class': 'form-control', 'onchange': 'handleOccupationChange()'}),
            'postgraduate_type': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name (required)'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the project title (required)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter a short description (required)', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email (required)'}),
            'Github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter GitHub link (optional)'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter project URL (optional)'}),
        }
        required_fields = ['name', 'title', 'description', 'email']  # Define required fields here

       
        

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)

class CollaboratorForm(forms.ModelForm):
    class Meta:
        model = Collaborator
        fields = ['name', 'email', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter collaborator\'s name (optional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter collaborator\'s email (optional)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class ProjectFileForm(forms.ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': False}))

    class Meta:
        model = ProjectFile
        fields = ['file','description']


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ( 'email', 'first_name', 'last_name', 'password1', 'password2')
 
 # forms.py

from django import forms

class SubscriptionForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        initial=10.00,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

