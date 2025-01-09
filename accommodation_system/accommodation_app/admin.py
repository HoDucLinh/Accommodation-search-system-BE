from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Accommodation,Post,User

# Register your models here.

class AccommodationAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'created_date', 'description', 'address', 'price', 'is_rented', 'owner_id']
    search_fields = ['description', 'address', 'price', 'owner__username' ]
    list_filter = ['district', 'city', 'number_of_people']



admin.site.register(Accommodation , AccommodationAdmin)
admin.site.register(Post)
admin.site.register(User, UserAdmin)
