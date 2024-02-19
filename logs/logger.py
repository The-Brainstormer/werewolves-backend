from calendar import c
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')


fh = logging.FileHandler('logs/werewolf.log')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)
