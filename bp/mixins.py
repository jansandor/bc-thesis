from django.contrib.auth.mixins import UserPassesTestMixin


class ClientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_client


class PsychologistRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_psychologist


class ResearcherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_researcher


class StaffResearcherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff and self.request.user.is_researcher


class PsychologistOrResearcherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_psychologist or self.request.user.is_researcher
