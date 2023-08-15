from glob import glob
from django.db import models
from django.utils.translation import gettext_lazy as _
from picklefield.fields import PickledObjectField

from .utils import *


class Customer(models.Model):
    """
    Model representing a customer.
    """
    name = models.CharField(max_length=255, help_text=_('The name of the Customer.'))
    organisation = models.ForeignKey('Organisation', on_delete=models.PROTECT, blank=True, null=True)
    settings = models.ManyToManyField('Settings', _('Settings'), help_text=_('Settings for the customers.'), blank=True,
                                      related_query_name="customer")

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')

    def __str__(self):
        return self.name


class Settings(models.Model):
    """
    Model representing a setting.
    """
    TYPE_STR = 'str'
    TYPE_INT = 'int'
    TYPE_FLOAT = 'float'
    TYPE_LIST = 'list'
    TYPE_DICT = 'Dictionary'
    TYPE_BOOL = 'bool'
    TYPE_CHOICES = [
        (TYPE_STR, 'STR'),
        (TYPE_INT, 'INT'),
        (TYPE_FLOAT, 'FLOAT'),
        (TYPE_LIST, 'LIST'),
        (TYPE_DICT, 'DICT'),
        (TYPE_BOOL, 'BOOL'),

    ]
    key = models.CharField(verbose_name=_('Key'), max_length=100, unique=True)
    value = PickledObjectField(verbose_name=_('value'))
    data_type = models.CharField(verbose_name=_('value data type'), choices=TYPE_CHOICES, max_length=10)

    @property
    def data_value(self):
        return self.value

    def __str__(self):
        return self.key


class Organisation(models.Model):
    name = models.CharField(max_length=255, help_text=_('The name of the Organisation.'))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_query_name='sub_organisations', null=True,
                               blank=True, help_text=_('Parent organisation of this organisation.'))
    settings = models.ManyToManyField(Settings, help_text=_('Settings for the organisation.'), blank=True,
                                      related_query_name="organisation")

    class Meta:
        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')

    def __str__(self):
        return self.name


class Component(models.Model):
    """
    Model representing a component.
    """
    name = models.CharField(max_length=255, help_text=_('The name of the Component.'))
    description = models.CharField(max_length=255, help_text=_('A description for the Component.'), blank=True,
                                   null=True)
    repo = models.ForeignKey('GitRepo', on_delete=models.PROTECT, null=True, blank=True,
                             help_text=_('The local_url for the component.'))
    version = models.CharField(max_length=255, help_text=_('The version of the component.'))
    systems = models.CharField(max_length=255, blank=True, null=True,
                               help_text=_('The systems the component is compatible with.'))
    requires_component = models.ManyToManyField('self', blank=True,
                                                help_text=_('The components required by this component.'))

    class Meta:
        verbose_name = _('component')
        verbose_name_plural = _('components')

    def __str__(self):
        return self.name

    def render(self, output='../', settings=None, apps=[]):
        from copier import run_copy
        import subprocess
        data = {'project_name': 'devportal', 'module_name': self.repo.name}
        if isinstance(settings, dict) and settings.get('local_apps') is None:
            settings['local_apps'] = apps
        try:
            if os.path.isdir(f'{self.repo.local_url}/pre_process'):
                subprocess.run(
                    f'cd {self.repo.local_url}/pre_process && sh ./0get.sh {output} .copier-answers-preprocess_{self.repo.name}.yml \'{str(settings) if settings else ""}\'',
                    shell=True
                )
                git_commit(
                    output,
                    message=f"{self.repo.name} preprocess commit"
                )
            defaults = False
            if glob(os.path.join(output, "**", f'.copier-answers-{self.repo.name}.yml'), recursive=True):
                defaults = True
            run_copy(
                f'{self.repo.local_url}',
                output,
                unsafe=True,
                answers_file=f'.copier-answers-{self.repo.name}.yml',
                defaults=defaults,
                overwrite=True,
                data=data
            )

            git_commit(
                output,
                message=f"{self.repo.name} copier commit"
            )

            if os.path.isdir(f'{self.repo.local_url}/post_process'):
                subprocess.run(
                    f'cd {self.repo.local_url}/post_process && sh ./0get.sh {output} .copier-answers-postprocess_{self.repo.name}.yml',
                    shell=True
                )
                git_commit(
                    output,
                    message=f"{self.repo.name} postprocess commit"
                )
        except Exception as e:
            print('error', e)


class ProjectConfiguration(models.Model):
    """
    Model representing a project configuration.
    """
    name = models.CharField(max_length=255, help_text=_('The name of the ProjectConfig.'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 help_text=_('The customer the project configuration belongs to.'))
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                     help_text=_('The organisation the project configuration belongs to.'))
    components = models.ManyToManyField(Component, help_text=_("Which components do you wish to include?"),
                                        through='ProjectConfigurationComponent')
    # features = models.ManyToManyField(Feature, help_text=_("Which features do you wish to include?"))
    settings = models.ManyToManyField(Settings, help_text=_('The settings of the project configuration.'), blank=True,
                                      related_name="projectconfig")

    class Meta:
        verbose_name = _('project configuration')
        verbose_name_plural = _('project configurations')

    def __str__(self):
        return self.name


class ProjectConfigurationComponent(models.Model):
    """
    Through Model for a project configuration and component.
    """
    component = models.ForeignKey(Component, help_text=_("Which components do you wish to include?"),
                                  on_delete=models.PROTECT, related_name='config_components')
    config = models.ForeignKey(ProjectConfiguration, verbose_name=_("Configuration Template"), on_delete=models.PROTECT,
                               help_text=_("Select which configuration the project will use to render its files."))
    setting = models.ForeignKey(Settings, help_text=_('The settings of the component.'), null=True, blank=True,
                                related_name="config_components", on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('project configuration component')
        verbose_name_plural = _('project configuration components')

    def __str__(self):
        return f"{self.config.name} - {self.component.name}"


class Project(models.Model):
    """
    Model representing a project.
    """
    name = models.CharField(max_length=255, help_text=_('The name of the Project.'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 help_text=_('The customer the project belongs to.'))
    config = models.ForeignKey(ProjectConfiguration, verbose_name=_("Configuration Template"), on_delete=models.PROTECT,
                               help_text=_("Select which configuration the project will use to render its files."))

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def __str__(self):
        return self.name

    def render(self):
        print("rendering project {0}", self.name)
        self.pipelines.first().run()


class Account(models.Model):
    name = models.CharField(max_length=255, help_text=_('The name of the Account.'))
    organisation = models.ForeignKey('Organisation', on_delete=models.CASCADE, related_query_name='accounts',
                                     help_text=_('Organisation to which this account belongs.'))
    creds = models.TextField(_('Credentials'), help_text=_('Credentials required to access the account.'))
    url = models.URLField(_('URL'), help_text=_('URL of the account.'))
    settings = models.ManyToManyField(Settings, help_text=_('Settings for the account.'), blank=True,
                                      related_query_name="account")

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    def __str__(self):
        return self.name


class GitRepo(models.Model):
    SOURCE_TYPE_CHOICES = [('github', _('GitHub')), ('codecommit', _('CodeCommit')), ('local', _('Local Filesystem'))]
    STATE_CHOICES = [('new', _('New')), ('uptodate', _('Uo to date')), ('dirty', _('Not Clean')), ]
    name = models.CharField(max_length=255, help_text=_('The name of the local_url.'))
    account = models.ForeignKey(Account, max_length=10,
                                help_text=_('WHich accounts is used to connect to the service?'),
                                on_delete=models.PROTECT)
    source_type = models.CharField(_('Source Type'), max_length=10, choices=SOURCE_TYPE_CHOICES,
                                   help_text=_('Indicates the type of source code repository.'))
    url = models.CharField(_('URL'), max_length=255, help_text=_('URL of the repository.'))
    local_url = models.CharField(_('temp dir'), max_length=255, blank=True, default='',
                                 help_text=_('URL of the repository.'))
    state = models.CharField(_('Repo State'), max_length=16, default='new', help_text="Internal state of the local_url")

    class Meta:
        verbose_name = _('Git Repository')
        verbose_name_plural = _('Git Repositories')

    def __str__(self):
        return self.name

    def sync_repo(self):
        print("syncing local_url {0}".format(self.name))
        if self.state == 'new':
            self.init_repo()
        elif self.state == 'dirty':
            raise Exception(_('Repo is dirty on disk.'))
        else:
            self.pull()

    def pull(self):
        git_pull(self.local_url, repo=self)
        self.state == 'uptodate'
        self.save()

    def push(self):
        if self.source_type == 'github':
            pass
        elif self.source_type == 'codecommit':
            pass
        elif self.source_type == 'local':
            pass

    def init_repo(self):
        repo_dir = os.path.join(get_local_dir(), self.name)
        if self.source_type == 'github':
            # check if local_url exist, import instead
            remote_repo = github_check_repo(repo=self)
            if remote_repo is None:
                # create the repo if it does not
                remote_repo = github_create_repo(repo=self)
                # save the new url
                self.url = remote_repo.git_url
            else:
                print("Found {0}".format(remote_repo.name))
            # Clone the repo to local disk
            github_clone(repo=self, repo_dir=repo_dir)
            # update local source dir
            self.local_url = repo_dir
        elif self.source_type == 'codecommit':
            pass
        elif self.source_type == 'local':
            pass
        self.state = 'uptodate'
        self.save()

    def import_repo(self):
        if self.source_type == 'github':
            pass
        elif self.source_type == 'codecommit':
            pass
        elif self.source_type == 'local':
            pass

    def clone(self, destination):
        if self.source_type == 'github':
            pass
        elif self.source_type == 'codecommit':
            pass
        elif self.source_type == 'local':
            pass

    def commit(self, message):
        if self.source_type == 'github':
            pass
        elif self.source_type == 'codecommit':
            pass
        elif self.source_type == 'local':
            pass

    def delete_repo(self):
        raise NotImplementedError("Not deleting repos automatically.  because.")


class Pipeline(models.Model):
    SOURCE_TYPE_CHOICES = [('tf_cloud', _('TF Cloud')), ('codepipeline', _('CodePipeline')),
                           ('mobile_build', _('Mobile Build')), ('local_build', _('Local Build'))]
    name = models.CharField(max_length=255, help_text=_('The name of the Pipeline.'))
    account = models.ForeignKey(Account, max_length=10,
                                help_text=_('WHich accounts is used to connect to the service?'),
                                on_delete=models.PROTECT, related_name='pipeline')
    source_type = models.CharField(_('Source Type'), max_length=20, choices=SOURCE_TYPE_CHOICES,
                                   help_text=_('Indicates the type of pipeline source.'))
    url = models.URLField(_('URL'), help_text=_('URL or ID of the pipeline.'))
    project = models.ForeignKey(Project, on_delete=models.PROTECT, blank=True, null=True, related_name="pipelines")
    repo = models.ForeignKey(GitRepo, on_delete=models.PROTECT, null=True, blank=True,
                             help_text=_('The repo for the feature.'))

    class Meta:
        verbose_name = _('Pipeline')
        verbose_name_plural = _('Pipelines')

    def __str__(self):
        return self.name

    def run(self):
        print("running pipeline")
        # The next steps shouldnt be hardcoded here, but its fine for the PoC

        # Sync the pipeline's repo
        self.repo.sync_repo()
        # get all components for this project
        for component_config in self.project.config.components.through.objects.all():
            # update locate copy
            component_config.component.repo.sync_repo()
            # run copier for each component
            component_config.component.render(
                output=self.repo.local_url,
                settings=component_config.setting.value if component_config.setting else None,
                apps=list(self.project.config.components.exclude(pk=component_config.component.pk).values_list('repo__name', flat=True))
            )
            # run copier for the pipeline
