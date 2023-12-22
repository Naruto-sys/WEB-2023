from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import activate

from App.models import Profile, Answer, Tag, Question


class LoginForm(forms.Form):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        super().clean()
        user = User.objects.filter(username=self.cleaned_data.get("username"))
        if not user.exists():
            raise ValidationError({"username": ["Такого пользователя не существует!"]})
        user = user[0]
        if not user.check_password(self.cleaned_data.get("password")):
            raise ValidationError({"password": ["Неверный пароль!"]})
        return self.cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=6, max_length=30, label="Введите имя пользователя")
    email = forms.EmailField(widget=forms.EmailInput, label="Введите почту")
    nickname = forms.CharField(min_length=6, max_length=30, label="Введите никнейм (будет виден на сайте)")
    password = forms.CharField(widget=forms.PasswordInput, label="Введите Пароль")
    repeat_password = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    def clean_password(self):
        activate("ru")
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data.get('password')

    def clean_username(self):
        activate("ru")
        username = self.cleaned_data.get("username")
        username = username.strip()
        if (len(username)) < 6:
            raise ValidationError("Имя пользователя не может быть короче 6 символов!")
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError("Это имя пользователя уже занято!")
        return self.cleaned_data.get('username')

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()
        if (len(nickname)) < 6:
            raise ValidationError("Никнейм не может быть короче 6 символов!")
        if Profile.objects.filter(nickname=nickname).exists():
            raise ValidationError("Этот никнейм уже занят!")
        return self.cleaned_data.get("nickname").strip()

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("Эта почта уже занята!")
        return self.cleaned_data.get('email')

    def clean(self):
        activate("ru")
        super().clean()
        if self.cleaned_data.get('password') is None or self.cleaned_data.get('repeat_password') is None:
            return self.cleaned_data
        if validate_password(self.cleaned_data.get('password')) is not None:
            return self.cleaned_data
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password'):
            raise ValidationError({"password": "Пароли различаются!",
                                   "repeat_password": "Пароли различаются!"})
        return self.cleaned_data

    def save(self):
        username = self.cleaned_data['username'].strip()
        email = self.cleaned_data['email'].strip()
        password = self.cleaned_data['password'].strip()
        nickname = self.cleaned_data['nickname'].strip()
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, nickname=nickname)
        user.save()


class AskForm(forms.Form):
    title = forms.CharField(min_length=8, max_length=250, label="Заголовок")
    text = forms.CharField(min_length=20, widget=forms.Textarea, label="Ваш вопрос")
    tags = forms.CharField(help_text="Введите теги вопроса через запятую", label="Теги")

    def clean_title(self):
        title = self.cleaned_data.get("title")
        title = title.strip()
        if (len(title)) < 8:
            raise ValidationError("Заголовок содержит меньше 8 символов!")
        return title

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if (len(text)) < 20:
            raise ValidationError("Вопрос содержит меньше 20 символов!")
        return text

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        tags = tags.split(',')
        tags = [tag.strip() for tag in tags]

        if len(tags) == 0:
            raise ValidationError("У вопроса должен быть хотя бы 1 тег")
        if len(tags) > 3:
            raise ValidationError("Введите не больше 3 тегов")
        for tag in tags:
            if len(tag) == 0:
                raise ValidationError("Тег не может быть пустой строкой")
            if tag.count(" ") > 0:
                raise ValidationError("Внутри тегов не может быть пробелов")
            if '/' in tag:
                raise ValidationError("Внутри тегов не может быть символов '/'")
        return self.cleaned_data.get("tags")

    def save(self, user=None):
        title = self.cleaned_data['title']
        text = self.cleaned_data['text']
        tags = self.cleaned_data['tags'].strip()
        tags_objects = []
        for tag in tags.split(','):
            cur_tag = tag.strip()
            objects = Tag.objects.all().filter(tag_title=cur_tag)
            if len(objects) > 0:
                tags_objects.append(objects[0])
            else:
                tags_objects.append(Tag.objects.create(tag_title=cur_tag))
        new_question = Question.objects.create(question_title=title, question_view=title,
                                               question_body=text, author=user)
        new_question.tags.set(tags_objects)
        new_question.save()
        return new_question


class ProfileForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    activate("ru")
    email = forms.EmailField(label="Почта")
    nickname = forms.CharField(min_length=6, max_length=30, label="Никнейм")
    avatar = forms.ImageField(required=False, widget=forms.FileInput(), label="Аватар")

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()
        if (len(nickname)) < 6:
            raise ValidationError("Никнейм не может быть короче 6 символов!")
        return nickname

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])
        return self.cleaned_data.get('email')

    def clean(self):
        activate("ru")
        super().clean()
        email = self.cleaned_data['email']
        nickname = self.cleaned_data['nickname']

        if User.objects.filter(email=email).exists():
            if User.objects.filter(email=email)[0] != self.user:
                raise ValidationError("Эта почта уже занята!")

        if Profile.objects.filter(nickname=nickname).exists():
            if Profile.objects.filter(nickname=nickname)[0].user != self.user:
                raise ValidationError("Этот никнейм уже занят!")

    def save(self):
        activate("ru")
        user_profile = self.user.profile
        self.user.email = self.cleaned_data.get('email')
        user_profile.nickname = self.cleaned_data.get('nickname')
        if self.cleaned_data.get('avatar'):
            user_profile.avatar = self.cleaned_data.get('avatar')
        self.user.save()
        user_profile.save()


class AnswerForm(forms.Form):
    text = forms.CharField(min_length=10, widget=forms.Textarea, label="Ваш ответ")

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if (len(text)) < 10:
            raise ValidationError("Ответ содержит меньше 10 символов!")
        return text

    def save(self, question, user):
        text = self.cleaned_data.get('text').strip()
        answer = Answer.objects.create(question=question, answer_body=text, author=user)
        question.answers_count = len(Answer.objects.filter(question=question))
        answer.save()
        question.save()
        return answer
