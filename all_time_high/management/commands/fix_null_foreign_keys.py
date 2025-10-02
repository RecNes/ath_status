from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix NULL foreign keys by interactively assigning valid PKs.'

    def handle(self, *args, **options):
        models = apps.get_models()
        for model in models:
            for field in model._meta.fields:
                if field.is_relation:
                    null_objs = model.objects.using('default').filter(**{f'{field.name}__isnull': True})
                    if null_objs.exists():
                        self.stdout.write(self.style.WARNING(f"{model.__name__}: {field.name} has NULLs."))
                        for obj in null_objs:
                            self.stdout.write(f"ID: {obj.pk} - Set {field.name} (valid PK required): ")
                            pk_input = input(f"Enter PK for {model.__name__}.{field.name} (ID {obj.pk}): ")
                            if pk_input:
                                rel_model = field.related_model
                                try:
                                    rel_instance = rel_model.objects.using('default').get(pk=pk_input)
                                    setattr(obj, field.name, rel_instance)
                                    with transaction.atomic(using='default'):
                                        obj.save(using='default')
                                    self.stdout.write(self.style.SUCCESS(f"Updated {model.__name__} ID {obj.pk} {field.name} -> {pk_input}"))
                                except rel_model.DoesNotExist:
                                    self.stdout.write(self.style.ERROR(f"PK {pk_input} not found for {rel_model.__name__}"))
        self.stdout.write(self.style.SUCCESS('All NULL foreign keys processed.'))
