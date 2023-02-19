
from definitions import LOCAL_TIMEZONE, PROPERTIES
from os.path import dirname, join
import sys
import logging
import glob
import time
import datetime
from collections import OrderedDict
import os
import datetime
import sys
import time
import json
import requests
from logging.handlers import RotatingFileHandler
import json_log_formatter
import rich
from rich.logging import RichHandler
from rich.console import Console
console = Console()
#########################################################################
# setup
#########################################################################
# Get environment variables
ENV = os.getenv('ENV')
if ENV is None:
    ENV = 'dev'  # default env

class CPLogger:
    def __init__(self, name, config, default_extra=None):
        # print(str(config))
        self.name = name
        self.orchestrator_id = "NULL"
        self.local_tz = LOCAL_TIMEZONE
        logging.Formatter.converter = time.gmtime
        self.logger = logging.getLogger(name)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.propagate = False
        self.logger.setLevel(config['default']['log_level'])
        self.default_extra_general = {'time': time.time(
        ), 'ctime': time.ctime(), 'datetime-now': datetime.datetime.now()}
        if default_extra is None:
            self.default_extra = self.default_extra_general
        else:
            self.default_extra = dict(default_extra)
            self.default_extra.update(self.default_extra_general)

        #self.sh = logging.StreamHandler(sys.stdout)
        self.sh = RichHandler(rich_tracebacks=True)

        log_name = ENV.lower()

        self.fh = RotatingFileHandler("{log_dir}/logs/cp.log".format(
            log_dir="."), mode='a', maxBytes=250000000, backupCount=4, encoding='utf-8', delay=0)

        self.json_formatter = json_log_formatter.JSONFormatter()
        self.default_formatter = logging.Formatter(
            f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.verbose_formatter = logging.Formatter(
            f'%(asctime)s - %(name)s - %(levelname)s - %(message)s ::: %(levelno)s - %(process)s - %(thread)s - %(threadName)s - %(relativeCreated)s - %(msecs)s - %(created)s - %(pathname)s')
        self.error_formatter = logging.Formatter(
            f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.simple_formatter = logging.Formatter(f'%(asctime)s - %(message)s')
        self.sh.setFormatter(self.json_formatter)
        self.fh.setFormatter(self.default_formatter)


    def set_orchestratorid(self, orchestratorid):
        self.orchestrator_id = orchestratorid

    def debug(self, message, extra=None, sessioninfo={}):
        if extra not in [None, {}]:
            extra.update(sessioninfo)
        self.logg('DEBUG', message, logg_extra=extra)

    def info(self, message, extra=None, sessioninfo={}):
        if extra not in [None, {}]:
            extra.update(sessioninfo)
        self.logg('INFO', message, logg_extra=extra)

    def warning(self, message, extra=None, sessioninfo={}):
        if extra not in [None, {}]:
            extra.update(sessioninfo)
        self.logg('WARNING', message, logg_extra=extra)

    def error(self, message, extra=None, sessioninfo={}):
        if extra not in [None, {}]:
            extra.update(sessioninfo)
        self.logg('ERROR', message, logg_extra=extra)

    def critical(self, message, extra=None, sessioninfo={}):
        if extra not in [None, {}]:
            extra.update(sessioninfo)
        self.logg('CRITICAL', message, logg_extra=extra)



    def exception(self, message, logg_extra=None):
        try:
            level = 'EXCEPTION'
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

            if logg_extra is None:
                dict_extra_combined = dict(self.default_extra)
            else:
                dict_extra_combined = dict(logg_extra)
                dict_extra_combined.update(self.default_extra)
            # finally
            dict_extra_combined.update({'level': level})

            # key value pairs
            log_extra_combined = ""
            if logg_extra is not None:
                for k, v in dict_extra_combined.items():
                    log_extra_combined = log_extra_combined + \
                        str(k) + "=" + str(v) + "|"
                logmessage = message + " ::: " + log_extra_combined
            else:
                logmessage = message

            # stream
            self.sh.setFormatter(self.json_formatter)
            self.logger.addHandler(self.sh)
            self.logg('ERROR', message, logg_extra=dict_extra_combined)
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

            # file
            # self.fh.setFormatter(self.error_formatter)
            # self.logger.addHandler(self.fh)
            # self.logg('ERROR', "{m}".format(m=logmessage),
            #           logg_extra=dict_extra_combined)
            # for handler in self.logger.handlers:
            #     self.logger.removeHandler(handler)

            # cloud
            self.gh.setFormatter(self.json_formatter)
            self.logger.addHandler(self.gh)
            self.logg('ERROR', "{m}".format(m=logmessage),
                      logg_extra=dict_extra_combined)
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)

        except Exception as e:
            pass

    def logg(self, level, message, logg_extra=None):

        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        if logg_extra is None:
            dict_extra_combined = dict(self.default_extra)
        else:
            dict_extra_combined = dict(logg_extra)
            dict_extra_combined.update(self.default_extra)
        # finally
        ct = str(time.ctime())
        now = str(datetime.datetime.now())
        ts = str(time.time())

        #dict_extra_combined.update({'level': level})
        dict_extra_combined.update(
            {'x_ct': ct, 'x_now': now, 'x_ts': ts, 'x_level': level, 'x_message': message})

        # key value pairs
        log_extra_combined = ""
        for k, v in dict_extra_combined.items():
            log_extra_combined = log_extra_combined + \
                str(k) + "=" + str(v) + "|"
        logmessage = message + " ::: " + log_extra_combined

        # stream
        self.sh.setFormatter(self.json_formatter)
        self.logger.addHandler(self.sh)
        if level == 'DEBUG':
            self.logger.debug(message, extra=dict_extra_combined)
        elif level == 'INFO':
            self.logger.info(message, extra=dict_extra_combined)
        elif level == 'WARNING':
            self.logger.warning(message, extra=dict_extra_combined)
        elif level == 'ERROR':
            self.logger.error(message, extra=dict_extra_combined)
            console.print(str(message), dict_extra_combined)
        elif level == 'CRITICAL':
            self.logger.critical(message, extra=dict_extra_combined)
            console.print(str(message), dict_extra_combined)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        # file
        self.fh.setFormatter(self.error_formatter)
        self.logger.addHandler(self.fh)
        if level == 'DEBUG':
            self.logger.debug("{m}".format(m=logmessage))
        elif level == 'INFO':
            self.logger.info("{m}".format(m=logmessage))
        elif level == 'WARNING':
            self.logger.warning("{m}".format(m=logmessage))
        elif level == 'ERROR':
            self.logger.error("{m}".format(m=logmessage))
        elif level == 'CRITICAL':
            self.logger.critical("{m}".format(m=logmessage))
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)


    def logg_unknown(self, level, message, logg_extra=None):
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        if logg_extra is None:
            dict_extra_combined = dict(self.default_extra)
        else:
            dict_extra_combined = dict(logg_extra)
            dict_extra_combined.update(self.default_extra)
        # finally
        dict_extra_combined.update({'tz': self.local_tz, 'level': level})

        # key value pairs
        log_extra_combined = "tz=" + self.local_tz + "|"
        for k, v in dict_extra_combined.items():
            log_extra_combined = log_extra_combined + \
                str(k) + "=" + str(v) + "|"
        logmessage = message + " ::: " + log_extra_combined

        # stream
        self.sh.setFormatter(self.json_formatter)
        self.logger.addHandler(self.sh)
        if level == 'DEBUG':
            self.logger.debug(message, extra=dict_extra_combined)
        elif level == 'INFO':
            self.logger.info(message, extra=dict_extra_combined)
        elif level == 'WARNING':
            self.logger.warning(message, extra=dict_extra_combined)
        elif level == 'ERROR':
            self.logger.error(message, extra=dict_extra_combined)
        elif level == 'CRITICAL':
            self.logger.critical(message, extra=dict_extra_combined)

        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

        if PROPERTIES['default']['log_print'] == "True":
            console.print(str(message), dict_extra_combined)

        # file
        # self.fhui.setFormatter(self.simple_formatter)
        # self.logger.addHandler(self.fhui)
        # if level == 'DEBUG':
        #     self.logger.debug("{m}".format(m=logmessage))
        # elif level == 'INFO':
        #     self.logger.info("{m}".format(m=logmessage))
        # elif level == 'WARNING':
        #     self.logger.warning("{m}".format(m=logmessage))
        # elif level == 'ERROR':
        #     self.logger.error("{m}".format(m=logmessage))
        # elif level == 'CRITICAL':
        #     self.logger.critical("{m}".format(m=logmessage))
        # for handler in self.logger.handlers:
        #     self.logger.removeHandler(handler)