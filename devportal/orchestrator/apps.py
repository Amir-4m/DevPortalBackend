from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrchestratorConfig(AppConfig):
    name = "orchestrator"
    verbose_name = _("Orchestrator")

    def ready(self):
        try:
            import orchestrator.signals  # noqa F401
        except ImportError:
            pass
