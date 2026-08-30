from pathlib import Path

import pytest

from ubuntu_ai.gui.app import UbuntuAIApp
from ubuntu_ai.gui.backend import GUIBackend
from ubuntu_ai.gui.operational_queries import OperationalQueryResponder
from ubuntu_ai.interaction import InteractionRoute, InteractionRouter

LOCAL_PARAPHRASES = (
    ("01", "Quanta memória RAM este computador tem?"),
    ("01", "Exiba as informações gerais do meu computador."),
    ("02", "Que Ubuntu está instalado?"),
    ("02", "Mostre a versão do kernel."),
    ("03", "Diagnostique a lentidão do meu computador."),
    ("03", "Há algum serviço falhando?"),
    ("04", "Quais são os comandos Linux mais usados?"),
    ("04", "Para que serve o chmod?"),
    ("07", "Mostre o espaço disponível no disco."),
    ("08", "Mostre o IP deste computador."),
    ("09", "Verifique se o SSH está rodando."),
    ("10", "Liste os aplicativos instalados."),
    ("11", "Tenho Docker instalado?"),
    ("11", "Que versão do Python está instalada?"),
    ("17", "Como o systemd trabalha?"),
    ("17", "Explique o que significa serviço no Linux."),
    ("19", "Qual versão do Ubuntu AI está instalada?"),
    ("19", "Cheque a integridade da instalação do assistente."),
)

ACTION_PARAPHRASES = (
    ("05", "Encontre os PDFs na pasta Documentos."),
    ("05", "Mostre o maior diretório."),
    ("06", "Liste os processos que mais consomem RAM."),
    ("06", "Há quanto tempo o computador está ligado?"),
    ("07", "Liste os discos e partições."),
    ("09", "Exiba os logs do Docker."),
    ("12", "Inicie o navegador Firefox."),
    ("12", "Abra Documentos."),
    ("13", "Inicie o Firefox."),
    ("13", "Abra o painel de rede."),
    ("20", "Inicie o Visual Studio Code."),
)

OPERATIONAL_PARAPHRASES = (
    ("10", "Há pacotes para atualizar?"),
    ("14", "Liste minhas automações."),
    ("15", "Mostre as tarefas ativas."),
    ("15", "Liste os agendamentos."),
    ("18", "Liste os agentes disponíveis."),
    ("18", "Quais plugins estão disponíveis?"),
)

SPECIAL_PARAPHRASES = (
    ("08", "Faça um diagnóstico do servidor escolhido.", "remote"),
    ("14", "Cancele a automação escolhida.", "cancel"),
    ("16", "Investigue meu problema de conexão.", "multi-agent"),
    ("16", "Analise por que o disco está cheio.", "multi-agent"),
)


def test_paraphrase_matrix_covers_all_announced_topics_and_39_variations() -> None:
    cases = LOCAL_PARAPHRASES + ACTION_PARAPHRASES + OPERATIONAL_PARAPHRASES + SPECIAL_PARAPHRASES

    assert len(cases) == 39
    assert {case[0] for case in cases} == {f"{number:02}" for number in range(1, 21)}


@pytest.mark.parametrize(("_topic", "phrase"), LOCAL_PARAPHRASES)
def test_information_paraphrases_receive_deterministic_local_answers(
    _topic: str,
    phrase: str,
) -> None:
    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response


@pytest.mark.parametrize(("_topic", "phrase"), ACTION_PARAPHRASES)
def test_action_paraphrases_reach_safe_plans(
    _topic: str,
    phrase: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "Documents").mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.ACTION
    assert decision.response is None


@pytest.mark.parametrize(("_topic", "phrase"), OPERATIONAL_PARAPHRASES)
def test_operational_paraphrases_use_read_only_panel_responder(
    _topic: str,
    phrase: str,
) -> None:
    assert OperationalQueryResponder.matches(phrase)


@pytest.mark.parametrize(("_topic", "phrase", "handler"), SPECIAL_PARAPHRASES)
def test_special_paraphrases_reach_their_explicit_gui_handlers(
    _topic: str,
    phrase: str,
    handler: str,
) -> None:
    matched = {
        "remote": GUIBackend.is_remote_diagnostic_request(phrase),
        "cancel": GUIBackend.is_cancel_selected_automation_request(phrase),
        "multi-agent": UbuntuAIApp._multi_agent_request(phrase) is not None,
    }

    assert matched[handler]
