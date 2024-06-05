
#& Imports
# External Imports
import logging
import sys
import os

# Internal Imports
from Util.EnvironmentVariable import env

#& Logger
#* You can use like this: `log.info(...)`
class log:
    __logger = logging.getLogger()
    __logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s\t: %(message)s')

    log_directory = env("LOG_DIRECTORY")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        f = open(log_directory + "/judger.log", 'a')
        f.close()
    file_handler = logging.FileHandler(log_directory + "/judger.log")
    file_handler.setFormatter(formatter)
    __logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    __logger.addHandler(stream_handler)

    @classmethod
    def info(self, s):
        self.__logger.info(s)

    @classmethod
    def debug(self, s):
        self.__logger.debug(s)
        