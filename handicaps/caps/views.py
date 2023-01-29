import pandas as pd
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
from .models import okee_Player, delray_Player, commons_Player, pga_Player, dreher_Player
import datetime as dt



# Create your views here.

def logout_user(request):
    auth.logout(request)
    return redirect('home')


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



def home_view(request, *args, **kwargs):
    return render(request, "index.html", {})


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
            csv_file = request.FILES['Cap_File']
            cap = pd.read_csv(csv_file)
            cap = cap[['name', 'total_score']]
            for index, row in cap.iterrows():
                name = row['name']
                score = row['total_score']
                if okee_Player.objects.filter(players_name=name).exists():
                    player = okee_Player.objects.get(players_name=name)
                    scores_list = player.last_five_scores.split(',')
                    if len(scores_list) < 5:
                        scores_list.append(score)
                    else:
                        scores_list.pop(0)
                        scores_list.append(score)
                    player.last_five_scores = ','.join(str(v) for v in scores_list)
                    player.save()
                else:
                    okee_Player.objects.create(players_name=name, last_five_scores=str(score))
            return render(request, 'okee_upload_success.html')
    else:
        form = cap_score_Form()

    return render(request, "okee_upload.html", {'form': form})

def okee_get_handicap(request):
    if request.method == 'GET':
        players = okee_Player.objects.all()
        data = {'players_name': [], 'score_1': [], 'score_2': [], 'score_3': [], 'score_4': [], 'score_5': []}
        for player in players:
            scores = player.last_five_scores.split(',')
            data['players_name'].append(player.players_name)
            for i in range(5):
                if i < len(scores):
                    data[f'score_{i+1}'].append(int(scores[i]))
                else:
                    data[f'score_{i+1}'].append(None)
        df = pd.DataFrame(data)
        df["Average"] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].mean(axis=1, skipna=True)
        df["Handicap"] = (df["Average"]-54)*.8
        df["Handicap"] = df["Handicap"].apply(lambda x: round(x))
        df["Handicap"] = df["Handicap"] * -1
        df = df[["players_name", "Handicap", 'score_1', 'score_2', 'score_3', 'score_4', 'score_5']]
        df = df.sort_values('players_name')
        df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].fillna(0).astype('int64')
        df = df.astype('str')
        df = df.replace(['0'], '')
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'okee_handicap.html', context)

@login_required
def delray_upload_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = cap_score_Form(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['Cap_File']
            cap = pd.read_csv(csv_file)
            cap = cap[['name', 'total_score']]
            for index, row in cap.iterrows():
                name = row['name']
                score = row['total_score']
                if delray_Player.objects.filter(players_name=name).exists():
                    player = delray_Player.objects.get(players_name=name)
                    scores_list = player.last_five_scores.split(',')
                    if len(scores_list) < 5:
                        scores_list.append(score)
                    else:
                        scores_list.pop(0)
                        scores_list.append(score)
                    player.last_five_scores = ','.join(str(v) for v in scores_list)
                    player.save()
                else:
                    delray_Player.objects.create(players_name=name, last_five_scores=str(score))
            return render(request, 'delray_upload_success.html')
    else:
        form = cap_score_Form()

    return render(request, "delray_upload.html", {'form': form})

def delray_get_handicap(request):
    if request.method == 'GET':
        players = delray_Player.objects.all()
        data = {'players_name': [], 'score_1': [], 'score_2': [], 'score_3': [], 'score_4': [], 'score_5': []}
        for player in players:
            scores = player.last_five_scores.split(',')
            data['players_name'].append(player.players_name)
            for i in range(5):
                if i < len(scores):
                    data[f'score_{i+1}'].append(int(scores[i]))
                else:
                    data[f'score_{i+1}'].append(None)
        df = pd.DataFrame(data)
        df["Average"] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].mean(axis=1, skipna=True)
        df["Handicap"] = (df["Average"]-54)*.8
        df["Handicap"] = df["Handicap"].apply(lambda x: round(x))
        df["Handicap"] = df["Handicap"] * -1
        df = df[["players_name", "Handicap", 'score_1', 'score_2', 'score_3', 'score_4', 'score_5']]
        df = df.sort_values('players_name')
        df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].fillna(0).astype('int64')
        df = df.astype('str')
        df = df.replace(['0'], '')
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'delray_handicap.html', context)

@login_required
def pga_upload_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = cap_score_Form(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['Cap_File']
            cap = pd.read_csv(csv_file)
            cap = cap[['name', 'total_score']]
            for index, row in cap.iterrows():
                name = row['name']
                score = row['total_score']
                if pga_Player.objects.filter(players_name=name).exists():
                    player = pga_Player.objects.get(players_name=name)
                    scores_list = player.last_five_scores.split(',')
                    if len(scores_list) < 5:
                        scores_list.append(score)
                    else:
                        scores_list.pop(0)
                        scores_list.append(score)
                    player.last_five_scores = ','.join(str(v) for v in scores_list)
                    player.save()
                else:
                    pga_Player.objects.create(players_name=name, last_five_scores=str(score))
            return render(request, 'pga_upload_success.html')
    else:
        form = cap_score_Form()

    return render(request, "pga_upload.html", {'form': form})

def pga_get_handicap(request):
    if request.method == 'GET':
        players = pga_Player.objects.all()
        data = {'players_name': [], 'score_1': [], 'score_2': [], 'score_3': [], 'score_4': [], 'score_5': []}
        for player in players:
            scores = player.last_five_scores.split(',')
            data['players_name'].append(player.players_name)
            for i in range(5):
                if i < len(scores):
                    data[f'score_{i+1}'].append(int(scores[i]))
                else:
                    data[f'score_{i+1}'].append(None)
        df = pd.DataFrame(data)
        df["Average"] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].mean(axis=1, skipna=True)
        df["Handicap"] = (df["Average"]-54)*.8
        df["Handicap"] = df["Handicap"].apply(lambda x: round(x))
        df["Handicap"] = df["Handicap"] * -1
        df = df[["players_name", "Handicap", 'score_1', 'score_2', 'score_3', 'score_4', 'score_5']]
        df = df.sort_values('players_name')
        df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].fillna(0).astype('int64')
        df = df.astype('str')
        df = df.replace(['0'], '')
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'pga_handicap.html', context)

@login_required
def commons_upload_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = cap_score_Form(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['Cap_File']
            cap = pd.read_csv(csv_file)
            cap = cap[['name', 'total_score']]
            for index, row in cap.iterrows():
                name = row['name']
                score = row['total_score']
                if commons_Player.objects.filter(players_name=name).exists():
                    player = commons_Player.objects.get(players_name=name)
                    scores_list = player.last_five_scores.split(',')
                    if len(scores_list) < 5:
                        scores_list.append(score)
                    else:
                        scores_list.pop(0)
                        scores_list.append(score)
                    player.last_five_scores = ','.join(str(v) for v in scores_list)
                    player.save()
                else:
                    commons_Player.objects.create(players_name=name, last_five_scores=str(score))
            return render(request, 'commons_upload_success.html')
    else:
        form = cap_score_Form()

    return render(request, "commons_upload.html", {'form': form})

def commons_get_handicap(request):
    if request.method == 'GET':
        players = commons_Player.objects.all()
        data = {'players_name': [], 'score_1': [], 'score_2': [], 'score_3': [], 'score_4': [], 'score_5': []}
        for player in players:
            scores = player.last_five_scores.split(',')
            data['players_name'].append(player.players_name)
            for i in range(5):
                if i < len(scores):
                    data[f'score_{i+1}'].append(int(scores[i]))
                else:
                    data[f'score_{i+1}'].append(None)
        df = pd.DataFrame(data)
        df["Average"] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].mean(axis=1, skipna=True)
        df["Handicap"] = (df["Average"]-54)*.8
        df["Handicap"] = df["Handicap"].apply(lambda x: round(x))
        df["Handicap"] = df["Handicap"] * -1
        df = df[["players_name", "Handicap", 'score_1', 'score_2', 'score_3', 'score_4', 'score_5']]
        df = df.sort_values('players_name')
        df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].fillna(0).astype('int64')
        df = df.astype('str')
        df = df.replace(['0'], '')
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'commons_handicap.html', context)

@login_required
def dreher_upload_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = cap_score_Form(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['Cap_File']
            cap = pd.read_csv(csv_file)
            cap = cap[['name', 'total_score']]
            for index, row in cap.iterrows():
                name = row['name']
                score = row['total_score']
                if dreher_Player.objects.filter(players_name=name).exists():
                    player = dreher_Player.objects.get(players_name=name)
                    scores_list = player.last_five_scores.split(',')
                    if len(scores_list) < 5:
                        scores_list.append(score)
                    else:
                        scores_list.pop(0)
                        scores_list.append(score)
                    player.last_five_scores = ','.join(str(v) for v in scores_list)
                    player.save()
                else:
                    dreher_Player.objects.create(players_name=name, last_five_scores=str(score))
            return render(request, 'dreher_upload_success.html')
    else:
        form = cap_score_Form()

    return render(request, "dreher_upload.html", {'form': form})

def dreher_get_handicap(request):
    if request.method == 'GET':
        players = dreher_Player.objects.all()
        data = {'players_name': [], 'score_1': [], 'score_2': [], 'score_3': [], 'score_4': [], 'score_5': []}
        for player in players:
            scores = player.last_five_scores.split(',')
            data['players_name'].append(player.players_name)
            for i in range(5):
                if i < len(scores):
                    data[f'score_{i+1}'].append(int(scores[i]))
                else:
                    data[f'score_{i+1}'].append(None)
        df = pd.DataFrame(data)
        df["Average"] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].mean(axis=1, skipna=True)
        df["Handicap"] = (df["Average"]-54)*.8
        df["Handicap"] = df["Handicap"].apply(lambda x: round(x))
        df["Handicap"] = df["Handicap"] * -1
        df = df[["players_name", "Handicap", 'score_1', 'score_2', 'score_3', 'score_4', 'score_5']]
        df = df.sort_values('players_name')
        df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']] = df[['score_1', 'score_2', 'score_3', 'score_4', 'score_5']].fillna(0).astype('int64')
        df = df.astype('str')
        df = df.replace(['0'], '')
        json_records = df.reset_index().to_json(orient='records')
        data = json.loads(json_records)
        context = {'d': data}
        return render(request, 'dreher_handicap.html', context)