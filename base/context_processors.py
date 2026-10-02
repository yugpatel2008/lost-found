"""
Global context processors – injected into every template automatically.
"""


def is_admin(request):
    """
    Adds `is_admin` (bool) to every template context.
    True when the logged-in user is a principal, HOD, teacher, or Django staff.
    """
    user = request.user
    if not user.is_authenticated:
        return {'is_admin': False}

    if user.is_staff:
        return {'is_admin': True}

    try:
        role = user.profile.role
        return {'is_admin': role in ('principal', 'hod', 'teacher')}
    except Exception:
        return {'is_admin': False}
