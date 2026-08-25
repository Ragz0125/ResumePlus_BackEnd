import logging

logging.basicConfig(filename="debug_logger", filemode="w", level=logging.DEBUG,  format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

db_logger = logging.getLogger("db_module")
