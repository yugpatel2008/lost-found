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
        if created or not admin_user.check_password('admin123'):
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user ready (admin / admin123)'))

        if hasattr(admin_user, 'profile'):
            admin_user.profile.role = 'principal'
            admin_user.profile.department = 'All Departments'
            admin_user.profile.save()

        # 2. Student User: dhruvmakvana.26.cse
        student1, s1_created = User.objects.get_or_create(
            username='dhruvmakvana.26.cse',
            defaults={
                'email': 'dhruvmakvana.26.cse@indusuni.ac.in',
                'first_name': 'Dhruv',
                'last_name': 'Makvana',
            }
        )
        if s1_created or not student1.check_password('!ABW46k.Xn4hVyF'):
            student1.set_password('!ABW46k.Xn4hVyF')
            student1.save()
            self.stdout.write(self.style.SUCCESS('User dhruvmakvana.26.cse ready'))

        # 3. Student User: patelyug.26.cse
        student2, s2_created = User.objects.get_or_create(
            username='patelyug.26.cse',
            defaults={
                'email': 'patelyug.26.cse@indusuni.ac.in',
                'first_name': 'Yug',
                'last_name': 'Patel',
            }
        )
        if s2_created or not student2.check_password('!ABW46k.Xn4hVyF'):
            student2.set_password('!ABW46k.Xn4hVyF')
            student2.save()
            self.stdout.write(self.style.SUCCESS('User patelyug.26.cse ready'))

        self.stdout.write(self.style.SUCCESS('Default accounts initialization complete!'))
