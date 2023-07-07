# Generated by Django 4.0.8 on 2023-02-04 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Account.', max_length=255)),
                ('creds', models.TextField(help_text='Credentials required to access the account.', verbose_name='Credentials')),
                ('url', models.URLField(help_text='URL of the account.', verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Account',
                'verbose_name_plural': 'Accounts',
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Component.', max_length=255)),
                ('version', models.CharField(help_text='The version of the component.', max_length=255)),
                ('systems', models.CharField(blank=True, help_text='The systems the component is compatible with.', max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'component',
                'verbose_name_plural': 'components',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Customer.', max_length=255)),
            ],
            options={
                'verbose_name': 'customer',
                'verbose_name_plural': 'customers',
            },
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Feature.', max_length=255)),
                ('version', models.CharField(help_text='The version of the feature.', max_length=255)),
                ('systems', models.CharField(blank=True, help_text='The systems the feature is compatible with.', max_length=255, null=True)),
                ('component', models.ForeignKey(help_text='The component the feature belongs to.', on_delete=django.db.models.deletion.CASCADE, to='orchestrator.component')),
                ('excludes_feature', models.ManyToManyField(blank=True, help_text='The features excluded by this feature.', to='orchestrator.feature')),
            ],
            options={
                'verbose_name': 'feature',
                'verbose_name_plural': 'features',
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Organisation.', max_length=255)),
                ('parent', models.ForeignKey(blank=True, help_text='Parent organisation of this organisation.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_query_name='sub_organisations', to='orchestrator.organisation')),
            ],
            options={
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
            },
        ),
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Pipeline.', max_length=255)),
                ('account', models.CharField(choices=[('org', 'Organization'), ('customer', 'Customer')], help_text='Indicates whether the account is an organization or customer.', max_length=10, verbose_name='Account')),
                ('source_type', models.CharField(choices=[('tf_cloud', 'TF Cloud'), ('codepipeline', 'CodePipeline'), ('mobile_build', 'Mobile Build')], help_text='Indicates the type of pipeline source.', max_length=20, verbose_name='Source Type')),
                ('url', models.URLField(help_text='URL or ID of the pipeline.', verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Pipeline',
                'verbose_name_plural': 'Pipelines',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='The key of the setting.', max_length=255)),
                ('value', models.TextField(help_text='The value of the setting.')),
                ('value_type', models.CharField(choices=[('string', 'String'), ('json', 'JSON'), ('timestamp', 'Timestamp')], default='string', help_text='The type of the value of the setting.', max_length=255)),
            ],
            options={
                'verbose_name': 'setting',
                'verbose_name_plural': 'settings',
            },
        ),
        migrations.CreateModel(
            name='ProjectConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the ProjectConfig.', max_length=255)),
                ('components', models.ManyToManyField(help_text='Which components do you wish to include?', to='orchestrator.component')),
                ('customer', models.ForeignKey(help_text='The customer the project configuration belongs to.', on_delete=django.db.models.deletion.CASCADE, to='orchestrator.customer')),
                ('features', models.ManyToManyField(help_text='Which features do you wish to include?', to='orchestrator.feature')),
                ('organisation', models.ForeignKey(help_text='The organisation the project configuration belongs to.', on_delete=django.db.models.deletion.CASCADE, to='orchestrator.organisation')),
                ('settings', models.ManyToManyField(blank=True, help_text='The settings of the project configuration.', related_name='projectconfig', to='orchestrator.settings')),
            ],
            options={
                'verbose_name': 'project configuration',
                'verbose_name_plural': 'project configurations',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Project.', max_length=255)),
                ('config', models.ForeignKey(help_text='Select which configuration the project will use to render its files.', on_delete=django.db.models.deletion.PROTECT, to='orchestrator.projectconfiguration', verbose_name='Configuration Template')),
                ('customer', models.ForeignKey(help_text='The customer the project belongs to.', on_delete=django.db.models.deletion.CASCADE, to='orchestrator.customer')),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
        ),
        migrations.AddField(
            model_name='organisation',
            name='settings',
            field=models.ManyToManyField(blank=True, help_text='Settings for the organisation.', related_query_name='organisation', to='orchestrator.settings'),
        ),
        migrations.CreateModel(
            name='GitRepo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the local_url.', max_length=255)),
                ('source_type', models.CharField(choices=[('github', 'GitHub'), ('codecommit', 'CodeCommit')], help_text='Indicates the type of source code repository.', max_length=10, verbose_name='Source Type')),
                ('url', models.URLField(help_text='URL of the repository.', verbose_name='URL')),
                ('account', models.ForeignKey(help_text='WHich accounts is used to connect to the service?', max_length=10, on_delete=django.db.models.deletion.PROTECT, to='orchestrator.account')),
            ],
            options={
                'verbose_name': 'Git Repository',
                'verbose_name_plural': 'Git Repositories',
            },
        ),
        migrations.AddField(
            model_name='feature',
            name='local_url',
            field=models.ForeignKey(blank=True, help_text='The local_url for the feature.', null=True, on_delete=django.db.models.deletion.PROTECT, to='orchestrator.gitrepo'),
        ),
        migrations.AddField(
            model_name='customer',
            name='settings',
            field=models.ManyToManyField(blank=True, help_text='Settings for the customers.', related_name='Settings', related_query_name='customer', to='orchestrator.settings'),
        ),
        migrations.AddField(
            model_name='component',
            name='local_url',
            field=models.ForeignKey(blank=True, help_text='The local_url for the component.', null=True, on_delete=django.db.models.deletion.PROTECT, to='orchestrator.gitrepo'),
        ),
        migrations.AddField(
            model_name='component',
            name='requires_component',
            field=models.ManyToManyField(blank=True, help_text='The components required by this component.', to='orchestrator.component'),
        ),
        migrations.AddField(
            model_name='account',
            name='organisation',
            field=models.ForeignKey(help_text='Organisation to which this account belongs.', on_delete=django.db.models.deletion.CASCADE, related_query_name='accounts', to='orchestrator.organisation'),
        ),
        migrations.AddField(
            model_name='account',
            name='settings',
            field=models.ManyToManyField(blank=True, help_text='Settings for the account.', related_query_name='account', to='orchestrator.settings'),
        ),
    ]
