from django.contrib.auth.models import UserManager
from django.contrib.auth.models import User
# Assuming you have a custom user model like: class User(AbstractBaseUser, PermissionsMixin):
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.response import Response

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize application data'

    def handle(self, *args, **options):
        # Code to create superuser
        User.objects.create_superuser(
            username='admin1',
            email='metiadmin@.com',
            password='admin1234'
        )

        return Response({'success':'Superuser created successfully'})