from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilityTopic:
    code: str
    title: str
    capabilities: tuple[str, ...]
    examples: tuple[str, ...]
    kind: str
    risk: str
    confirmation: str
    availability: str


def _topic(
    code: str,
    title: str,
    capabilities: tuple[str, ...],
    examples: tuple[str, ...],
    *,
    kind: str = "Consulta e orientação",
    risk: str = "Baixo",
    confirmation: str = "Não para consultas",
    availability: str = "Local",
) -> CapabilityTopic:
    return CapabilityTopic(
        code,
        title,
        capabilities,
        examples,
        kind,
        risk,
        confirmation,
        availability,
    )


class CapabilityCatalog:
    """Catálogo navegável de recursos e exemplos do assistente."""

    _TOPICS = (
        _topic(
            "01",
            "Informações do computador",
            (
                "mostrar hostname e usuário",
                "consultar CPU e memória",
                "medir o consumo do assistente",
                "apresentar resumo",
            ),
            ("Quanto tenho de memória?", "Mostre um resumo deste computador."),
        ),
        _topic(
            "02",
            "Informações do sistema operacional",
            ("mostrar versão do Ubuntu", "mostrar kernel e arquitetura"),
            ("Qual a versão do Ubuntu?", "Qual é o kernel deste computador?"),
        ),
        _topic(
            "03",
            "Diagnóstico e cuidados do computador",
            (
                "verificar CPU, memória e discos",
                "identificar serviços com falha",
                "explicar problemas e possíveis soluções",
                "apresentar cuidados de desempenho, atualizações e segurança",
            ),
            ("Por que meu computador está lento?", "Existem serviços com falha?"),
            availability="Local e SSH",
        ),
        _topic(
            "04",
            "Comandos Linux",
            (
                "mostrar comandos por categoria",
                "explicar opções e argumentos",
                "fornecer exemplos e alertas seguros",
            ),
            ("Mostre os principais comandos Linux.", "Explique o comando chmod."),
            confirmation="Explicar não autoriza execução",
            availability="Local e SSH",
        ),
        _topic(
            "05",
            "Arquivos e diretórios",
            (
                "criar, copiar, mover e renomear",
                "localizar arquivos e calcular tamanhos",
                "verificar permissões",
            ),
            ("Localize arquivos PDF em Documentos.", "Qual pasta ocupa mais espaço?"),
            kind="Consulta ou ação",
            risk="Baixo a alto",
            confirmation="Obrigatória para alterações sensíveis",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "06",
            "Processos e desempenho",
            (
                "listar e explicar processos",
                "identificar consumo de CPU ou memória",
                "mostrar carga e tempo ligado",
            ),
            ("Quais processos usam mais memória?", "Mostre o tempo de atividade."),
            kind="Consulta ou ação",
            risk="Baixo; alto para encerramento",
            confirmation="Obrigatória para encerramento sensível",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "07",
            "Armazenamento e discos",
            ("mostrar discos e partições", "consultar espaço", "localizar arquivos grandes"),
            ("Mostre meus discos.", "Quanto espaço livre existe?"),
            kind="Consulta ou ação",
            risk="Baixo a crítico",
            confirmation="Obrigatória para alterações",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "08",
            "Rede e SSH — Administração remota",
            (
                "mostrar interfaces de rede, IP, rotas, portas e DNS",
                "testar conectividade",
                "cadastrar e diagnosticar computadores autorizados",
            ),
            ("Qual é meu endereço IP?", "Diagnostique o servidor selecionado."),
            kind="Consulta ou ação remota",
            risk="Baixo a crítico",
            confirmation="Conforme a operação",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "09",
            "Serviços do Ubuntu",
            ("listar serviços", "consultar estado e logs", "explicar systemctl e journalctl"),
            ("O serviço SSH está ativo?", "Mostre os logs do serviço Docker."),
            kind="Consulta ou ação",
            risk="Baixo a alto",
            confirmation="Obrigatória para alterações",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "10",
            "Pacotes e aplicativos",
            (
                "consultar programas instalados",
                "verificar versões e procurar pacotes",
                "preparar instalação, atualização ou remoção",
                "guiar limpeza e atualização com prévia e confirmação",
            ),
            ("Quais programas tenho instalados?", "Quais atualizações estão disponíveis?"),
            kind="Consulta ou ação",
            risk="Baixo a alto",
            confirmation="Obrigatória para alterações",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "11",
            "Docker e Python",
            ("verificar disponibilidade e versão", "consultar containers e ambiente Python"),
            ("O Docker está instalado?", "Qual a versão do Python?"),
            kind="Consulta ou ação",
            risk="Baixo a alto",
            confirmation="Conforme a alteração",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "12",
            "Ações no desktop",
            ("abrir aplicativos autorizados", "abrir diretórios e configurações"),
            ("Abra o Firefox.", "Abra minha pasta Documentos."),
            kind="Ação",
            confirmation="Conforme a ação",
            availability="Computador local com desktop",
        ),
        _topic(
            "13",
            "Abertura rápida de aplicativos e pastas",
            ("abrir Firefox", "abrir Documentos", "abrir configurações de rede"),
            ("Abra o Firefox.", "Abra as configurações de rede."),
            kind="Ação rápida",
            availability="Computador local com desktop",
        ),
        _topic(
            "14",
            "Automações e tarefas longas",
            (
                "criar tarefas acompanhadas",
                "mostrar progresso",
                "pausar, retomar ou cancelar",
                "consultar histórico auditável de ações",
            ),
            ("Mostre minhas automações.", "Cancele a tarefa selecionada."),
            kind="Automação",
            risk="Conforme as etapas",
            confirmation="Política aplicada a cada etapa",
        ),
        _topic(
            "15",
            "Tarefas em execução e agendamentos",
            ("mostrar tarefas e resultados", "consultar agendamentos locais seguros"),
            ("Quais tarefas estão em execução?", "Mostre meus agendamentos."),
            kind="Consulta ou agendamento",
            risk="Conforme a tarefa",
            confirmation="Quando a tarefa possuir risco",
        ),
        _topic(
            "16",
            "Agentes especializados",
            (
                "usar agentes de sistema, rede, armazenamento e serviços",
                "coordenar especialistas com limites",
                "replanejar sem contornar confirmações",
            ),
            ("Analise este problema de rede.", "Diagnostique a falta de espaço."),
            kind="Planejamento especializado",
            risk="Conforme as ações propostas",
            confirmation="Política centralizada",
            availability="Local e SSH autorizado",
        ),
        _topic(
            "17",
            "Conhecimento, conversação e comandos por voz",
            (
                "responder dúvidas",
                "explicar Linux e Ubuntu",
                "usar conhecimento local",
                "receber pedidos por voz com reconhecimento local em português",
                "ler respostas em voz alta com síntese local opcional",
            ),
            ("Explique como funciona o systemd.", "Leia suas respostas em voz alta."),
        ),
        _topic(
            "18",
            "Configurações, perfis e plugins",
            (
                "importar configurações sem segredos",
                "gerenciar perfis",
                "validar e aprovar plugins",
                "consultar o aprendizado persistente",
            ),
            ("Mostre os perfis de agentes.", "Mostre o catálogo de plugins."),
            kind="Consulta ou configuração",
            risk="Baixo a alto",
            confirmation="Obrigatória para confiança e alterações",
        ),
        _topic(
            "19",
            "Instalação, configuração da IA e manutenção",
            (
                "mostrar versão e integridade",
                "configurar Ollama e modelos pela interface gráfica",
                "preparar o reconhecimento local de voz",
                "atualizar ou remover o assistente preservando dados",
            ),
            ("Mostre a versão do assistente.", "Verifique a instalação."),
            kind="Consulta ou manutenção",
            risk="Baixo a alto",
            confirmation="Obrigatória para alterações",
        ),
        _topic(
            "20",
            "Integração com VS Code",
            ("acessar comandos seguros", "consultar diagnósticos", "iniciar tarefas autorizadas"),
            ("Abra o VS Code.",),
            kind="Integração opcional",
            risk="Conforme o comando",
            confirmation="Conforme a ação",
            availability="Local com extensão instalada",
        ),
    )

    _REQUESTS = {
        "help",
        "ajuda",
        "me ajude",
        "mostrar recursos",
        "mostre os recursos",
        "lista de recursos",
        "o que voce faz",
        "o que voce pode fazer",
        "o que posso pedir",
        "o que eu posso pedir",
        "o que posso perguntar",
        "o que eu posso perguntar",
        "que perguntas posso fazer",
        "quais perguntas posso fazer",
        "me de uma lista do que voce pode fazer",
        "me diga o que voce pode fazer",
        "me mostre o que voce pode fazer",
        "mostre o que voce pode fazer",
        "me de exemplos do que posso perguntar",
        "me mostre o que posso perguntar",
        "me diga o que posso perguntar",
        "liste o que voce pode fazer",
        "liste suas funcoes",
        "quais sao suas funcoes",
        "quais sao suas capacidades",
        "como voce pode ajudar",
        "quais comandos posso pedir",
        "mostrar capacidades",
        "mostre suas capacidades",
    }
    @property
    def topics(self) -> tuple[CapabilityTopic, ...]:
        return self._TOPICS

    def respond(self, request: str) -> str | None:
        if request in self._REQUESTS:
            return self.render()
        if request.startswith("ajuda sobre "):
            return self.detail(request.removeprefix("ajuda sobre "))
        return None

    def render(self) -> str:
        lines = ["O que o Ubuntu AI Assistant pode fazer:"]
        lines.extend(
            f"{topic.code}. {topic.title}\n   Você pode perguntar: “{topic.examples[0]}”"
            for topic in self._TOPICS
        )
        lines.extend(
            (
                "",
                "Digite “ajuda sobre rede” para detalhes de uma categoria.",
                "Use o botão Recursos e ajuda para abrir o painel visual.",
                "Ações sensíveis continuam sujeitas a confirmação.",
            )
        )
        return "\n".join(lines)

    def detail(self, query: str) -> str:
        topic = self.find(query)
        if topic is None:
            return "Categoria não encontrada.\n\n" + self.render()
        lines = [topic.title, "", "O assistente pode:"]
        lines.extend(f"• {item};" for item in topic.capabilities)
        lines.extend(("", "Exemplos:"))
        lines.extend(f"• {example}" for example in topic.examples)
        lines.extend(
            (
                "",
                f"Tipo: {topic.kind}",
                f"Risco: {topic.risk}",
                f"Confirmação: {topic.confirmation}",
                f"Disponibilidade: {topic.availability}",
            )
        )
        return "\n".join(lines)

    def find(self, query: str) -> CapabilityTopic | None:
        normalized = self._normalize(query)
        for topic in self._TOPICS:
            title = self._normalize(topic.title)
            if normalized in {topic.code, title} or normalized in title:
                return topic
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        return normalized.encode("ascii", "ignore").decode().lower().strip()
