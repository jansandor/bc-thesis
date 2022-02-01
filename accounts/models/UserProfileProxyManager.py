# todo tyka se "user+profile single modelu".. model/dto? co by mel data usera i profilu.. hodilo by se na vice mistech
# class PsychologistManager(models.Manager):
#    def get_queryset(self):
#        queryset = super().get_queryset().intersection(PsychologistProfile.objects.get_queryset())
#        return queryset.


# class PsychologistProxy(User):
#    objects = PsychologistManager
#    class Meta:
#        proxy = True
