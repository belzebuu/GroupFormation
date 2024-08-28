import logging.config
import yaml
from pathlib import Path 

#logger = logging.getLogger(__name__)

with open(Path.cwd()/'logging.yaml', 'r') as stream:
    lconfig = yaml.load(stream, Loader=yaml.FullLoader)
    # lconfig = yaml.safe_load(stream.read())
    logging.config.dictConfig(lconfig)
    #logging.config.fileConfig('logging.conf')
