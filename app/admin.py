from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Thread, Comment, User

class ThreadAdminForm(forms.ModelForm):
    # Plain text password field for input
    plain_password = forms.CharField(
        label="Thread Password",
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text="Enter a new password to change it, or leave blank to keep existing."
    )

    class Meta:
        model = Thread
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        plain_password = cleaned_data.get('plain_password')
        if plain_password:
            cleaned_data['password'] = make_password(plain_password)
        else:
            # Retain existing hashed password if no new password is provided
            thread = self.instance
            if thread.pk and thread.password:
                cleaned_data['password'] = thread.password
        return cleaned_data

class UserAdminForm(forms.ModelForm):
    # Plain text password field for input
    plain_password = forms.CharField(
        label="User Password",
        widget=forms.PasswordInput(render_value=True),
        required=False,
        help_text="Enter a new password to change it, or leave blank to keep existing."
    )

    class Meta:
        model = User
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        plain_password = cleaned_data.get('plain_password')
        if plain_password:
            cleaned_data['password'] = make_password(plain_password)
        else:
            # Retain existing hashed password if no new password is provided
            user = self.instance
            if user.pk and user.password:
                cleaned_data['password'] = user.password
        return cleaned_data

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    form = ThreadAdminForm
    list_display = ('thread_name', 'slug', 'created_at', 'has_password')
    list_filter = ('created_at',)
    search_fields = ('thread_name', 'slug')
    readonly_fields = ('password', 'slug', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('thread_name', 'plain_password', 'slug')
        }),
        ('Advanced', {
            'fields': ('password', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    def has_password(self, obj):
        return bool(obj.password)
    has_password.short_description = 'Password Set'
    has_password.boolean = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # When editing, clear plain_password field
            form.base_fields['plain_password'].initial = ''
        return form

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'content_preview', 'created_at')
    list_filter = ('created_at', 'thread', 'user')
    search_fields = ('content', 'user__username', 'thread__thread_name')
    readonly_fields = ('created_at',)
    actions = ['delete_selected_comments']

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'

    def delete_selected_comments(self, request, queryset):
        return queryset.delete()
    delete_selected_comments.short_description = "Delete selected comments"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('username', 'has_password')
    list_filter = ('username',)
    search_fields = ('username',)
    readonly_fields = ('password',)
    fieldsets = (
        (None, {
            'fields': ('username', 'plain_password')
        }),
        ('Advanced', {
            'fields': ('password',),
            'classes': ('collapse',),
        }),
    )

    def has_password(self, obj):
        return bool(obj.password)
    has_password.short_description = 'Password Set'
    has_password.boolean = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # When editing, clear plain_password field
            form.base_fields['plain_password'].initial = ''
        return form
