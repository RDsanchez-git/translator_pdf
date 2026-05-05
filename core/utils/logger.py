import logging
import json
import time

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            log_record.update(extra_data)
        return json.dumps(log_record, ensure_ascii=False)

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Prevenir duplicidad si la función se llama varias veces
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.handlers = [handler]