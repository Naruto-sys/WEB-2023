from django.db import models
from django.contrib.auth.models import User


class QuestionManager(models.Manager):
    def get_hot_questions(self):
        return self.order_by('-likes_count', '-answers_count', '-created_at')

    def get_newest_questions(self):
        return self.order_by('-created_at')

    def get_question_by_id(self, question_id):
        return self.filter(question_id__exact=question_id)

    def get_questions_by_tag(self, tag):
        return tag.questions.order_by('-created_at')


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
    created_at = models.DateTimeField(auto_now=True)
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
    created_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    objects = AnswerManager()

    def __str__(self):
        return f"Вопрос: '{self.question.question_title}'\tОтвет номер: {self.answer_id}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, null=False, blank=False)
    avatar_path = models.URLField(null=True, blank=True, max_length=500)
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

    def __str__(self):
        return f"{str(self.question)};\t оценка от {str(self.liked_by)}"


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{str(self.answer)};\t оценка от {str(self.liked_by)}"
