SERVER_NAME = 'localhost:5000'
DEBUG = True
SECRET_KEY = 'SERIOUSLY REPLACE THIS WITH RANDOM BYTES'

PROXY_FIX = False  # Set to True if behind a reverse proxy

FRESHBOOKS_URL = 'whatevs.freshbooks.com'
FRESHBOOKS_TOKEN = 'fjkdlsfjdsklfjdsklfjds'
FRESHBOOKS_USER_AGENT = 'ATX Hackerspace Payments'

RECAPTCHA_PUBLIC_KEY = 'SET THIS'
RECAPTCHA_PRIVATE_KEY = 'SET THIS TOO'

AD_USER_BASE_DN = 'ou=Batpass Users,dc=atxhs,dc=hack'
AD_GROUP_BASE_DN = 'ou=Batpass Groups,dc=atxhs,dc=hack'

AD_USER = 'username'
AD_PASSWD = 'passwordisabadpassword'
AD_SERVER_LIST = ['10.2.3.4', '10.3.4.5']
AD_USE_TLS = True
