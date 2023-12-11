import string

from django.core.management import BaseCommand
from django.db import IntegrityError
from faker import Faker
import random

from App.models import User, Question, Profile, Tag, QuestionLike, AnswerLike, Answer

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = "Fills database with fake data"

    def add_arguments(self, parser):
        parser.add_argument("num_users", type=int)

    def create_users(self, num):
        users = []
        for _ in range(num):
            try:
                user = User.objects.create_user(
                    ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 16))),
                    first_name=fake.first_name(), last_name=fake.last_name(),
                    email=fake.email(), password=fake.password())
                users.append(user)
                user.save()
            except IntegrityError as e:
                print(e)
                print("Error in user saving occurred")
        return users

    def create_profiles(self, users):
        profiles = []
        for _ in range(len(users)):
            profiles.append(
                Profile(
                    user=users[_],
                    nickname=''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(8, 25))),
                )
            )
        Profile.objects.bulk_create(profiles)
        return profiles

    def create_tags(self, num):
        tags = [
            Tag(
                tag_title=''.join(random.choices(string.ascii_letters, k=random.randint(7, 10)))
            ) for _ in range(num)
        ]
        Tag.objects.bulk_create(tags)
        return tags

    def create_questions(self, users, tags, num):
        questions = []
        a = 0
        for _ in range(num * 10):
            question = Question.objects.create(
                question_title=fake.text(max_nb_chars=100),
                question_body=fake.text(max_nb_chars=1000),
                author=random.choice(users))
            questions.append(question)
            if len(question.question_body) > 100:
                question.question_view = question.question_body[0:100] + "..."
            else:
                question.question_view = question.question_body
            questions_tags = random.sample(tags, random.randint(1, min(3, num)))
            [question.tags.add(question_tag) for question_tag in questions_tags]
            question.save()
        return questions

    def create_answers(self, questions, users, num):
        answers = []
        for _ in range(num * 100):
            question = random.choice(questions)
            user = random.choice(users)
            question.answers_count += 1
            answer = Answer.objects.create(question=question,
                                           answer_body=fake.text(max_nb_chars=500), author=user)
            answer.save()
            question.save()
            answers.append(answer)
        return answers

    def create_likes(self, users, questions, answers, num):
        for _ in range(num * 200):
            if random.randint(0, 1):
                question = random.choice(questions)
                question.likes_count += 1
                user = random.choice(users)
                like = QuestionLike(
                    question=question,
                    liked_by=user,
                )
                question.save()
                like.save()
            else:
                answer = random.choice(answers)
                answer.likes_count += 1
                user = random.choice(users)
                like = AnswerLike(
                    answer=answer,
                    liked_by=user,
                )
                answer.save()
                like.save()

    def handle(self, *args, **kwargs):
        num = kwargs['num_users']
        users = self.create_users(num)
        self.create_profiles(users)
        tags = self.create_tags(num)
        questions = self.create_questions(users, tags, num)
        answers = self.create_answers(questions, users, num)
        self.create_likes(users, questions, answers, num)
        self.stdout.write(self.style.SUCCESS("SUCCESS"))
