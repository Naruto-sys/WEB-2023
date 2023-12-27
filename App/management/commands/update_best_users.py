from django.conf import settings as conf_settings
from django.core.cache import cache
from django.core.management import BaseCommand

from App.models import get_best_users_nicks


class Command(BaseCommand):
    help = "Set cache of best users"

    def handle(self, *args, **kwargs):
        cache.set(conf_settings.USERS_CACHE_KEY, get_best_users_nicks(), 900) # Храню 15мин, обновляю каждые 10
