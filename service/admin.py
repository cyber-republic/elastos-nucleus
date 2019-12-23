from django.contrib import admin

from .models import UploadFile , userAPIKeys


class UploadFileAdmin(admin.ModelAdmin):
    model = UploadFile
    list_display = ('did', 'uploaded_file')


admin.site.register(UploadFile, UploadFileAdmin)

admin.site.register(userAPIKeys)
