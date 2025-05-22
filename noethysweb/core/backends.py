from django.contrib.auth.backends import ModelBackend, UserModel
from django.db.models import Q
from core.models import Individu


class EmailModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            for individu in Individu.objects.exclude(
                statut=Individu.STATUT_JEUNE
            ).filter(mail__isnull=False):
                if individu.mail.lower() == username.lower():
                    break
            else:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                UserModel().set_password(password)
                return
            user = individu.rattachement_set.first().famille.utilisateur

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
