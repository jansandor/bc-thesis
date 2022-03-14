def user_specific_upload_dir(user_profile, filename):
    return 'accounts/user_{0}/{1}'.format(user_profile.user.id, filename)
# TODO mozna zmenit pak path at to dava nejakej smysl treba
