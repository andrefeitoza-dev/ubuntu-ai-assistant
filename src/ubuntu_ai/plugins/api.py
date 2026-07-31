from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ubuntu_ai.skills import Skill

PLUGIN_API_VERSION = 1


@dataclass(frozen=True, slots=True)
class PluginContext:
    """Narrow public context exposed during plugin initialization."""

    api_version: int = PLUGIN_API_VERSION


class UbuntuAIPlugin(ABC):
    """Stable public contract implemented by third-party plugins."""

    @abstractmethod
    def skills(self) -> tuple[Skill, ...]:
        """Return skills contributed by this plugin."""

    def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin without exposing internal runtime objects."""

        del context

    def shutdown(self) -> None:
        """Release resources owned by the plugin."""
