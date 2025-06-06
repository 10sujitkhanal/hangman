from django.db import models

class Word(models.Model):
    text = models.CharField(max_length=50, help_text="Enter the text")
    suggestions = models.CharField(max_length=50, null=True, blank=True)
    is_solved = models.BooleanField(default=False, help_text="Check if this word has been solved by a user.")

    def __str__(self):
        return self.text.upper()

    class Meta:
        verbose_name_plural = "Words"
        ordering = ['text']