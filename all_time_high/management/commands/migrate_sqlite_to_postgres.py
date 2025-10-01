from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections, transaction

class Command(BaseCommand):
    help = 'Migrate all data from sqlite to postgresql.'

    def handle(self, *args, **options):
        sqlite = connections['sqlite']
        postgres = connections['default']
        models = apps.get_models()
        self.stdout.write(self.style.WARNING('Starting migration from sqlite to postgresql...'))
        for model in models:
            table = model._meta.db_table
            self.stdout.write(f'Transferring {table}...')
            objects = model.objects.using('sqlite').all()
            with transaction.atomic(using='default'):
                for obj in objects:
                    obj.pk = None  # Avoid PK collision
                    obj.save(using='default')
        self.stdout.write(self.style.SUCCESS('Migration completed!'))
