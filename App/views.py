import django
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_protect

from App.forms import LoginForm, RegisterForm, AskForm, ProfileForm, AnswerForm
from App.models import Question, Answer, Tag, Profile

activate('RU')

HOT_QUESTIONS = list(Question.objects.get_hot_questions())
NEWEST_QUESTIONS = list(Question.objects.get_newest_questions())
# POPULAR_TAGS = Tag.objects.get_popular_tags()
POPULAR_TAGS = list(Tag.objects.all()[:10])


def get_base(request):
    if request.user.is_authenticated:
        return 'layouts/base_with_user.html'
    return 'layouts/base_no_user.html'


def paginate(objects, request, per_page=10):
    paginator = Paginator(objects, per_page)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def index(request):
    questions = NEWEST_QUESTIONS
    page_obj = paginate(questions, request, 10)
    context = {'questions': page_obj.object_list, 'page_obj': page_obj,
               'base': get_base(request), 'request': request, 'popular_tags': POPULAR_TAGS}
    return render(request, "index.html", context)


@csrf_protect
def question(request, question_id):
    current_question = list(Question.objects.get_question_by_id(question_id))[0]
    answer_form = AnswerForm()
    answers = list(Answer.objects.get_answers_by_question(current_question))
    page_obj = paginate(answers, request, 5)
    context = {'question': current_question, 'answers': page_obj.object_list, 'form': answer_form,
               'page_obj': page_obj, 'base': get_base(request), 'popular_tags': POPULAR_TAGS}

    if request.method == "POST":
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            text = answer_form.cleaned_data['text'].strip()
            Answer.objects.create(question=current_question, answer_body=text,
                                  author=request.user)
            return redirect(f"{request.path}?page=1#last-answer")
        else:
            return redirect(f"{request.path}?page={page_obj.number}#answer-form")
    return render(request, "question.html", context)


def hot(request):
    questions = HOT_QUESTIONS
    page_obj = paginate(questions, request, 10)
    context = {'questions': page_obj.object_list, 'page_obj': page_obj,
               'base': get_base(request), 'popular_tags': POPULAR_TAGS}
    return render(request, "hot.html", context)


@csrf_protect
def login(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = authenticate(request, **login_form.cleaned_data)
            if user is not None:
                django.contrib.auth.login(request, user)
                return redirect(request.GET.get("continue", "/"))
            else:
                if User.objects.filter(username=login_form.cleaned_data.get("username")).exists():
                    login_form.add_error("password", "Неверный пароль!")
                else:
                    login_form.add_error("username", "Такого пользователя не существует!")
    return render(request, "login.html", context={"form": login_form, 'popular_tags': POPULAR_TAGS})


@csrf_protect
def signup(request):
    reg_form = RegisterForm()
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        reg_form = RegisterForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username'].strip()
            email = reg_form.cleaned_data['email'].strip()
            password = reg_form.cleaned_data['password'].strip()
            nickname = reg_form.cleaned_data['nickname'].strip()
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user, nickname=nickname)
            authenticate(request, username=username, password=password)
            django.contrib.auth.login(request, user)
            return redirect(request.GET.get("continue", "/"))
    return render(request, "signup.html", context={"form": reg_form, 'popular_tags': POPULAR_TAGS})


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    ask_form = AskForm()
    if request.method == "POST":
        ask_form = AskForm(request.POST)
        if ask_form.is_valid():
            title = ask_form.cleaned_data['title'].strip()
            text = ask_form.cleaned_data['text'].strip()
            tags = ask_form.cleaned_data['tags'].strip()

            tags_objects = []
            for tag in tags.split(','):
                cur_tag = tag.lstrip()
                cur_tag = cur_tag.rstrip()
                objects = Tag.objects.all().filter(tag_title=cur_tag)
                if len(objects) > 0:
                    tags_objects.append(objects[0])
                else:
                    tags_objects.append(Tag.objects.create(tag_title=cur_tag))
            new_question = Question.objects.create(question_title=title, question_view=title,
                                                   question_body=text, author=request.user)
            new_question.tags.set(tags_objects)
            return redirect(f"question/{new_question.question_id}")
    return render(request, "ask.html", context={'form': ask_form, 'popular_tags': POPULAR_TAGS})


def end_session(request):
    logout(request)
    if request.GET.get("continue") is None:
        return redirect("index")
    return redirect(request.GET.get("continue"))


def tag(request, tag_title):
    tag = list(Tag.objects.get_tag_by_title(tag_title))[0]
    tag_questions = Question.objects.get_questions_by_tag(tag)
    page_obj = paginate(tag_questions, request, 10)
    context = {'questions': page_obj.object_list, 'tag': tag_title, 'page_obj': page_obj,
               'base': get_base(request), 'popular_tags': POPULAR_TAGS}
    return render(request, "listtag.html", context)


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def profile(request):
    profile_form = ProfileForm()
    user_profile = Profile.objects.all().filter(user_id=request.user.id)
    user = request.user
    if request.method == "GET":
        profile_form = ProfileForm()
        if len(user_profile) > 0:
            user_profile = user_profile[0]
            nick = user_profile.nickname if user_profile.nickname is not None else ""
            email = user.email if user.email is not None else ""
            profile_form.fields['nickname'].initial = nick
            profile_form.fields['email'].initial = email
    if request.method == "POST":
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            email = profile_form.cleaned_data['email'].strip()
            nickname = profile_form.cleaned_data['nickname'].strip()

            if User.objects.filter(email=email).exists():
                if User.objects.filter(email=email)[0] != request.user:
                    profile_form.add_error("email", "Эта почта уже занята!")

            if Profile.objects.filter(nickname=nickname).exists():
                if Profile.objects.filter(nickname=nickname)[0].user != request.user:
                    profile_form.add_error("nickname", "Этот никнейм уже занят!")

            if len(profile_form.errors) > 0:
                return render(request, "profile.html", context={'form': profile_form,
                                                                'popular_tags': POPULAR_TAGS})

            # avatar = profile_form.cleaned_data['avatar_path'].strip()
            # (avatar)

            user_profile = Profile.objects.all().filter(user_id=request.user.id)[0]
            user.email = email
            user_profile.nickname = nickname
            user.save()
            user_profile.save()
            # user_profile.avatar = avatar
            return render(request, "profile.html", context={'form': profile_form,
                                                            'popular_tags': POPULAR_TAGS})

    return render(request, "profile.html", context={'form': profile_form,
                                                    'popular_tags': POPULAR_TAGS})
