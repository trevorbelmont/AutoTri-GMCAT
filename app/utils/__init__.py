from .logger import logger, log_queue, log_path, section_log, reset_log_file
from .formatters import format_by_pattern, format_by_pattern2
from .pastas import abrir_pasta, criar_pasta_resultados
from .web_driver import driver_context
from .relatorio import (
    normalizar_nome,
    extrair_elementos_do_endereco_para_comparacao,
    parse_area,
    formatar_area,
)
from .decorators import retry

# O que é importado (variáveis, classes e métodos)
__all__ = [
    
    "logger",
    "log_queue",
    "log_path",
    "section_log",
    "reset_log_file",
    "format_by_pattern",
    "format_by_pattern2",
    "abrir_pasta",
    "driver_context",
    "criar_pasta_resultados",
    "normalizar_nome",
    "extrair_elementos_do_endereco_para_comparacao",
    "parse_area",
    "formatar_area",
    "retry",
]
