from django.apps import AppConfig
from django.db.models.signals import post_migrate

def update_default_site(sender, **kwargs):
    try:
        from django.contrib.sites.models import Site
        site = Site.objects.get(id=1)
        if site.domain == 'example.com':
            site.domain = '127.0.0.1:8000'
            site.name = 'Organa'
            site.save()
            print("[Organa Config] Default site domain updated to 127.0.0.1:8000")
    except Exception:
        pass

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    label = 'authentication'

    def ready(self):
        post_migrate.connect(update_default_site, sender=self)
