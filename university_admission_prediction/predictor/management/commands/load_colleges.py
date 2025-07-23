from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load initial college data from fixtures'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading college data...')
        call_command('loaddata', 'colleges.json')
        self.stdout.write(self.style.SUCCESS('Successfully loaded college data'))
