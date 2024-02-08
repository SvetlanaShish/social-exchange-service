from ravendb import DocumentStore
from config import RAVEN_DB_URL, RAVEN_DB_NAME


def initialize_ravendb():
    # RavenDB configuration
    store = DocumentStore(urls=[RAVEN_DB_URL], database=RAVEN_DB_NAME)
    store.initialize()
    
    try:
        # Attempt to open a session for the database
        with store.open_session() as session:
            pass  # No need to perform any operation, just checking if the session can be opened
    except Exception as e:
        # Database doesn't exist, create it
        store.maintenance.server.send(DocumentStore.CreateDatabaseOperation(store.get_configuration_for_new_database(RAVEN_DB_NAME)))
        print(f"Database {RAVEN_DB_NAME} created.")

    return store
