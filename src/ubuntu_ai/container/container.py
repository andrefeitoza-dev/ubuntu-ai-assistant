from collections.abc import Callable
from dataclasses import replace
from typing import TypeVar, cast

from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.agent_loop import AgentLoopConfig, AgentLoopController
from ubuntu_ai.ai.ollama_provider import OllamaProvider
from ubuntu_ai.ai.provider import AIProvider
from ubuntu_ai.ai.registry import AIProviderRegistry
from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.conversation.engine import ConversationEngine
from ubuntu_ai.conversation.repository import ConversationRepository
from ubuntu_ai.conversation.service import ConversationService
from ubuntu_ai.conversation.sqlite_repository import SQLiteConversationRepository
from ubuntu_ai.core.config import AppConfig
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.execution_intelligence.discovery import DiscoveryEngine
from ubuntu_ai.execution_intelligence.engine import ExecutionIntelligence
from ubuntu_ai.execution_intelligence.preflight import PreflightEngine
from ubuntu_ai.knowledge.engine import KnowledgeEngine
from ubuntu_ai.knowledge.repository import KnowledgeRepository
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository
from ubuntu_ai.learning.engine import LearningEngine
from ubuntu_ai.learning.repository import LearningRepository
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.learning.sqlite_repository import SQLiteLearningRepository
from ubuntu_ai.memory.repository import MemoryRepository
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.memory.sqlite_repository import SQLiteMemoryRepository
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.planner.rule_planner import RulePlanner
from ubuntu_ai.plugins import PluginManager, PluginPolicy, PluginRegistry
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer
from ubuntu_ai.reflection.engine import ReflectionEngine
from ubuntu_ai.semantic import (
    RAGContextBuilder,
    SemanticKnowledgeService,
    SemanticRepository,
    SQLiteSemanticRepository,
)
from ubuntu_ai.services.ollama import OllamaService
from ubuntu_ai.skills import Skill, SkillManager, SkillRegistry, default_skills
from ubuntu_ai.tools.capability_registry import CapabilityRegistry
from ubuntu_ai.tools.selection import ToolSelectionEngine
from ubuntu_ai.tui.app import TerminalApp

T = TypeVar("T")


class Container:
    """Container simples para gerenciamento de dependências."""

    def __init__(self) -> None:
        self._singletons: dict[str, object] = {}

    def _singleton(
        self,
        key: str,
        factory: Callable[[], T],
    ) -> T:
        """Obtém ou cria um singleton."""

        if key not in self._singletons:
            self._singletons[key] = factory()

        return cast(T, self._singletons[key])

    def reset(self) -> None:
        """Descarta singletons para recompor a aplicação com segurança."""

        self._singletons.clear()

    def config(self) -> AppConfig:
        """Retorna a configuração única da aplicação."""

        return self._singleton("config", AppConfig)

    def ollama_service(self) -> OllamaService:
        """Retorna o cliente único do Ollama."""

        config = self.config()

        return self._singleton(
            "ollama_service",
            lambda: OllamaService(
                base_url=config.ollama_base_url,
                timeout=config.request_timeout,
            ),
        )

    def ollama_provider(self) -> OllamaProvider:
        """Retorna o provedor único baseado no Ollama."""

        config = self.config()

        return self._singleton(
            "ollama_provider",
            lambda: OllamaProvider(
                service=self.ollama_service(),
                model=config.ollama_model,
            ),
        )

    def ai_provider_registry(self) -> AIProviderRegistry:
        """Retorna o registro de provedores disponível na aplicação."""

        def factory() -> AIProviderRegistry:
            registry = AIProviderRegistry()
            registry.register("ollama", self.ollama_provider)
            return registry

        return self._singleton("ai_provider_registry", factory)

    def register_ai_provider(
        self,
        name: str,
        provider: AIProvider,
        *,
        replace_existing: bool = False,
        select: bool = False,
    ) -> None:
        """Registra uma instância de provedor para composição ou testes."""

        self.ai_provider_registry().register(
            name,
            lambda: provider,
            replace=replace_existing,
        )
        if select:
            self._singletons["config"] = replace(self.config(), ai_provider=name)
        self._singletons.pop("ai_provider", None)

    def ai_provider(self) -> AIProvider:
        """Retorna o provedor de IA selecionado pela configuração."""

        config = self.config()
        return self._singleton(
            "ai_provider",
            lambda: self.ai_provider_registry().create(config.ai_provider),
        )

    def plugin_registry(self) -> PluginRegistry:
        """Retorna o registro de plugins carregados."""

        return self._singleton("plugin_registry", PluginRegistry)

    def plugin_policy(self) -> PluginPolicy:
        """Retorna a política de admissão de plugins."""

        return self._singleton("plugin_policy", PluginPolicy)

    def plugin_manager(self) -> PluginManager:
        """Retorna o gerenciador do SDK de plugins."""

        return self._singleton(
            "plugin_manager",
            lambda: PluginManager(
                registry=self.plugin_registry(),
                skill_registry=self.skill_registry(),
            ),
        )

    def skill_registry(self) -> SkillRegistry:
        """Retorna o registro único de skills instaladas."""

        return self._singleton("skill_registry", lambda: SkillRegistry(default_skills()))

    def register_skill(self, skill: Skill, *, replace_existing: bool = False) -> None:
        """Registra uma skill e recompõe os componentes derivados."""

        self.skill_registry().register(skill, replace=replace_existing)
        for key in (
            "capability_registry",
            "skill_manager",
            "tool_selection_engine",
            "execution_intelligence",
            "execution_pipeline",
        ):
            self._singletons.pop(key, None)

    def skill_manager(self) -> SkillManager:
        """Retorna o orquestrador de skills."""

        return self._singleton(
            "skill_manager", lambda: SkillManager(self.skill_registry())
        )

    def capability_registry(self) -> CapabilityRegistry:
        """Compõe capacidades a partir das skills registradas."""

        return self._singleton(
            "capability_registry",
            lambda: CapabilityRegistry(self.skill_registry().capabilities()),
        )

    def tool_selection_engine(self) -> ToolSelectionEngine:
        """Retorna o mecanismo de seleção de ferramentas."""

        return self._singleton(
            "tool_selection_engine",
            lambda: ToolSelectionEngine(
                registry=self.capability_registry(),
                learning_service=self.learning_service(),
            ),
        )

    def discovery_engine(self) -> DiscoveryEngine:
        """Retorna o mecanismo de descoberta do ambiente."""

        return self._singleton("discovery_engine", DiscoveryEngine)

    def preflight_engine(self) -> PreflightEngine:
        """Retorna o mecanismo de verificações prévias."""

        return self._singleton(
            "preflight_engine",
            lambda: PreflightEngine(self.discovery_engine()),
        )

    def execution_intelligence(self) -> ExecutionIntelligence:
        """Retorna a camada de inteligência anterior à execução."""

        return self._singleton(
            "execution_intelligence",
            lambda: ExecutionIntelligence(
                registry=self.capability_registry(),
                preflight=self.preflight_engine(),
                skill_manager=self.skill_manager(),
            ),
        )

    def rule_planner(self) -> RulePlanner:
        """Cria um planejador determinístico."""

        return RulePlanner()

    def ai_planner(self) -> AIPlanner:
        """Cria um planejador baseado em IA."""

        return AIPlanner(
            provider=self.ai_provider(),
            knowledge_service=self.knowledge_service(),
            learning_service=self.learning_service(),
            rag_context_builder=self.rag_context_builder(),
        )

    def planner(self) -> Planner:
        """Cria o orquestrador de planejamento."""

        return Planner(
            rule_planner=self.rule_planner(),
            ai_planner=self.ai_planner(),
            tool_selector=self.tool_selection_engine(),
        )

    def preview_builder(self) -> PreviewBuilder:
        """Cria o construtor de previews."""

        return PreviewBuilder()

    def preview_renderer(self) -> PreviewRenderer:
        """Cria o renderizador de previews."""

        return PreviewRenderer()

    def execution_pipeline(self) -> ExecutionPipeline:
        """Cria o pipeline de planejamento e preview."""

        return ExecutionPipeline(
            planner=self.planner(),
            preview_builder=self.preview_builder(),
            preview_renderer=self.preview_renderer(),
        )

    def register_knowledge_repository(
        self,
        repository: KnowledgeRepository,
    ) -> None:
        """Registra a implementação concreta do repositório de conhecimento."""

        self._singletons["knowledge_repository"] = repository
        self._singletons.pop("knowledge_service", None)
        self._singletons.pop("knowledge_engine", None)

    def knowledge_repository(self) -> KnowledgeRepository:
        """Retorna o backend de conhecimento previamente registrado."""

        return self._singleton(
            "knowledge_repository",
            SQLiteKnowledgeRepository,
        )

    def knowledge_service(self) -> KnowledgeService:
        """Retorna o serviço de conhecimento desacoplado do backend."""

        return self._singleton(
            "knowledge_service",
            lambda: KnowledgeService(self.knowledge_repository()),
        )

    def knowledge_engine(self) -> KnowledgeEngine:
        """Retorna o mecanismo de ingestão e busca de conhecimento."""

        return self._singleton(
            "knowledge_engine",
            lambda: KnowledgeEngine(self.knowledge_service()),
        )

    def register_semantic_repository(
        self,
        repository: SemanticRepository,
    ) -> None:
        """Registra o backend de embeddings e recompõe o RAG."""

        self._singletons["semantic_repository"] = repository
        for key in ("semantic_knowledge_service", "rag_context_builder"):
            self._singletons.pop(key, None)

    def semantic_repository(self) -> SemanticRepository:
        """Retorna a persistência local de embeddings."""

        def factory() -> SemanticRepository:
            knowledge_repository = self.knowledge_repository()
            database_path = getattr(knowledge_repository, "database_path", None)
            return SQLiteSemanticRepository(database_path)

        return self._singleton("semantic_repository", factory)

    def semantic_knowledge_service(self) -> SemanticKnowledgeService:
        """Retorna o serviço de indexação e recuperação semântica."""

        return self._singleton(
            "semantic_knowledge_service",
            lambda: SemanticKnowledgeService(
                knowledge_service=self.knowledge_service(),
                repository=self.semantic_repository(),
            ),
        )

    def rag_context_builder(self) -> RAGContextBuilder:
        """Retorna o construtor de contexto RAG usado pelo Planner."""

        return self._singleton(
            "rag_context_builder",
            lambda: RAGContextBuilder(self.semantic_knowledge_service()),
        )

    def register_learning_repository(
        self,
        repository: LearningRepository,
    ) -> None:
        """Registra uma implementação de persistência do aprendizado."""

        self._singletons["learning_repository"] = repository
        self._singletons.pop("learning_service", None)
        self._singletons.pop("learning_engine", None)

    def learning_repository(self) -> LearningRepository:
        """Retorna o repositório persistente de aprendizado."""

        return self._singleton("learning_repository", SQLiteLearningRepository)

    def learning_service(self) -> LearningService:
        """Retorna o serviço único de aprendizado."""

        return self._singleton(
            "learning_service",
            lambda: LearningService(self.learning_repository()),
        )

    def learning_engine(self) -> LearningEngine:
        """Retorna a fachada de alto nível do aprendizado."""

        return self._singleton(
            "learning_engine",
            lambda: LearningEngine(self.learning_service()),
        )

    def memory_repository(self) -> MemoryRepository:
        """Retorna o repositório persistente de memória."""

        return self._singleton(
            "memory_repository",
            SQLiteMemoryRepository,
        )

    def memory_service(self) -> MemoryService:
        """Retorna o serviço único de memória."""

        return self._singleton(
            "memory_service",
            lambda: MemoryService(self.memory_repository()),
        )

    def conversation_repository(self) -> ConversationRepository:
        """Retorna o repositório persistente de conversas."""

        return self._singleton(
            "conversation_repository",
            SQLiteConversationRepository,
        )

    def conversation_service(self) -> ConversationService:
        """Retorna o serviço único de conversas."""

        return self._singleton(
            "conversation_service",
            lambda: ConversationService(self.conversation_repository()),
        )

    def conversation_engine(self) -> ConversationEngine:
        """Retorna o mecanismo persistente de conversação."""

        return self._singleton(
            "conversation_engine",
            lambda: ConversationEngine(self.conversation_service()),
        )

    def context_engine(self) -> ContextEngine:
        """Cria o mecanismo de contexto para uma sessão do runtime."""

        return ContextEngine(memory_service=self.memory_service())

    def reflection_engine(self) -> ReflectionEngine:
        """Retorna o mecanismo único de autorreflexão."""

        return self._singleton("reflection_engine", ReflectionEngine)

    def agent_loop_controller(self) -> AgentLoopController:
        """Retorna o controlador iterativo com limites configuráveis."""

        config = self.config()
        return self._singleton(
            "agent_loop_controller",
            lambda: AgentLoopController(
                runtime=self.agent_runtime(),
                config=AgentLoopConfig(
                    max_iterations=config.agent_loop_max_iterations,
                    max_stalled_iterations=(
                        config.agent_loop_max_stalled_iterations
                    ),
                ),
            ),
        )


    def terminal_app(self) -> TerminalApp:
        """Retorna a interface interativa de terminal."""

        return TerminalApp(
            controller=self.agent_loop_controller(),
            memory_service=self.memory_service(),
            plugin_registry=self.plugin_registry(),
        )

    def agent_runtime(self) -> AgentRuntime:
        """Cria o runtime central do agente."""

        return AgentRuntime(
            execution_pipeline=self.execution_pipeline(),
            memory_service=self.memory_service(),
            context_engine=self.context_engine(),
            conversation_engine=self.conversation_engine(),
            learning_service=self.learning_service(),
            execution_intelligence=self.execution_intelligence(),
            reflection_engine=self.reflection_engine(),
        )
