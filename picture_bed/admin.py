from django.contrib import admin

from picture_bed.models import Picture

"""
class PictureBedAdmin(admin.ModelAdmin):
    fields = ['picture', 'user']

    inlines = []
"""
admin.site.register(Picture)
