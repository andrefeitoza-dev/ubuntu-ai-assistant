from __future__ import annotations

import argparse

from ubuntu_ai.distribution.first_run import (
    DEFAULT_MODEL,
    OLLAMA_INSTALL_URL,
    FirstRunSetup,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configura o runtime local do Ubuntu AI Assistant.",
    )
    parser.add_argument(
        "--pull-model",
        action="store_true",
        help=f"Baixa o modelo padrão {DEFAULT_MODEL}.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup = FirstRunSetup()
    status = setup.status()

    if not status.ollama_available:
        raise SystemExit(
            "Ollama não encontrado. Instale-o seguindo "
            + OLLAMA_INSTALL_URL
            + " e execute novamente."
        )
    if not status.ollama_running:
        raise SystemExit(
            "Ollama está instalado, mas não responde. Inicie o serviço e tente novamente."
        )
    if status.model_available:
        print(f"Configuração pronta. Modelo {status.model} disponível.")
        return
    if not args.pull_model:
        raise SystemExit(f"Modelo {status.model} ausente. Execute: ubuntu-ai-setup --pull-model")

    print(f"Baixando {status.model}. O processo pode levar alguns minutos...")
    result = setup.pull_model()
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "Não foi possível baixar o modelo.")
    print(f"Modelo {status.model} instalado. Ubuntu AI Assistant pronto para uso.")


if __name__ == "__main__":
    main()
