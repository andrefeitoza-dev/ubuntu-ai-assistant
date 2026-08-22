"""Valida OpenSSH real contra um servidor efêmero limitado a 127.0.0.1."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import asyncssh
from validate_multi_agent_ssh import validate as validate_multi_agent

from ubuntu_ai.gui.backend import GUIBackend
from ubuntu_ai.remote.models import RemoteCommand, RemoteHost, RemoteHostKind
from ubuntu_ai.remote.ssh_executor import SSHExecutor

USERNAME = "ubuntu-ai-test"
RESPONSES = {
    "true": "",
    "uname -srmo": "Linux ubuntu-ai-test 6.8.0 x86_64 GNU/Linux\n",
    "free -m": "Mem: 1024 256 768\n",
    "uptime": " 17:44:00 up 2 days, 1 user, load average: 0.10, 0.20, 0.30\n",
    "ip route": "default via 192.0.2.1 dev eth0\n",
    "df -h": "Filesystem Size Used Avail Use% Mounted on\n/dev/vda1 20G 5G 15G 25% /\n",
    "systemctl --failed --no-legend --plain": "",
}


async def handle_process(process: asyncssh.SSHServerProcess[str]) -> None:
    command = process.command or ""
    if command == "sleep-test":
        await asyncio.sleep(2)
        process.exit(0)
        return
    if command not in RESPONSES:
        process.stderr.write("command rejected by isolated test server\n")
        process.exit(126)
        return
    process.stdout.write(RESPONSES[command])
    process.exit(0)


def write_private_key(path: Path, key: asyncssh.SSHKey) -> None:
    path.write_bytes(key.export_private_key(format_name="openssh"))
    os.chmod(path, 0o600)


def write_known_hosts(path: Path, port: int, key: asyncssh.SSHKey) -> None:
    public = key.export_public_key(format_name="openssh").decode().strip()
    path.write_text(f"[127.0.0.1]:{port} {public}\n", encoding="utf-8")
    os.chmod(path, 0o600)


async def execute(executor: SSHExecutor, host: RemoteHost, command: RemoteCommand):
    return await asyncio.to_thread(executor.execute, host, command)


async def validate() -> None:
    with tempfile.TemporaryDirectory(prefix="ubuntu-ai-ssh-") as directory:
        root = Path(directory)
        isolated_home = root / "home"
        isolated_home.mkdir(mode=0o700)
        previous_home = os.environ.get("HOME")
        os.environ["HOME"] = str(isolated_home)
        server_key = asyncssh.generate_private_key("ssh-ed25519")
        client_key = asyncssh.generate_private_key("ssh-ed25519")
        wrong_key = asyncssh.generate_private_key("ssh-ed25519")

        authorized_keys = root / "authorized_keys"
        authorized_keys.write_bytes(client_key.export_public_key(format_name="openssh"))
        client_identity = root / "id_ed25519"
        wrong_identity = root / "wrong_ed25519"
        write_private_key(client_identity, client_key)
        write_private_key(wrong_identity, wrong_key)

        server = await asyncssh.create_server(
            None,
            "127.0.0.1",
            0,
            server_host_keys=[server_key],
            authorized_client_keys=str(authorized_keys),
            process_factory=handle_process,
        )

        try:
            port = server.get_port()
            known_hosts = root / "known_hosts"
            wrong_known_hosts = root / "wrong_known_hosts"
            write_known_hosts(known_hosts, port, server_key)
            write_known_hosts(
                wrong_known_hosts,
                port,
                asyncssh.generate_private_key("ssh-ed25519"),
            )

            executor = SSHExecutor()
            host = RemoteHost(
                name="isolated",
                kind=RemoteHostKind.SSH,
                hostname="127.0.0.1",
                user=USERNAME,
                port=port,
                identity_file=str(client_identity),
                known_hosts_file=str(known_hosts),
                connect_timeout=3,
            )

            success = await execute(executor, host, RemoteCommand(("uname", "-srmo"), 5))
            assert success.success
            assert "ubuntu-ai-test" in success.stdout

            unknown_identity = RemoteHost(
                name="unknown-identity",
                kind=RemoteHostKind.SSH,
                hostname="127.0.0.1",
                user=USERNAME,
                port=port,
                identity_file=str(client_identity),
                known_hosts_file=str(wrong_known_hosts),
                connect_timeout=3,
            )
            rejected_host = await execute(
                executor,
                unknown_identity,
                RemoteCommand(("true",), 5),
            )
            assert not rejected_host.success
            assert "host key verification failed" in rejected_host.stderr.lower()

            rejected_key_host = RemoteHost(
                name="wrong-key",
                kind=RemoteHostKind.SSH,
                hostname="127.0.0.1",
                user=USERNAME,
                port=port,
                identity_file=str(wrong_identity),
                known_hosts_file=str(known_hosts),
                connect_timeout=3,
            )
            rejected_key = await execute(
                executor,
                rejected_key_host,
                RemoteCommand(("true",), 5),
            )
            assert not rejected_key.success
            assert "permission denied" in rejected_key.stderr.lower()

            try:
                await execute(executor, host, RemoteCommand(("sleep-test",), 0.1))
            except TimeoutError:
                pass
            else:
                raise AssertionError("O timeout SSH não encerrou a execução.")

            backend = GUIBackend()
            backend.register_remote_host(
                name="isolated-multi-agent",
                hostname="127.0.0.1",
                user=USERNAME,
                port=port,
                identity_file=str(client_identity),
                known_hosts_file=str(known_hosts),
            )
            await asyncio.to_thread(validate_multi_agent, "isolated-multi-agent")
        finally:
            server.close()
            await server.wait_closed()
            if previous_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = previous_home


def main() -> int:
    asyncio.run(validate())
    print("Integração SSH isolada aprovada.")
    print("- autenticação por chave: OK")
    print("- known_hosts obrigatório: OK")
    print("- chave não autorizada recusada: OK")
    print("- timeout com encerramento: OK")
    print("- diagnóstico multiagente SSH: OK")
    print("- auditoria dos quatro especialistas: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
