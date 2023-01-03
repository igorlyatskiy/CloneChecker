import configparser
import pathlib
import sys

config = configparser.ConfigParser()
config.read('config.cfg')

token = configparser.ConfigParser()
token.read('token.cfg')

sys.setrecursionlimit(config.getint('Settings', 'recursion_limit'))

GITHUB_TOKEN = token.get('Token', 'github_token')

SCRIPT_PATH = pathlib.Path(__file__).parent.absolute()
COMPARE_FILENAME = config.get('Settings', 'compare_file')
DOWNLOAD_DATA = config.getboolean('Settings', 'download_data')
UPPER_LIMIT = config.getfloat('Settings', 'upper_limit')
THRESHOLD = config.getfloat('Settings', 'threshold')
BUNDLE_FILENAME = config.get('Settings', 'bundle_filename')
TASK_NAME = config.get('Settings', 'task_name')
CONCAT_PATTERN = config.get('Settings', 'concat_pattern')
CSV_DELIMITER = config.get('Settings', 'csv_delimiter')

config = configparser.ConfigParser()
