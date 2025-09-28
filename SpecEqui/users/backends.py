from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Аутентификация: сначала пробуем по email, если не нашли — по username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        user = None
        # попробуем e-mail
        if '@' in username:
            user = User.objects.filter(email__iexact=username, is_active=True).first()
        # если не нашли по e-mail, попробуем username
        if user is None:
            user = User.objects.filter(username__iexact=username, is_active=True).first()

        if user and user.check_password(password):
            return user
        return None
