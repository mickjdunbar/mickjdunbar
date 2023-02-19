import os
from os.path import dirname, join
from pathlib import Path
import datetime
import configparser
import collections
#ENV=os.getenv('ENV')


def get_config_section(config):
    if not hasattr(get_config_section, 'section_dict'):
        get_config_section.section_dict = collections.defaultdict()
        for section in config.sections():
            get_config_section.section_dict[section] = dict(config.items(section))

    return get_config_section.section_dict


PROPERTIES_FILE = "{dir}/config/server.properties".format(dir=".")
config = configparser.RawConfigParser()
config.read(PROPERTIES_FILE)
config_dict = get_config_section(config)
print(config_dict)
PROPERTIES = config_dict
LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
print("TIMEZONE -> " + str(LOCAL_TIMEZONE))
