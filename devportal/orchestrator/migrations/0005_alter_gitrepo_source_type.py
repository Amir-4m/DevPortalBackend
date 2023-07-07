# Generated by Django 4.0.8 on 2023-02-06 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrator', '0004_pipeline_project_pipeline_repo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitrepo',
            name='source_type',
            field=models.CharField(choices=[('github', 'GitHub'), ('codecommit', 'CodeCommit'), ('local', 'Local Filesystem')], help_text='Indicates the type of source code repository.', max_length=10, verbose_name='Source Type'),
        ),
    ]