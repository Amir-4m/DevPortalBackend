from django.contrib import admin
from .models import Customer, Settings, Project, ProjectConfiguration, Component, GitRepo, Account, Organisation, Pipeline


admin.site.register(Customer)
admin.site.register(Settings)
admin.site.register(Project)
admin.site.register(ProjectConfiguration)
admin.site.register(Organisation)
admin.site.register(Component)
admin.site.register(Account)
admin.site.register(Pipeline)

from django.contrib import messages
from django.utils.translation import ngettext, gettext


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
