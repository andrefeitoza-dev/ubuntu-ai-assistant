from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(command: tuple[str, ...], env: dict[str, str]) -> None:
    subprocess.run(command, check=True, env=env, shell=False)


def validate(wheel: Path, uv_executable: str) -> None:
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError("Informe um wheel existente.")

    with tempfile.TemporaryDirectory(prefix="ubuntu-ai-lifecycle-") as sandbox_value:
        sandbox = Path(sandbox_value)
        home = sandbox / "home"
        tool_dir = sandbox / "tools"
        bin_dir = sandbox / "bin"
        cache_dir = sandbox / "cache"
        for directory in (home, tool_dir, bin_dir, cache_dir):
            directory.mkdir(parents=True)

        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "XDG_CONFIG_HOME": str(home / ".config"),
                "XDG_DATA_HOME": str(home / ".local/share"),
                "XDG_STATE_HOME": str(home / ".local/state"),
                "XDG_CACHE_HOME": str(home / ".cache"),
                "UV_TOOL_DIR": str(tool_dir),
                "UV_TOOL_BIN_DIR": str(bin_dir),
                "UV_CACHE_DIR": str(cache_dir),
                "PATH": f"{bin_dir}:{env.get('PATH', '')}",
            }
        )

        run((uv_executable, "tool", "install", str(wheel)), env)

        entry_points = (
            bin_dir / "ubuntu-ai",
            bin_dir / "ubuntu-ai-gui",
            bin_dir / "ubuntu-ai-install-launcher",
        )
        missing = [
            path.name for path in entry_points if not path.is_file() or not os.access(path, os.X_OK)
        ]
        if missing:
            raise RuntimeError("Entry points ausentes ou não executáveis: " + ", ".join(missing))

        run((str(bin_dir / "ubuntu-ai-install-launcher"),), env)

        preserved = home / ".config/ubuntu-ai/release-marker"
        preserved.parent.mkdir(parents=True, exist_ok=True)
        preserved.write_text("preservar", encoding="utf-8")

        run((uv_executable, "tool", "install", "--force", str(wheel)), env)
        if preserved.read_text(encoding="utf-8") != "preservar":
            raise RuntimeError("A atualização não preservou os dados do usuário.")

        run((str(bin_dir / "ubuntu-ai-install-launcher"), "--uninstall"), env)
        run((uv_executable, "tool", "uninstall", "ubuntu-ai-assistant"), env)
        if any(bin_dir.iterdir()):
            raise RuntimeError("A desinstalação deixou comandos no diretório isolado.")
        if not preserved.is_file():
            raise RuntimeError("A desinstalação removeu dados preservados.")

    print("Ciclo de vida limpo aprovado: instalação, atualização e remoção.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida o ciclo de vida em ambiente isolado.")
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--uv", default=shutil.which("uv"))
    args = parser.parse_args()
    if not args.uv:
        raise SystemExit("uv não encontrado.")
    validate(args.wheel, args.uv)


if __name__ == "__main__":
    main()
