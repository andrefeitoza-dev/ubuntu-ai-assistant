class PluginError(RuntimeError):
    """Base exception for plugin lifecycle failures."""


class PluginManifestError(PluginError):
    """Raised when a plugin manifest is invalid."""


class PluginCompatibilityError(PluginError):
    """Raised when a plugin targets an unsupported API version."""


class PluginPermissionError(PluginError):
    """Raised when a plugin requests a permission that is not allowed."""


class PluginLoadError(PluginError):
    """Raised when a plugin module cannot be imported or initialized."""


class PluginTrustError(PluginPermissionError):
    """Raised when plugin contents were not explicitly trusted."""
