from django.contrib.auth.models import User

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create user"

    def add_arguments(self, parser):
        parser.add_argument("nick", type=str)
        parser.add_argument("pass", type=str)
        parser.add_argument("id", type=int)

    def handle(self, *args, **kwargs):
        name = kwargs["nick"]
        password = kwargs["pass"]
        id = kwargs["id"]
        user = User.objects.create_user(username=name, password=password, id=id, is_superuser=True, is_staff=True)
