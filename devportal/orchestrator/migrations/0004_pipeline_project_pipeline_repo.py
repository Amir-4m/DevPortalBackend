# Generated by Django 4.0.8 on 2023-02-05 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orchestrator', '0003_component_description_feature_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipeline',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='orchestrator.project'),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='local_url',
            field=models.ForeignKey(blank=True, help_text='The local_url for the feature.', null=True, on_delete=django.db.models.deletion.PROTECT, to='orchestrator.gitrepo'),
        ),
    ]
