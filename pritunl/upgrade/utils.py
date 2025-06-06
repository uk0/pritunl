from pritunl.constants import *
from pritunl import settings
from pritunl import utils
from pritunl import logger

import pymongo
import base64

_prefix = None
_database = None

def database_setup():
    global _prefix
    global _database

    _prefix = settings.conf.mongodb_collection_prefix or ''
    client = pymongo.MongoClient(settings.conf.mongodb_uri,
        connectTimeoutMS=MONGO_CONNECT_TIMEOUT)
    _database = client.get_default_database()

def database_clean_up():
    global _prefix
    global _database
    _prefix = None
    _database = None

def get_collection(collection):
    return getattr(_database, _prefix + collection)

def setup_cert():
    server_cert = None
    server_key = None

    if _database is not None:
        settings_collection = get_collection('settings')
        doc = settings_collection.find_one({'_id': 'app'})
        if doc:
            server_cert = doc.get('server_cert')
            server_key = doc.get('server_key')

    if not server_cert or not server_key:
        logger.info('Generating setup server ssl cert', 'setup')
        server_cert, server_key = utils.generate_server_cert()

    server_cert = base64.b64encode(server_cert.encode()).decode()
    server_key = base64.b64encode(server_key.encode()).decode()

    return server_cert, server_key

def get_server_port():
    port = settings.conf.port

    if _database is not None:
        settings_collection = get_collection('settings')
        doc = settings_collection.find_one({'_id': 'app'})
        if doc:
            port = doc.get('server_port', 443)

    return port
