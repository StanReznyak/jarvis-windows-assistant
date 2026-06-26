from .settings_layout_panel import SettingsLayoutMixin
from .settings_visual_panel import SettingsVisualMixin
from .settings_runtime_panel import SettingsRuntimeMixin


class SettingsPanelMixin(SettingsLayoutMixin, SettingsVisualMixin, SettingsRuntimeMixin):
    pass
