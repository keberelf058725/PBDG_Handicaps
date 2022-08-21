from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import auth
import json
from .forms import NewUserForm, cap_score_Form
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


# Create your views here.

def logout_user(request):
    auth.logout(request)
    return redirect('login')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            form.save()

            subject = "PBDG League Tool"
            email_template_name = "password/new_user_setup.txt"
            c = {
                "email": user.email,
                'domain': '127.0.0.1:8000',
                'site_name': 'PBDG',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            email = render_to_string(email_template_name, c)

            send_mail(subject, email, 'no_reply_PBDG@gmail.com', [user.email], fail_silently=True)

            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="register_user.html", context={"register_form": form})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'PBDG',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'no_reply_PBDG@gmail.com', [user.email], fail_silently=True)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


@login_required
def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})


def sting_to_list(score):
    score_list = score.split()
    return score_list


def list_to_string(score_list):
    score = ' '.join(score_list)
    return score


@login_required
def okee_upload_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = cap_score_Form(request.POST, request.FILES)
        if form.is_valid():
            try:
                # reads csv and instantiates dataframe object
                sheet1 = request.FILES['Cap_File']
                cap = pandas.DataFrame(pandas.read_csv(sheet1))

                # function outline
                """for each player check if player is in database if so run string to list queue 
                in new round and oldest is queued out calculate new handicap and
                replace old handicap in model/db run list to string func and save string to db """



            except Exception:
                messages.error(request, 'Unknown Columns Detected: Operation Cancelled')
            else:
                messages.success(request,
                                 'Success File has Been Uploaded')

            return render(request, "okee_upload_success.html", {})
    else:
        form = cap_score_Form()

    return render(request, "okee_upload.html", {'form': form})
