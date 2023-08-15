from django.core.management.base import BaseCommand, CommandError
from orchestrator.models import Project

class Command(BaseCommand):
    help = 'Process all of the pipelines of projects.'

    def add_arguments(self, parser):
        parser.add_argument('project_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        for project_id in options['project_ids']:
            try:
                project = Project.objects.get(pk=project_id)
                self.stdout.write(self.style.NOTICE('Initiating rendering for project "%s"' % project.name))
                project.render()
            except Project.DoesNotExist:
                raise CommandError('Project "%s" does not exist' % project_id)
            except Exception as e:
                self.stdout.write(self.style.ERROR('project "%s" could not render properly.' % project.name))
                raise CommandError('Here is the error output: %s' % e)
