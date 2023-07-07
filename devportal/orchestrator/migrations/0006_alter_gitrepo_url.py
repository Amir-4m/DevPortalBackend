# Generated by Django 4.0.8 on 2023-02-06 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrator', '0005_alter_gitrepo_source_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitrepo',
            name='url',
            field=models.CharField(help_text='URL of the repository.', max_length=255, verbose_name='URL'),
        ),
    ]
