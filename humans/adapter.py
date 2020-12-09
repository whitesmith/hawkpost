from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        try:
            email = EmailAddress.objects.get(email=sociallogin.user.email)
        except EmailAddress.DoesNotExist:
            return

        sociallogin.connect(request, email.user)
