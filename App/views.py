from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from App.models import Question, Answer, Tag


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
    questions = list(Question.objects.get_newest_questions())
    page_obj = paginate(questions, request, 10)
    return render(request, "index.html",
                  {'questions': page_obj.object_list, 'page_obj': page_obj})


def question(request, question_id):
    current_question = list(Question.objects.get_question_by_id(question_id))[0]
    answers = list(Answer.objects.get_answers_by_question(current_question))
    page_obj = paginate(answers, request, 5)
    return render(request, "question.html",
                  {'question': current_question, 'answers': page_obj.object_list, 'page_obj': page_obj})


def hot(request):
    questions = list(Question.objects.get_hot_questions())
    page_obj = paginate(questions, request, 10)
    return render(request, "hot.html",
                  {'questions': page_obj.object_list, 'page_obj': page_obj})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def ask(request):
    return render(request, "ask.html")


def end_session(request):
    return render(request, "login.html")


def tag(request, tag_title):
    tag = list(Tag.objects.get_tag_by_title(tag_title))[0]
    tag_questions = Question.objects.get_questions_by_tag(tag)
    page_obj = paginate(tag_questions, request, 10)
    return render(request, "listtag.html",
                  {'questions': page_obj.object_list, 'tag': tag_title, 'page_obj': page_obj})


def profile(request, profile_id=0):
    return render(request, "profile.html")


def handler404(request, *args, **argv):
    print("HERE")
    return render(request, "404.html", status=404)
