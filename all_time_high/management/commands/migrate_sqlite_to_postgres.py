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


        # 1. Migrate django_content_type first
        ct_models = [m for m in models if m._meta.db_table == 'django_content_type']
        for model in ct_models:
            table = model._meta.db_table
            self.stdout.write(f'Transferring CONTENT TYPES: {table}...')
            objects = model.objects.using('sqlite').all()
            for obj in objects:
                obj.pk = None
                # Check for missing FK (e.g. content_type_id)
                skip = False
                for field in model._meta.fields:
                    if field.is_relation and getattr(obj, field.name, None):
                        rel_model = field.related_model
                        rel_pk = getattr(obj, field.name)
                        if rel_pk and not rel_model.objects.using('default').filter(pk=rel_pk.pk if hasattr(rel_pk, 'pk') else rel_pk).exists():
                            self.stdout.write(self.style.WARNING(f"Skipped {table} ID {obj.pk}: missing FK {field.name}={rel_pk}"))
                            skip = True
                            break
                if skip:
                    continue
                try:
                    with transaction.atomic(using='default'):
                        obj.save(using='default')
                except Exception as e:
                    if 'duplicate key value violates unique constraint' in str(e):
                        self.stdout.write(self.style.WARNING(f"Skipped duplicate in {table}: {e}"))
                    else:
                        raise

        # 2. Migrate users and related tables
        user_models = [
            m for m in models if m._meta.app_label == 'auth' or m._meta.db_table.startswith('auth_')
        ]
        for model in user_models:
            table = model._meta.db_table
            self.stdout.write(f'Transferring USERS: {table}...')
            objects = model.objects.using('sqlite').all()
            for obj in objects:
                obj.pk = None
                try:
                    with transaction.atomic(using='default'):
                        obj.save(using='default')
                except Exception as e:
                    if 'duplicate key value violates unique constraint' in str(e):
                        self.stdout.write(self.style.WARNING(f"Skipped duplicate in {table}: {e}"))
                    if 'violates foreign key constraint' in str(e):
                        self.stdout.write(self.style.WARNING(f"Skipped {table} ID {obj.pk}: missing FK, set to NULL."))
                    else:
                        raise

        # 2. Migrate all other models
        for model in models:
            if model in user_models:
                continue
            table = model._meta.db_table
            self.stdout.write(f'Transferring {table}...')
            objects = model.objects.using('sqlite').all()
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
                try:
                    with transaction.atomic(using='default'):
                        obj.save(using='default')
                except Exception as e:
                    if 'duplicate key value violates unique constraint' in str(e):
                        self.stdout.write(self.style.WARNING(f"Skipped duplicate in {table}: {e}"))
                    else:
                        raise
        self.stdout.write(self.style.SUCCESS('Migration completed!'))
        self.stdout.write(self.style.SUCCESS('Migration completed!'))
