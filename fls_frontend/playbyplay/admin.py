from django.contrib import admin

import models

# Register your models here.
class PlayByPlayAdmin(admin.ModelAdmin):
    pass


class GameAdmin(admin.ModelAdmin):
    pass


class PlayerGameStatsAdmin(admin.ModelAdmin):
    pass


class ShootoutAdmin(admin.ModelAdmin):
    pass


class PlayerOnIceAdmin(admin.ModelAdmin):
    pass


class GameScratchAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.PlayByPlay, PlayByPlayAdmin)
admin.site.register(models.Game, GameAdmin)
admin.site.register(models.PlayerGameStats, PlayerGameStatsAdmin)
admin.site.register(models.Shootout, ShootoutAdmin)
admin.site.register(models.PlayerOnIce, PlayerOnIceAdmin)
admin.site.register(models.GameScratch, GameScratchAdmin)

