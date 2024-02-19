from calendar import c
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(message)s')
formatter = logging.Formatter('%(message)s')

fh = logging.FileHandler('logs/werewolf.log')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

if (len(logger.handlers) > 0):
    logger.handlers[0].setFormatter(formatter)