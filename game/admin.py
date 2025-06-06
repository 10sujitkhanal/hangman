from django.contrib import admin
from .models import Word

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_solved')
    list_filter = ('is_solved',)
    search_fields = ('text',)
    actions = ['mark_as_unsolved']

    def mark_as_unsolved(self, request, queryset):
        updated = queryset.update(is_solved=False)
        self.message_user(request, f"{updated} word(s) marked as unsolved.")
    mark_as_unsolved.short_description = "Mark selected words as unsolved"