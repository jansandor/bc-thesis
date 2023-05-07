from django.core.exceptions import PermissionDenied


def user_is_client(user):
    if user.is_anonymous:
        return False
    if user.is_client:
        return True
    raise PermissionDenied


def user_is_psychologist(user):
    if user.is_anonymous:
        return False
    if user.is_psychologist:
        return True
    raise PermissionDenied


def user_is_researcher(user):
    if user.is_anonymous:
        return False
    if user.is_researcher:
        return True
    raise PermissionDenied


def user_is_staff_researcher(user):
    if user.is_anonymous:
        return False
    if user.is_staff and user.is_researcher:
        return True
    raise PermissionDenied


def user_is_psychologist_or_researcher(user):
    if user.is_anonymous:
        return False
    if user.is_psychologist or user.is_researcher:
        return True
    return PermissionDenied
