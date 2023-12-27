from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


def get_best_users_nicks():
    last_week = now() - timedelta(days=7)
    last_answers = list(Answer.objects.filter(created_at__gte=last_week))
    last_questions = list(Question.objects.filter(created_at__gte=last_week))
    nominee = last_answers + last_questions
    nominee.sort(key=lambda nom: -nom.likes_count)  # Sort по кол-ву лайков среди вопросов и ответов
    best_users = []
    index = 0
    # Если у юзера несколько вопросов-ответов из топа, он должен войти лишь раз
    while len(best_users) < 10 and index < len(nominee):
        if nominee[index].author not in best_users:
            best_users.append(nominee[index].author)
        index += 1
    best_users_nicknames = [nom.profile.nickname for nom in best_users]
    return best_users_nicknames


def get_popular_tags():
    all_tags = Tag.objects.all()

    def key_func(tag):
        three_months = now() - timedelta(days=90)
        return -len(tag.questions.filter(created_at__gte=three_months))

    return list(sorted(all_tags, key=key_func))[:10]


def get_questions_by_tag(tag):
    return tag.questions.order_by('-created_at')


def get_question_likes_count(question):
    question.likes_count = len(QuestionLike.objects.filter(question=question))
    question.save()
    return question.likes_count


def get_answer_likes_count(answer):
    answer.likes_count = len(AnswerLike.objects.filter(answer=answer))
    answer.save()
    return answer.likes_count


class QuestionManager(models.Manager):
    def get_hot_questions(self):
        return self.order_by('-likes_count', '-answers_count', '-created_at')

    def get_newest_questions(self):
        return self.order_by('-created_at')

    def get_question_by_id(self, question_id):
        return self.filter(question_id__exact=question_id)


class QuestionLikeManager(models.Manager):
    def toggle_like(self, user, question):
        if self.filter(liked_by=user, question=question).exists():
            self.filter(liked_by=user, question=question).delete()
            return "disliked"
        self.create(liked_by=user, question=question)
        return "liked"


class AnswerLikeManager(models.Manager):
    def toggle_like(self, user, answer):
        if self.filter(liked_by=user, answer=answer).exists():
            self.filter(liked_by=user, answer=answer).delete()
            return "disliked"
        self.create(liked_by=user, answer=answer)
        return "liked"


class AnswerManager(models.Manager):
    def get_answers_by_question(self, question):
        all_answers = self.all()
        try:
            return all_answers.filter(question__exact=question).order_by('-created_at')
        except self.model.DoesNotExist as e:
            return Answer.objects.none()


class TagManager(models.Manager):
    def get_tag_by_title(self, title):
        return self.filter(tag_title__exact=title)


class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_title = models.CharField(null=False, blank=False, max_length=250)
    question_view = models.CharField(null=False, blank=False, max_length=120)
    question_body = models.CharField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    likes_count = models.IntegerField(default=0)
    answers_count = models.IntegerField(default=0)
    tags = models.ManyToManyField("Tag", related_name="questions")

    objects = QuestionManager()

    def __str__(self):
        return f"Вопрос: '{self.question_title}'"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_id = models.AutoField(primary_key=True)
    answer_body = models.CharField(null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    objects = AnswerManager()

    def __str__(self):
        return f"Вопрос: '{self.question.question_title}'\tОтвет номер: {self.answer_id}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, null=False, blank=False)
    avatar = models.ImageField(null=True, blank=True, default="avatar.jpg", upload_to="avatar/%Y/%m/%d")
    nickname = models.CharField(max_length=256, unique=True, null=False, blank=False)

    def __str__(self):
        return f"Профиль {str(self.user)}"


class Tag(models.Model):
    tag_title = models.CharField(primary_key=True, max_length=50)
    objects = TagManager()

    def __str__(self):
        return self.tag_title


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = QuestionLikeManager()

    class Meta:
        unique_together = ('question', 'liked_by',)

    def __str__(self):
        return f"{str(self.question)};\t оценка от {str(self.liked_by)}"


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = AnswerLikeManager()

    class Meta:
        unique_together = ('answer', 'liked_by',)

    def __str__(self):
        return f"{str(self.answer)};\t оценка от {str(self.liked_by)}"
