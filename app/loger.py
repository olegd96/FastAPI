import logging
import logging.handlers
from datetime import datetime

from pythonjsonlogger import jsonlogger
from app.config import settings

logger = logging.getLogger()

logHadler = logging.StreamHandler()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')

logHadler.setFormatter(formatter)
logger.addHandler(logHadler)
logger.setLevel(settings.LOG_LEVEL)

log_file = f"app/logs/fastapi-efk.log"
file = logging.handlers.TimedRotatingFileHandler(filename=log_file, when="midnight", backupCount=5)
file.setFormatter(formatter)
logger.addHandler(file)






