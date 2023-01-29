from django.contrib import admin
from .models import okee_Player, delray_Player, commons_Player, pga_Player, dreher_Player
# Register your models here.
admin.site.register(okee_Player)
admin.site.register(delray_Player)
admin.site.register(commons_Player)
admin.site.register(pga_Player)
admin.site.register(dreher_Player)