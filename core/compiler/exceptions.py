
class CompilationServiceError(Exception):
    """Excepción base para fallos en el Bounded Context de compilación."""
    pass

class ProfileNotFoundError(CompilationServiceError):
    """El perfil heurístico no fue persistido o expiró antes de la compilación."""
    pass

class ASTConsistencyError(CompilationServiceError):
    """Corrupción del linaje: imposible reconciliar el AST con el resultado del Dispatcher."""
    pass

class AssemblyRejectedError(CompilationServiceError):
    """La decisión de ensamblado no admite publicación productiva conforme."""
    pass