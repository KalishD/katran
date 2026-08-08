# This file imports and registers admin from apps.store
# Django looks for admin.py in the app directory, so we need this file
# if the app is registered as 'store' in INSTALLED_APPS
from apps.store.admin import *
from apps.store.models import Patent, Variable

# Re-register models with correct admin classes
admin.site.unregister(Patent)
admin.site.unregister(Variable)

from apps.store.admin import PatentAdmin, VariableAdmin
admin.site.register(Patent, PatentAdmin)
admin.site.register(Variable, VariableAdmin)
