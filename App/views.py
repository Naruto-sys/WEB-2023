from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

ANSWERS = [
    {
        'title': 'title' + str(i),
        'id': i,
        'content': 'text' + str(i),
        'likes': 15 + i
    }
    for i in range(100)
]

QUESTIONS = [
    {
        'title': 'title' + str(i),
        'id': i,
        'content': 'text' + str(i),
        'tags': ['tag1', 'tag2', 'tag3'],
        'answers_count': 100,
        'likes': 15 + i,
        'answers': ANSWERS,
    }
    for i in range(100)
]

QUESTIONS_BY_TAG = {'tag1': QUESTIONS, 'tag2': QUESTIONS, 'tag3': QUESTIONS}


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
    page_obj = paginate(QUESTIONS, request, 10)
    return render(request, "index.html", {'questions': page_obj.object_list, 'page_obj': page_obj})


def question(request, question_id):
    current_question = QUESTIONS[question_id]
    page_obj = paginate(current_question['answers'], request, 5)
    return render(request, "question.html",
                  {'question': current_question, 'answers': page_obj.object_list, 'page_obj': page_obj})


def hot(request): # Разницы пока что никакой
    return render(request, "index.html", {'questions': paginate(QUESTIONS, request, 4)})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def ask(request):
    return render(request, "ask.html")


def end_session(request):
    return render(request, "login.html")


def tag(request, tag_name):
    tag_questions = QUESTIONS_BY_TAG[tag_name]
    page_obj = paginate(tag_questions, request, 10)
    return render(request, "listtag.html", {'questions': page_obj.object_list, 'tag': tag_name, 'page_obj': page_obj})


def profile(request, profile_id=0):
    return render(request, "profile.html")
