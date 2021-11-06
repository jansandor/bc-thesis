def user_specific_upload_dir(instance, filename):
    return 'accounts/user_{0}/{1}'.format(instance.user.id, filename)
# TODO mozna zmenit pak path at to dava nejakej smysl treba
