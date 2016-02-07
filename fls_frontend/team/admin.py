from django.contrib import admin

import models


# Register your models here.
class VenueAdmin(admin.ModelAdmin):
    pass


class TeamAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Venue, VenueAdmin)
admin.site.register(models.Team, TeamAdmin)
