from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
#paypal intergrations
from django.conf import settings
from .models import PayPalPayment, Subscription
from .forms import SubscriptionForm
import paypalrestsdk
from django.urls import reverse
from datetime import timedelta

# views.py
import logging
logger = logging.getLogger(__name__)
from django.urls import reverse
from django.forms import modelformset_factory
# filter
from .filters import OrderFilter
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db import IntegrityError

# Create your views here.
def base(request):
    return render(request, "base.html")

def home(request):
    recent_projects = Projects.objects.filter(
        status__in=['active', 'completed'], 
        occupation='undergraduate'
    ).order_by('-date')[:3]
    
    news_items = NewsAndEvents.objects.filter(news_item=True)
    event_items = NewsAndEvents.objects.filter(event_item=True)
    researchers = FeaturedResearcher.objects.all()
    
    return render(request, "home.html", {
        'recent_projects': recent_projects,
        'current_page': 'home',
        'news_items': news_items,
        'event_items': event_items,
        'researchers': researchers
    })

def sign_in(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            if User.objects.filter(username=email).exists():
                form.add_error('email', 'A user with this email already exists.')
            else:
                try:
                    user = form.save(commit=False)
                    user.username = email
                    user.save()
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect('profile_page')
                except IntegrityError:
                    form.add_error(None, 'An error occurred while creating the user.')
    else:
        form = SignUpForm()
    
    return render(request, 'user/sign_in.html', {'form': form, 'current_page': 'sign_in'})

def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("profile_page")
    else:
        form = AuthenticationForm()
    return render(request, "user/login_page.html", {
        'form': form,
        'current_page': 'login_page'
    })

def logout_page(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")

def FAQs(request):
    return render(request, "FAQs.html")

def project_page(request):
    # Filter out cancelled and secure projects
    if request.user.is_superuser:
        projects = Projects.objects.exclude(status='cancelled')
    else:
        projects = Projects.objects.exclude(status='cancelled').exclude(is_secure=True)
    
    projects = projects.order_by('-date')

    # Filtering codes
    myFilter = OrderFilter(request.GET, queryset=projects)
    projects = myFilter.qs

    # Pagination logic
    paginator = Paginator(projects, 5)  # Show 5 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "projects_page.html", {
        'projects': page_obj,
        'myFilter': myFilter,
        'current_page': 'project_page'
    })

@login_required(login_url='login_page')
def create_project(request):
    if not request.user.email.endswith('jkuat.ac.ke') and not request.user.is_superuser:
        return redirect('invalid_email')

    if request.method == "POST":
        form = CreateProjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                new_project = form.save(commit=False)
                new_project.creator = request.user
                new_project.status = 'active'
                new_project.save()
                return redirect('add_collaborators', project_id=new_project.id)
            except Exception as e:
                logger.error(f"Error creating project: {e}")
                messages.error(request, 'An error occurred while creating the project.')
    else:
        form = CreateProjectForm()
    
    return render(request, "user/create_project_step1.html", {'form': form, 'current_page': 'create_project'})

def invalid_email(request):
    return render(request, 'profile/error_page.html')


@login_required(login_url='login_page')
def add_collaborators(request, project_id):
    project = Projects.objects.get(id=project_id)
    CollaboratorFormSet = modelformset_factory(Collaborator, form=CollaboratorForm, extra=1, can_delete=True)

    if request.method == "POST":
        formset = CollaboratorFormSet(request.POST, request.FILES, queryset=Collaborator.objects.filter(project=project))
        if formset.is_valid():
            collaborators = formset.save(commit=False)
            for collaborator in collaborators:
                collaborator.project = project
                collaborator.save()
            return redirect('upload_files', project_id=project_id)
    else:
        formset = CollaboratorFormSet(queryset=Collaborator.objects.filter(project=project))

    return render(request, "user/create_project_step2.html", {'formset': formset, 'current_page': 'add_collaborators'})

@login_required(login_url='login_page')
def upload_files(request, project_id):
    project = Projects.objects.get(id=project_id)

    if request.method == "POST":
        files = request.FILES.getlist('file[]')
        descriptions = request.POST.getlist('description[]')
        for file, description in zip(files, descriptions):
            ProjectFile.objects.create(project=project, file=file, description=description)
        return redirect('myProject_page')

    return render(request, "user/create_project_step3.html", {'current_page': 'upload_files'})

@login_required(login_url='login_page')
def update_files(request, project_id):
    project = Projects.objects.get(id=project_id)
    files = ProjectFile.objects.filter(project=project)

    if request.method == "POST":
        descriptions = request.POST.getlist('description[]')
        for file_obj, description in zip(files, descriptions):
            file_obj.description = description
            file_obj.save()

        new_files = request.FILES.getlist('new_files[]')
        new_descriptions = request.POST.getlist('new_descriptions[]')
        for new_file, new_description in zip(new_files, new_descriptions):
            ProjectFile.objects.create(project=project, file=new_file, description=new_description)

        # Delete files if specified
        files_to_delete = request.POST.getlist('files_to_delete[]')
        for file_id in files_to_delete:
            ProjectFile.objects.filter(id=file_id).delete()

        return redirect('myProject_page')

    return render(request, "user/update_files.html", {'project': project, 'files': files, 'current_page': 'update_files'})

@login_required(login_url='login_page')
def profile_page(request):
    user_form = BasicUserForm(instance=request.user)
    profile = getattr(request.user, 'profile', None)
    profile_form = ProfileForm(instance=profile) if profile else ProfileForm()
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        if request.POST.get('action') == 'update_profile':
            user_form = BasicUserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('profile_page')
        elif request.POST.get('action') == 'update_password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated.')
                return redirect('profile_page')
            else:
                messages.error(request, 'Failed to update password. Please try again.')
        elif request.POST.get('action') == 'update_profile_image':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                if not profile:
                    profile = profile_form.save(commit=False)
                    profile.user = request.user
                    profile.save()
                else:
                    profile_form.save()
                messages.success(request, 'Your profile image has been updated.')
                return redirect('profile_page')
            else:
                messages.error(request, 'Failed to update profile image. Please try again.')

    return render(request, 'profile/profile_page.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'messages': messages.get_messages(request),
        'password_form': password_form,
        'current_page': 'profile_page'
    })

@login_required(login_url='login_page')
def myProject_page(request, status=None):
    user = request.user
    
    if not user.email.endswith('jkuat.ac.ke') and not user.is_superuser:
        return redirect('invalid_email')

    if status is None:
        # Default to active projects if no status is specified
        status = 'active'

    if status == 'active':
        projects = Projects.objects.filter(creator=user, status='active').order_by('-date')
    elif status == 'completed':
        projects = Projects.objects.filter(creator=user, status='completed').order_by('-date')
    elif status == 'cancelled':
        projects = Projects.objects.filter(creator=user, status='cancelled').order_by('-date')
    else:
        projects = Projects.objects.filter(creator=user).order_by('-date')  # This case should never be hit due to the default

    # Set up pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(projects, 3)  # Show 3 projects per page

    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    return render(request, "profile/myProjects.html", {
        'projects': projects,
        'status': status,
        'current_page': 'myProject_page'
    })

@login_required(login_url='login_page')
def project_detail(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
    return render(request, 'profile/project_detail.html', {'project': project, 'current_page': 'project_detail'})

@login_required(login_url='login_page')
def cancel_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
    if request.method == 'POST':
        project.status = 'cancelled'
        project.save()
        return redirect('myProject_page_status', 'cancelled')
    return redirect('project_detail', project_id=project_id)


def details_page(request, project_id):
    project = get_object_or_404(Projects, pk=project_id)

    # Check if the project is secure
    if project.is_secure and request.user != project.creator and not request.user.is_superuser:
        messages.warning(request, "You do not have permission to view this secure project.")
        return redirect('project_page')

    # Check if the project is for postgraduate or staff
    if project.occupation in ['postgraduate', 'staff']:
        if request.user == project.creator:
            # Allow creator to view details without subscription
            collaborators = Collaborator.objects.filter(project=project)
            project_files = ProjectFile.objects.filter(project=project)
            return render(request, 'details_page.html', {
                'project': project,
                'collaborators': collaborators,
                'project_files': project_files,
                'current_page': 'details_page'
            })

        if request.user.is_authenticated:
            subscription = Subscription.objects.filter(user=request.user).first()
            if not subscription or not subscription.is_active():
                # Notify the user that their subscription has expired
                messages.warning(request, "Your subscription has expired. Please renew your subscription to access this page.")
                return render(request, 'user/subscription_expired.html')
        else:
            # Redirect to login page if the user is not authenticated
            return redirect('login_page')

    collaborators = Collaborator.objects.filter(project=project)
    project_files = ProjectFile.objects.filter(project=project)
    return render(request, 'details_page.html', {
        'project': project,
        'collaborators': collaborators,
        'project_files': project_files,
        'current_page': 'details_page'
    })


@login_required(login_url='login_page')
def update_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
    if request.method == 'POST':
        form = CreateProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('update_files', project_id=project.id)
    else:
        form = CreateProjectForm(instance=project)
    return render(request, 'user/update_project.html', {'form': form, 'current_page': 'update_project'})

@login_required(login_url='login_page')
def complete_project(request, project_id):
    project = get_object_or_404(Projects, id=project_id)
    if request.method == 'POST':
        project.status = 'completed'
        project.save()
        return redirect('myProject_page_status', 'completed')
    return redirect('project_detail', project_id=project_id)

# Paypal views.py
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

@login_required
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": "USD"},
                    "description": "Subscription payment"}],
                "redirect_urls": {
                    "return_url": request.build_absolute_uri(reverse('paypal_return')),
                    "cancel_url": request.build_absolute_uri(reverse('paypal_cancel')),
                },
            })

            if payment.create():
                PayPalPayment.objects.create(
                    user=request.user,
                    payment_id=payment.id,
                    amount=amount,
                    status='Created',
                )
                for link in payment.links:
                    if link.rel == 'approval_url':
                        return redirect(link.href)
            else:
                messages.error(request, 'Error creating PayPal payment.')
    else:
        form = SubscriptionForm()

    return render(request, 'payments/subscribe.html', {'form': form})


@login_required
def paypal_return(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    # Assuming paypalrestsdk.Payment.find(payment_id) correctly retrieves payment information
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
    except paypalrestsdk.exceptions.ResourceNotFound:
        messages.error(request, 'Payment not found.')
        return redirect('subscribe')

    if payment.execute({"payer_id": payer_id}):
        # Mark PayPalPayment as approved
        paypal_payment = PayPalPayment.objects.get(payment_id=payment_id)
        paypal_payment.status = 'Approved'
        paypal_payment.save()

        # Create or update subscription
        subscription, created = Subscription.objects.get_or_create(user=request.user)
        if created or subscription.end_date < timezone.now():
            subscription.start_date = timezone.now()
            subscription.end_date = subscription.start_date + timedelta(days=30)  # Adjust as per your subscription logic
            # Alternatively, if you have a specific subscription period based on payment details, adjust accordingly

        subscription.save()

        messages.success(request, 'Payment successful. Subscription activated.')
        return render(request, 'payments/payment_success.html')
    else:
        messages.error(request, 'Payment failed.')
        return redirect('subscribe')

@login_required
def paypal_cancel(request):
    messages.error(request, 'Payment cancelled.')
    return render(request, 'payments/payment_cancel.html')

@login_required
def subscription_status(request):
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-start_date')
    current_subscription = None
    expired_subscription = None

    if subscriptions:
        current_subscription = subscriptions.first()
        if current_subscription.end_date >= timezone.now():
            active = True
        else:
            active = False
            expired_subscription = current_subscription.end_date
    else:
        active = False

    context = {
        'subscriptions': subscriptions,
        'active': active,
        'current_subscription': current_subscription,
        'expired_subscription': expired_subscription,
    }

    return render(request, 'payments/subscription_status.html', context)


def billing(request):
    return render(request, "terms/billing.html")

def privacy(request):
    return render(request, "terms/privacy.html")

def terms(request):
    return render(request, "terms/terms.html")