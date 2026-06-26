from .launcher_panel import LauncherPanelMixin
from .intent_panel import IntentPanelMixin
from .scenario_actions_panel import ScenarioActionsPanelMixin


class ActionsPanelMixin(LauncherPanelMixin, IntentPanelMixin, ScenarioActionsPanelMixin):
    pass
