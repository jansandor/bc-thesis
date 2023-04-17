# TODO mozna zmenit pak path at to dava nejakej smysl treba
def user_specific_upload_file_path(user_profile, filename):
    return f'accounts/user_{user_profile.user.id}/{filename}'


def user_specific_upload_dir(user):
    return f'accounts/user_{user.id}/'
