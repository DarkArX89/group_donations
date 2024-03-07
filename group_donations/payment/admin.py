from django.contrib import admin

from .models import Payment, Collect, Reason

admin.site.register(Payment)
admin.site.register(Collect)
admin.site.register(Reason)
