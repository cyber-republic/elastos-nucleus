from django.contrib import admin

from .models import UploadFile , UserAPIKeys


class UploadFileAdmin(admin.ModelAdmin):
    model = UploadFile
    list_display = ('did', 'uploaded_file')


admin.site.register(UploadFile, UploadFileAdmin)

admin.site.register(UserAPIKeys)
