from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ["email"]


admin.site.register(CustomUser, CustomUserAdmin)

# Register your models here.
