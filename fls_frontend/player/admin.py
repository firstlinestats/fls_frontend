from django.contrib import admin

import models


# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Player, PlayerAdmin)
