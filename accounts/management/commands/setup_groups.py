from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from capsules.models import Capsule


class Command(BaseCommand):
    help = 'Setup user groups and permissions'

    def handle(self, *args, **kwargs):
        timekeeper_group, created = Group.objects.get_or_create(name='Timekeeper')

        guardian_group, created = Group.objects.get_or_create(name='Guardian')

        capsule_ct = ContentType.objects.get_for_model(Capsule)

        can_open_any, _ = Permission.objects.get_or_create(
            codename='can_open_any_capsule',
            name='Can open any capsule regardless of date',
            content_type=capsule_ct,
        )
        timekeeper_group.permissions.add(can_open_any)

        can_verify, _ = Permission.objects.get_or_create(
            codename='can_verify_capsules',
            name='Can verify capsules for opening',
            content_type=capsule_ct,
        )
        guardian_group.permissions.add(can_verify)

        self.stdout.write(self.style.SUCCESS('Successfully created groups and permissions'))
