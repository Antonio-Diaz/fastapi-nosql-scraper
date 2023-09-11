import logging
import logging.config
import os

class LoggingConfig:

    @staticmethod
    def setup_logging(log_dir='logs', log_level=logging.INFO):
        # Verificar si el directorio de registros existe; si no, crearlo
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configuración del registro
        logging_config = {
            'version': 1,
            'formatters': {
                'detailed': {
                    'class': 'logging.Formatter',
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': log_level,
                    'formatter': 'detailed',
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(log_dir, 'app.log'),
                    'mode': 'a',
                    'formatter': 'detailed',
                },
            },
            'root': {
                'level': log_level,
                'handlers': ['console', 'file']
            },
        }

        logging.config.dictConfig(logging_config)

# Uso de la clase
if __name__ == "__main__":
    LoggingConfig.setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Este es un mensaje informativo.")
    logger.error("Este es un mensaje de error.")
