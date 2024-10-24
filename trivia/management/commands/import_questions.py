import csv
from django.core.management.base import BaseCommand
from trivia.models import Question
import os


class Command(BaseCommand):
    help = 'Import questions from a CSV file'

    def handle(self, *args, **kwargs):
        try:
            # Usar una ruta absoluta si es necesario
            csv_file_path = os.path.join(os.path.dirname(__file__), '../../../questions.csv')


            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    Question.objects.create(
                        question_text=row['question_text'],
                        option_a=row['option_a'],
                        option_b=row['option_b'],
                        option_c=row['option_c'],
                        option_d=row['option_d'],
                        correct_answer=row['correct_answer'],
                        points=row['points']
                    )
            self.stdout.write(self.style.SUCCESS('Questions successfully imported!'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found in path: {csv_file_path}!'))
