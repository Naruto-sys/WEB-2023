from django.core.management import BaseCommand

from App.models import QuestionLike, AnswerLike
from django.core.management import BaseCommand

from App.models import QuestionLike, AnswerLike


class Command(BaseCommand):
    help = "Make likes tables unique"

    def handle(self, *args, **kwargs):
        for row in AnswerLike.objects.all().reverse():
            if AnswerLike.objects.filter(answer=row.answer_id, liked_by=row.liked_by_id).count() > 1:
                row.delete()
        for row in QuestionLike.objects.all().reverse():
            if QuestionLike.objects.filter(question=row.question_id, liked_by=row.liked_by_id).count() > 1:
                row.delete()
