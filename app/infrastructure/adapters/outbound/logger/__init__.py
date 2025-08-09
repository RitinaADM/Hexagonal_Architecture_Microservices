import sys
import structlog
import logging
from structlog.processors import (
    TimeStamper,
    JSONRenderer,
    format_exc_info,
)
from structlog.stdlib import (
    add_log_level,
    add_logger_name,
)

logging.getLogger("aio_pika").setLevel(logging.INFO)
logging.getLogger("aiormq").setLevel(logging.INFO)

def configure_structlog():
    # Процессор для добавления request_id
    def add_request_id(logger, method_name, event_dict):
        request_id = structlog.contextvars.get_contextvars().get('request_id')
        if request_id:
            event_dict['request_id'] = request_id
        return event_dict

    # Процессор для добавления endpoint
    def add_endpoint(logger, method_name, event_dict):
        endpoint = structlog.contextvars.get_contextvars().get('endpoint')
        if endpoint:
            event_dict['endpoint'] = endpoint
        return event_dict

    # Процессор для добавления client_ip
    def add_client_ip(logger, method_name, event_dict):
        client_ip = structlog.contextvars.get_contextvars().get('client_ip')
        if client_ip:
            event_dict['client_ip'] = client_ip
        return event_dict

    # Настройка structlog
    structlog.configure(
        processors=[
            add_request_id,
            add_endpoint,
            add_client_ip,
            add_log_level,
            TimeStamper(fmt="iso"),
            add_logger_name,
            format_exc_info,
            JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного логгера Python
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[console_handler],
        encoding='utf-8',
    )

def get_logger():
    logger = structlog.get_logger()
    logger.debug("DEBUG: Logger created")
    return logger