from django.conf import settings
from .models import Testimonial, Business, Blog, SocialPlatform, Service, PaymentLink

class DualWriteRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'ntls' and any(model._meta.model_name == m._meta.model_name for m in [Testimonial, Business, Blog, SocialPlatform, Service, PaymentLink]):
            return 'server'
        if model._meta.app_label == 'sessions':
            return 'default'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'ntls' and any(model._meta.model_name == m._meta.model_name for m in [Testimonial, Business, Blog, SocialPlatform, Service, PaymentLink]):
            return 'server'
        if model._meta.app_label == 'sessions':
            return 'default'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_list = ('server', 'default')
        return (obj1._state.db in db_list and obj2._state.db in db_list)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'ntls':
            return db in ['default', 'server']
        if app_label == 'sessions':
            return db == 'default'
        return db == 'default'