import pathlib
import logging

from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import (register_connection, set_default_connection)

from . import config

settings = config.get_setting()

BASE_DIR = pathlib.Path(__file__).parent
CLUSTER_BUNDLE = str(BASE_DIR / "ignored"  / 'connect.zip')
ASTRA_DB_CLIENT_ID = settings.db_client_id
ASTRA_DB_CLIENT_SECRET = settings.db_client_secret

class CassandraSession:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CassandraSession, cls).__new__(cls)
            cls._instance.cloud_config = {'secure_connect_bundle': CLUSTER_BUNDLE}
            cls._instance.auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
            cls._instance.session = None
            cls._instance.cluster = None
        return cls._instance
    
    def connect(self):
        if self.session is None:
            try:
                self.cluster = Cluster(cloud=self.cloud_config, auth_provider=self.auth_provider)
                self.session = self.cluster.connect()
            except NoHostAvailable as e:
                logging.error(f"No host in the cluster could be contacted: {e}")
            except Exception as e:
                logging.error(f"An unspecified error occurred: {e}")
                
    @staticmethod
    def get_cluster():
        instance = CassandraSession()
        instance.connect()
        return instance.cluster
    
    @staticmethod
    def get_session():
        instance = CassandraSession()
        instance.connect()
        
        # Utilizar un nombre de conexión más descriptivo y fijo
        connection_name = "default_connection"
        
        # Registrar la conexión sólo si aún no se ha registrado
        try:
            register_connection(name=connection_name, session=instance.session)
            set_default_connection(connection_name)
        except Exception as e:
            logging.error(f"Failed to register or set the default connection: {e}")
        
        return instance.session
