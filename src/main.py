import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_directory = 'logs'
    os.makedirs(log_directory, exist_ok=True)
    log_filename = os.path.join(log_directory, 'application.log')

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler = RotatingFileHandler(log_filename, maxBytes=1024*1024, backupCount=5)
    log_handler.setFormatter(log_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(log_handler)

if __name__ == '__main__':
    setup_logging()
    # Rest of the application start-up code