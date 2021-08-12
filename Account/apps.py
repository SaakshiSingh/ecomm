from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'Account'
    default_auto_field = 'django.db.models.BigAutoField'


    def ready(self):
        import Account.signals
