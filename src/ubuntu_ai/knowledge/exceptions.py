class KnowledgeError(Exception):
    """Erro base do domínio de conhecimento."""


class KnowledgeValidationError(KnowledgeError, ValueError):
    """Dados inválidos foram fornecidos ao mecanismo de conhecimento."""


class KnowledgeNotFoundError(KnowledgeError, LookupError):
    """O documento de conhecimento solicitado não foi encontrado."""


class KnowledgeRepositoryNotConfiguredError(KnowledgeError, RuntimeError):
    """Nenhuma implementação de KnowledgeRepository foi configurada."""
