import logging.config
from utils.exceptions import UndefinedLogHandler

LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'crawler': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': { 
        'crawler': {
            'handlers': ['crawler'],
            'level': 'DEBUG',
            'propagate': False
        },
    } 
}

def validate_handlers(name):
    """
     Validates if handler for the requested logger exists
    
    Args:
     name: name of the logger to be created
    
    Raises:
     UndefinedLogHandler: Error if handler does not exist for the logger
    """
    available_handlers = LOGGING_CONFIG['handlers'].keys()
    if name not in available_handlers:
        raise UndefinedLogHandler()

def get_logger(name='crawler'):
    """
     Creates and returns logger
    
     Args:
      name: Name of log handler
    
     Returns: Logger object
    """
    validate_handlers(name)
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(name)
    return logger