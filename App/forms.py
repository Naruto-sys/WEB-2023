from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import activate

from App.models import Profile, Answer, Tag, Question


class LoginForm(forms.Form):
    username = forms.CharField()
    username.label = "Имя пользователя"
    password = forms.CharField(widget=forms.PasswordInput)
    password.label = "Пароль"

    def clean(self, request=None):
        super().clean()
        if request is None:
            return
        user = authenticate(request, **self.cleaned_data)
        if user is not None:
            login(request, user)
            return
        if User.objects.filter(username=self.cleaned_data.get("username")).exists():
            self.add_error("password", "Неверный пароль!")
        else:
            self.add_error("username", "Такого пользователя не существует!")
        return 0


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=6, max_length=30)
    username.label = "Введите имя пользователя"
    email = forms.EmailField(widget=forms.EmailInput)
    email.label = "Введите почту"
    nickname = forms.CharField(min_length=6, max_length=30)
    nickname.label = "Введите никнейм (будет виден на сайте)"
    password = forms.CharField(widget=forms.PasswordInput)
    password.label = "Введите Пароль"
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    repeat_password.label = "Повторите пароль"

    def clean_password(self):
        activate("ru")
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data.get('password')

    def clean_username(self):
        activate("ru")
        username = self.cleaned_data.get("username")
        username = username.strip()
        if (len(username)) < 6:
            self.add_error("username", "Имя пользователя не может быть короче 6 символов!")
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError("Это имя пользователя уже занято!")
        return self.cleaned_data.get('username')

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()
        if (len(nickname)) < 6:
            self.add_error("nickname", "Никнейм не может быть короче 6 символов!")
        if Profile.objects.filter(nickname='nickname').exists():
            raise ValidationError("Этот никнейм уже занят!")
        return self.cleaned_data.get('nickname')

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            self.add_error("email", "Эта почта уже занята!")
        return self.cleaned_data.get('email')

    def clean(self):
        activate("ru")
        super().clean()
        if self.cleaned_data.get('password') is None or self.cleaned_data.get('repeat_password') is None:
            return self.cleaned_data
        if validate_password(self.cleaned_data.get('password')) is not None:
            return self.cleaned_data
        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password'):
            self.add_error("password", "Пароли различаются!")
            self.add_error("repeat_password", "Пароли различаются!")
        return self.cleaned_data

    def save(self, request=None):
        username = self.cleaned_data['username'].strip()
        email = self.cleaned_data['email'].strip()
        password = self.cleaned_data['password'].strip()
        nickname = self.cleaned_data['nickname'].strip()
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, nickname=nickname)
        authenticate(request, username=username, password=password)
        user.save()
        login(request, user)


class AskForm(forms.Form):
    title = forms.CharField(min_length=8, max_length=250)
    title.label = "Заголовок"
    text = forms.CharField(min_length=20, widget=forms.Textarea)
    text.label = "Ваш вопрос"
    tags = forms.CharField(help_text="Введите теги вопроса через запятую")
    tags.label = "Теги"

    def clean_title(self):
        title = self.cleaned_data.get("title")
        title = title.strip()
        if (len(title)) < 8:
            self.add_error("title", "Заголовок содержит меньше 8 символов!")
        return self.cleaned_data.get("title")

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if (len(text)) < 20:
            self.add_error("text", "Вопрос содержит меньше 20 символов!")
        return self.cleaned_data.get("text")

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        tags = tags.split(',')
        tags = [tag.strip() for tag in tags]

        if len(tags) == 0:
            self.add_error("tags", "У вопроса должен быть хотя бы 1 тег")
        if len(tags) > 3:
            self.add_error("tags", "Введите не больше 3 тегов")
        for tag in tags:
            if len(tag) == 0:
                self.add_error("tags", "Тег не может быть пустой строкой")
            if tag.count(" ") > 0:
                self.add_error("tags", "Внутри тегов не может быть пробелов")
            if '/' in tag:
                self.add_error("tags", "Внутри тегов не может быть символов '/'")
        return self.cleaned_data.get("tags")

    def clean(self):
        super().clean()

    def save(self, user=None):
        title = self.cleaned_data['title'].strip()
        text = self.cleaned_data['text'].strip()
        tags = self.cleaned_data['tags'].strip()
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
                                               question_body=text, author=user)
        new_question.tags.set(tags_objects)
        new_question.save()
        return new_question


class ProfileForm(forms.Form):
    activate("ru")
    email = forms.EmailField()
    email.label = "Почта"
    nickname = forms.CharField(min_length=6, max_length=30)
    nickname.label = "Никнейм"
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    avatar.label = "Аватар"

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()
        if (len(nickname)) < 6:
            self.add_error("nickname", "Никнейм не может быть короче 6 символов!")
        return self.cleaned_data.get("nickname")

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])
        return self.cleaned_data.get('email')

    def clean(self, user=None):
        activate("ru")
        super().clean()
        if user is None:
            return
        email = self.cleaned_data['email'].strip()
        nickname = self.cleaned_data['nickname'].strip()

        if User.objects.filter(email=email).exists():
            if User.objects.filter(email=email)[0] != user:
                self.add_error("email", "Эта почта уже занята!")
                return 0

        if Profile.objects.filter(nickname=nickname).exists():
            if Profile.objects.filter(nickname=nickname)[0].user != user:
                self.add_error("nickname", "Этот никнейм уже занят!")
                return 0

    def save(self, user=None):
        activate("ru")
        user_profile = user.profile
        user.email = self.cleaned_data.get('email')
        user_profile.nickname = self.cleaned_data.get('nickname')
        if self.cleaned_data.get('avatar'):
            user_profile.avatar = self.cleaned_data.get('avatar')
        user.save()
        user_profile.save()


class AnswerForm(forms.Form):
    text = forms.CharField(min_length=10, widget=forms.Textarea)
    text.label = "Ваш ответ"

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if (len(text)) < 10:
            self.add_error("text", "Ответ содержит меньше 10 символов!")
        return self.cleaned_data.get("text")

    def clean(self):
        super().clean()

    def save(self, question, user):
        text = self.cleaned_data.get('text').strip()
        answer = Answer.objects.create(question=question, answer_body=text, author=user)
        question.answers_count = len(Answer.objects.filter(question=question))
        answer.save()
        question.save()
        return answer
