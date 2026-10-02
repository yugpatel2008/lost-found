from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.models import UserProfile


class Command(BaseCommand):
    help = 'Initialize default admin and test user accounts if they do not exist.'

    def handle(self, *args, **options):
        # 1. Admin / Principal User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@indusuni.ac.in',
                'first_name': 'Admin',
                'last_name': 'Principal',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.role = 'principal'
        profile.department = 'All Departments'
        profile.save()
        self.stdout.write(self.style.SUCCESS('Admin user reset: admin / admin123'))

        # 2. Student User: dhruvmakvana.26.cse
        student1, _ = User.objects.get_or_create(
            username='dhruvmakvana.26.cse',
            defaults={
                'email': 'dhruvmakvana.26.cse@indusuni.ac.in',
                'first_name': 'Dhruv',
                'last_name': 'Makvana',
            }
        )
        student1.set_password('!ABW46k.Xn4hVyF')
        student1.save()
        profile1, _ = UserProfile.objects.get_or_create(user=student1)
        profile1.role = 'student'
        profile1.save()
        self.stdout.write(self.style.SUCCESS('User dhruvmakvana.26.cse reset'))

        # 3. Student User: patelyug.26.cse
        student2, _ = User.objects.get_or_create(
            username='patelyug.26.cse',
            defaults={
                'email': 'patelyug.26.cse@indusuni.ac.in',
                'first_name': 'Yug',
                'last_name': 'Patel',
            }
        )
        student2.set_password('!ABW46k.Xn4hVyF')
        student2.save()
        profile2, _ = UserProfile.objects.get_or_create(user=student2)
        profile2.role = 'student'
        profile2.save()
        self.stdout.write(self.style.SUCCESS('User patelyug.26.cse reset'))

        self.stdout.write(self.style.SUCCESS('Default accounts initialization complete!'))
