from django.core.cache import cache
from django.core.management import BaseCommand
from django.conf import settings as conf_settings
from App.models import Tag, get_popular_tags


class Command(BaseCommand):
    help = "Set cache of popular tags"

    def handle(self, *args, **kwargs):
        cache.set(conf_settings.TAGS_CACHE_KEY, get_popular_tags(), 900)  # Храню 15мин, обновляю каждые 10
