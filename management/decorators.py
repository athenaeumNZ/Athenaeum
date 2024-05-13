def is_librarian(user):
    return user.groups.filter(name='librarian').exists()