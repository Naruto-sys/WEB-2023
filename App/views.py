import time
import django
import jwt
from cent import Client
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_protect
from App.forms import LoginForm, RegisterForm, AskForm, ProfileForm, AnswerForm
from App.models import Question, Answer, Tag, QuestionLike, AnswerLike, get_questions_by_tag, get_question_likes_count, \
    get_answer_likes_count

activate('RU')

client = Client(conf_settings.CENTRIFUGO_API_URL, api_key=conf_settings.CENTRIFUGO_API_KEY)


def get_hot_questions():
    return list(Question.objects.get_hot_questions())


def get_newest_questions():
    return list(Question.objects.get_newest_questions())


def get_popular_tags():
    return cache.get(conf_settings.TAGS_CACHE_KEY)


def get_best_users_nicks():
    return cache.get(conf_settings.USERS_CACHE_KEY)


def get_centrifugo_data(user_id, channel):
    token = jwt.encode({"sub": str(user_id), "exp": int(time.time()) + 10 * 60},
                       conf_settings.CENTRIFUGO_TOKEN_HMAC_SECRET_KEY,
                       algorithm="HS256")
    return {"centrifugo": {"token": token,
                           "ws_url": conf_settings.CENTRIFUGO_WS_URL,
                           "channel": channel}}


def get_base(request):
    if request.user.is_authenticated:
        return 'layouts/base_with_user.html'
    return 'layouts/base_no_user.html'


def get_right_column():
    return {"popular_tags": get_popular_tags(), "best_users": get_best_users_nicks()}


def get_liked_list(request, answers=False):
    try:
        liked = []
        for like in QuestionLike.objects.filter(liked_by=request.user):
            liked.append(like.question)
        if not answers:
            return list(liked)
        for like in AnswerLike.objects.filter(liked_by=request.user):
            liked.append(like.answer)
        return list(liked)
    except TypeError:
        return None


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
    questions = get_newest_questions()  # так правильно
    # questions = NEWEST_QUESTIONS  # так быстрее
    page_obj = paginate(questions, request, 10)
    context = {'questions': page_obj.object_list, 'page_obj': page_obj, 'base': get_base(request),
               'liked_list': get_liked_list(request)}
    return render(request, "index.html", context | get_right_column())


def get_question_context(request, question_id):
    current_question = list(Question.objects.get_question_by_id(question_id))[0]
    answer_form = AnswerForm()
    answers = list(Answer.objects.get_answers_by_question(current_question))
    correct_answers = list(Answer.objects.filter(question=current_question, is_correct=True))
    page_obj = paginate(answers, request, 5)
    context = {'question': current_question, 'answers': page_obj.object_list, 'form': answer_form,
               'page_obj': page_obj, 'base': get_base(request),
               'liked_list': get_liked_list(request, answers=True), 'correct_answers': correct_answers,
               **get_centrifugo_data(request.user.id, f"question.{question_id}")}
    return context


@csrf_protect
def question(request, question_id):
    context = get_question_context(request, question_id)
    current_question = context.get("question")
    page_obj = context.get("page_obj")
    if request.method == "POST":
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            comment = model_to_dict(answer_form.save(user=request.user, question=current_question))
            comment["author_img"] = request.user.profile.avatar.url
            client.publish(f'question.{question_id}', comment)
            return redirect(f"{request.path}?page=1#last-answer")
        else:
            return redirect(f"{request.path}?page={page_obj.number}#answer-form")
    return render(request, "question.html", context | get_right_column())


def hot(request):
    questions = get_hot_questions()  # так правильно
    # questions = HOT_QUESTIONS  # а так быстрее
    page_obj = paginate(questions, request, 10)
    context = {'questions': page_obj.object_list, 'page_obj': page_obj, 'base': get_base(request),
               'liked_list': get_liked_list(request)}
    return render(request, "hot.html", context | get_right_column())


@csrf_protect
def login(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            django.contrib.auth.login(request, authenticate(request, **login_form.cleaned_data))
            return redirect(request.GET.get("continue", "/"))
    return render(request, "login.html", context={"form": login_form} | get_right_column())


@csrf_protect
def signup(request):
    reg_form = RegisterForm()
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        reg_form = RegisterForm(request.POST)
        if reg_form.is_valid():
            user = reg_form.save()
            django.contrib.auth.login(request, user)
            return redirect(request.GET.get("continue", "/"))
    return render(request, "signup.html", context={"form": reg_form} | get_right_column())


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    ask_form = AskForm()
    if request.method == "POST":
        ask_form = AskForm(request.POST)
        if ask_form.is_valid():
            new_question = ask_form.save(user=request.user)
            return redirect(f"question/{new_question.question_id}")
    return render(request, "ask.html", context={'form': ask_form} | get_right_column())


def end_session(request):
    logout(request)
    if request.GET.get("continue") is None:
        return redirect("index")
    return redirect(request.GET.get("continue"))


def tag(request, tag_title):
    tag_element = list(Tag.objects.get_tag_by_title(tag_title))[0]
    tag_questions = get_questions_by_tag(tag_element)
    page_obj = paginate(tag_questions, request, 10)
    context = {'questions': page_obj.object_list, 'tag': tag_title, 'page_obj': page_obj,
               'base': get_base(request), 'liked_list': get_liked_list(request)}
    return render(request, "listtag.html", context | get_right_column())


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def profile(request):
    user = request.user
    user_profile = user.profile
    profile_form = ProfileForm(user)

    if request.method == "GET":
        params_dict = model_to_dict(user) | model_to_dict(user_profile)
        profile_form = ProfileForm(user, initial=params_dict)

    if request.method == "POST":
        profile_form = ProfileForm(user, request.POST, request.FILES)
        if profile_form.is_valid():
            profile_form.save()
            context = {'form': profile_form} | get_right_column()
            return render(request, "profile.html", context)
    context = {'form': profile_form} | get_right_column()
    return render(request, "profile.html", context)


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def question_like(request):
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        question_object = get_object_or_404(Question, question_id=question_id)
        if not question_object:
            return JsonResponse({'message': 'Question not found'})
        if QuestionLike.objects.toggle_like(user=request.user, question=question_object) == "disliked":
            action_type = "disliked"
        else:
            action_type = "liked"
        count = get_question_likes_count(question=question_object)
        return JsonResponse({
            'type': action_type,
            'count': count,
            'message': 'OK'
        })
    return JsonResponse({'method': 'GET', 'message': 'OK'})


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def answer_like(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer_object = get_object_or_404(Answer, answer_id=answer_id)
        if not answer_object.question:
            return JsonResponse({'message': 'Answer not found'})
        if AnswerLike.objects.toggle_like(user=request.user, answer=answer_object) == "disliked":
            action_type = "disliked"
        else:
            action_type = "liked"
        count = get_answer_likes_count(answer=answer_object)
        return JsonResponse({
            'count': count,
            'type': action_type,
            'message': 'OK'
        })
    return JsonResponse({'method': 'GET', 'message': 'OK'})


@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def correct_answer(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer_object = get_object_or_404(Answer, answer_id=answer_id)
        if not answer_object.question:
            return JsonResponse({'message': 'Answer not found'})
        answer_object.is_correct = True
        answer_object.save()
    return JsonResponse({'method': 'GET', 'message': 'OK'})
