from django.contrib import admin

from .models import *

class ImageInlineAdmin(admin.TabularInline):
    model = Image
    fields = ('images', )
    max_num = 3



@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [ImageInlineAdmin, ]


admin.site.register(Category)
