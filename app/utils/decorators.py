import time
from functools import wraps
from .logger import logger


def retry(max_retries=None, delay=None, exceptions=(Exception,)):
    """
    Decorador para repetir a execução de uma função em caso de erro.
    Nesse contexto, não é necessário refresh do Selenium, porque
    cada tentativa recria o driver.

    Args:
        max_retries (int): número máximo de tentativas.
        delay (float): tempo (segundos) para esperar entre tentativas.
        exceptions (tuple): exceções que devem disparar retry.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from utils import settings

            v_max_retries = max_retries if max_retries is not None else settings.RETRY_MAX
            v_delay = delay if delay is not None else settings.RETRY_DELAY 

            for attempt in range(1, v_max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.error(
                        "Erro na execução de %s (tentativa %d/%d): %s",
                        func.__name__,
                        attempt,
                        v_max_retries,
                        e,
                    )
                    if attempt < v_max_retries:
                        logger.info(
                            f"Aguardando {v_delay}s antes da próxima tentativa..."
                        )
                        time.sleep(v_delay)
                    else:
                        logger.error(
                            "Falha definitiva em %s após %d tentativas",
                            func.__name__,
                            v_max_retries,
                        )
                        raise

        return wrapper

    return decorator
