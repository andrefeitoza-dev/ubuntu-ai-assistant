import pytest

from ubuntu_ai.plugins import PluginManifest, PluginPermissionError, PluginPolicy


def test_policy_blocks_unapproved_permission() -> None:
    manifest = PluginManifest.from_mapping(
        {
            "name": "unsafe",
            "version": "1",
            "api_version": 1,
            "entrypoint": "unsafe:Plugin",
            "permissions": ["shell.execute"],
        }
    )

    with pytest.raises(PluginPermissionError):
        PluginPolicy().validate(manifest)
