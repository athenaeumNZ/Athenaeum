from management.models import Member

def make_email_list(library):
    users = Member.objects.filter(
        library=library,
        active=True).values_list('user__email', flat=True)
    # Join the email addresses into a comma-separated string
    return ", ".join(users)