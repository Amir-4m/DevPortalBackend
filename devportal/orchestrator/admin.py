import json

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Customer, Settings, Project, ProjectConfiguration, Component, GitRepo, Account, Organisation, \
    Pipeline, ProjectConfigurationComponent

admin.site.register(Customer)
admin.site.register(Project)
admin.site.register(ProjectConfiguration)
admin.site.register(Organisation)
admin.site.register(Component)
admin.site.register(Account)
admin.site.register(Pipeline)
admin.site.register(ProjectConfigurationComponent)

from django.contrib import messages
from django.utils.translation import ngettext, gettext


class Dictionary(dict):
    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self)


class SettingsAdminForm(forms.ModelForm):
    raw_value = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Settings
        fields = ['key', 'raw_value', 'data_type']

    def clean(self):
        raw_value = self.cleaned_data.get('raw_value')
        data_type = self.cleaned_data.get('data_type')
        try:
            data = eval(f"{data_type}({raw_value})")
            self.cleaned_data.update({"raw_value": data})
        except Exception:
            raise ValidationError(_('Enter your raw value in the shape of entered data type'))


@admin.register(Settings)
class ConfigModelAdmin(admin.ModelAdmin):
    form = SettingsAdminForm
    list_display = ('key', 'data_type', 'data_value')
    search_fields = ('key',)
    list_filter = ('data_type',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(ConfigModelAdmin, self).get_form(request, obj, change, **kwargs)
        if obj is not None:
            form.base_fields['raw_value'].initial = obj.value
        return form

    def save_model(self, request, obj, form, change):
        raw_value = form.cleaned_data.get('raw_value')
        obj.value = raw_value
        return super(ConfigModelAdmin, self).save_model(request, obj, form, change)


class GitRepoAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'account', 'state']
    ordering = ['name']
    actions = ['sync_repos']

    @admin.action(description='Sync selected repositories.')
    def sync_repos(self, request, queryset):
        try:
            for repo in queryset:
                repo.sync_repo()
            self.message_user(request, ngettext(
                '%d local_url was successfully marked as synced.',
                '%d repos were successfully marked as synced.',
                queryset.count(),
            ) % queryset.count(), messages.SUCCESS)
        except Exception as e:
            self.message_user(request, gettext(
                '%s',
            ) % e, messages.ERROR)


admin.site.register(GitRepo, GitRepoAdmin)
