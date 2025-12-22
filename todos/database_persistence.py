import psycopg2
from psycopg2.extras import DictCursor 

from contextlib import contextmanager 

class SessionPersistence:
    def __init__(self, session):
        pass
    
    @contextmanager
    def _database_connect(self):
        connection = psycopg2.connect(dbname="todos")
        try:
            with connection:
                yield connection 

        finally:
            connection.close()
    def find_list(self, list_id):
        pass
    
    def all_lists(self):
        pass
    
    def create_new_list(self, title): 
        pass
    
    def update_list_by_id(self, list_id, new_title):
        pass
    
    def delete_list(self, list_id):
        pass
    
    def create_new_todo(self, list_id, todo_title):
        pass

    def update_todo_status(self, list_id, todo_id, todo_status):
        pass
    
    def delete_todo_from_list(self, list_id, todo_id):
        pass
    
    def mark_all_completed(self, list_id):
        pass
