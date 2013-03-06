from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        call_command('syncdb')
        call_command('loaddata', 'sections')
        call_command('loaddata', 'categories')
        call_command('loaddata', 'countries')
        call_command('loaddata', 'languages')
