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
                    for field in model._meta.fields:
                        if field.is_relation and getattr(obj, field.name, None):
                            rel_model = field.related_model
                            rel_pk = getattr(obj, field.name)
                            if rel_pk and not rel_model.objects.using('default').filter(pk=rel_pk.pk if hasattr(rel_pk, 'pk') else rel_pk).exists():
                                self.stdout.write(self.style.WARNING(
                                    f"Missing FK for {table}.{field.name}={rel_pk}, set to NULL."
                                ))
                                setattr(obj, field.name, None)
                    obj.save(using='default')
        self.stdout.write(self.style.SUCCESS('Migration completed!'))
        self.stdout.write(self.style.SUCCESS('Migration completed!'))
