from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configurer le fichier de paramètres par défaut de Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'money_transfer.settings')

app = Celery('money_transfer')

# Charger les paramètres de configuration à partir des paramètres de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-détection des tâches dans tous les modules d'applications Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
