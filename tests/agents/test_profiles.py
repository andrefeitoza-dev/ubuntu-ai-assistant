from __future__ import annotations

from pathlib import Path

import pytest

from ubuntu_ai.agents import (
    AgentKind,
    AgentProfile,
    AgentProfilePolicy,
    AgentProfileRepository,
    default_agent_profiles,
)


def test_default_profiles_are_restrictive() -> None:
    profiles = default_agent_profiles()

    assert {profile.kind for profile in profiles} == {
        AgentKind.SYSTEM,
        AgentKind.NETWORK,
        AgentKind.STORAGE,
        AgentKind.SERVICES,
    }
    assert all(not profile.allow_sensitive for profile in profiles)
    assert all(profile.environments == {"local"} for profile in profiles)


def test_profile_cannot_expand_agent_executables() -> None:
    profile = AgentProfile(
        name="network-unsafe",
        kind=AgentKind.NETWORK,
        executables=frozenset({"ip", "systemctl"}),
    )

    with pytest.raises(PermissionError, match="ampliar executáveis"):
        AgentProfilePolicy().validate(profile)


def test_profile_cannot_include_elevation() -> None:
    with pytest.raises(ValueError, match="elevação"):
        AgentProfile(
            name="system-unsafe",
            kind=AgentKind.SYSTEM,
            executables=frozenset({"sudo"}),
        )


def test_profile_repository_roundtrip_and_permissions(tmp_path: Path) -> None:
    path = tmp_path / "profiles" / "catalog.json"
    repository = AgentProfileRepository(path)
    profiles = default_agent_profiles()

    repository.save(profiles)

    assert repository.load() == profiles
    assert path.stat().st_mode & 0o777 == 0o600
