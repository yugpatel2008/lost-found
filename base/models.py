from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ─── Shared choices ───────────────────────────────────────────────────────────
DEPARTMENT_CHOICES = [
    ('IT Department',          'IT Department'),
    ('Civil Department',       'Civil Department'),
    ('Mechanical Department',  'Mechanical Department'),
    ('Electrical Department',  'Electrical Department'),
    ('Computer Department',    'Computer Department'),
]

LOCATION_CHOICES = [
    ('Amenity Hall',           'Amenity Hall'),
    ('Annexe Building',        'Annexe Building'),
    ('Library',                'Library'),
    ('Canteen',                'Canteen'),
    ('Main Building',          'Main Building'),
    ('GymKhana',               'GymKhana'),
    ('Parking Lot',            'Parking Lot'),
    ('Technology Bhavan',      'Technology Bhavan'),
    ('Workshop-2',             'Workshop-2'),
    ('Workshop-1',             'Workshop-1'),
    ('Indus Uni. Commons',         'Indus Uni. Commons'),
    ('IT Department',          'IT Department'),
    ('Civil Department',       'Civil Department'),
    ('Mechanical Department',  'Mechanical Department'),
    ('Electrical Department',  'Electrical Department'),
    ('Computer Department',    'Computer Department'),
]

# Locations that belong to specific departments (for HOD filtering)
DEPT_LOCATIONS = {dept: dept for dept, _ in DEPARTMENT_CHOICES}


# ─── UserProfile ──────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('principal', 'Principal'),
        ('hod',       'Head of Department (HOD)'),
        ('teacher',   'Teacher'),
        ('student',   'Student'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        blank=True, null=True,
        help_text="Required for HOD role. Leave blank for Principal / Student."
    )

    def __str__(self):
        dept = f" — {self.department}" if self.department else ""
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()}{dept})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Only create a profile for brand-new users. Do NOT re-save on every User.save()
    to avoid session invalidation after password changes."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


# ─── Item ─────────────────────────────────────────────────────────────────────
class Item(models.Model):
    item_type      = models.CharField(max_length=10, null=True, blank=True)
    name           = models.CharField(max_length=100)
    description    = models.TextField()
    date_found     = models.DateField(null=True, blank=True)
    location_found = models.CharField(max_length=100, choices=LOCATION_CHOICES)
    tags           = models.CharField(
        max_length=200,
        help_text="Comma-separated tags",
        null=True, blank=True
    )
    file           = models.FileField(upload_to='uploads/', null=True, blank=True)
    contact_info   = models.CharField(max_length=100, null=True, blank=True)

    # Meetup details (for "found" items)
    meetup_place   = models.CharField(max_length=200, null=True, blank=True)
    meetup_date    = models.DateField(null=True, blank=True)
    meetup_time    = models.TimeField(null=True, blank=True)

    # Who posted it (links to the logged-in user, optional for now)
    posted_by      = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='items'
    )
    created_at     = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"[{self.item_type}] {self.name}"

    class Meta:
        ordering = ['-created_at']
