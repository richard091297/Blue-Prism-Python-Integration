from configparser import ConfigParser
from dotenv import load_dotenv
import os

# grab default parser from config file
parser = ConfigParser()
parser.read(r'./config.ini')

# load envrionment variables from local
load_dotenv()
environment = os.environ.get('environment')

# get configs
if environment == 'P':
    configs = parser['PROD']
else:
    configs = parser['DEV']
