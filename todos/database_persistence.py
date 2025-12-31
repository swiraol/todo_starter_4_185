from contextlib import contextmanager 

import logging
import psycopg2
from psycopg2.extras import DictCursor 

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class DatabasePersistence:
    def __init__(self):
        self._setup_schema()
    
    def _setup_schema(self):
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'lists';
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE lists (
                            id serial PRIMARY KEY,
                            title text NOT NULL UNIQUE 
                        );
                    """)
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'todos';
                """)
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        CREATE TABLE todos (
                            id serial PRIMARY KEY,
                            title text NOT NULL,
                            completed BOOLEAN DEFAULT false,
                            list_id NOT NULL
                                    REFERENCES lists (id) 
                                    ON DELETE CASCADE
                        );
                                   """)
    
    @contextmanager
    def _database_connect(self):
        connection = psycopg2.connect(dbname="todos")
        try:
            with connection:
                yield connection 

        finally:
            connection.close()

    def find_list(self, list_id):
        query = """
            SELECT lists.*,
                    COUNT(todos.id) AS todos_count,
                    COUNT(NULLIF(todos.completed, True)) as todos_remaining
            FROM lists
            WHERE lists.id = %s
            LEFT JOIN todos ON todos.list_id = lists.id
            GROUP BY lists.id
            ORDER BY lists.title
        """
        logger.info("Executing query: %s with list_id: %s", query, list_id)
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (list_id,))
                result = cursor.fetchone()
        lst = dict(result)
        
        return lst
        
    
    def all_lists(self):
        query = """
            SELECT lists.*,
                    COUNT(todos.id) AS todos_count,
                    COUNT(NULLIF(todos.completed, True)) as todos_remaining
            FROM lists
            LEFT JOIN todos ON todos.list_id = lists.id
            GROUP BY lists.id
            ORDER BY lists.title
        """
        logger.info("Executing query: %s", query)

        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
        lists = [dict(result) for result in results]
        
        return lists
    
    def create_new_list(self, title): 
        query = "INSERT INTO lists (title) VALUES (%s)"
        logger.info("Executing query: %s with title: %s", query, title)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (title,))

    def update_list_by_id(self, list_id, new_title):
        query = "UPDATE lists SET title = %s WHERE id = %s"
        logger.info("Executing query: %s with title: %s and id: %s", query, new_title, list_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_title, list_id,))
    
    def delete_list(self, list_id):
        query = "DELETE FROM lists WHERE id = %s"
        logger.info("Executing query: %s with id: %s", query, list_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id,))

    def find_todos_for_list(self, list_id):
        query = "SELECT * FROM todos WHERE list_id = %s"
        logger.info("Executing query: %s where list_id: %s", query, list_id)
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (list_id,))
                results = cursor.fetchall()

        return results
    
    def create_new_todo(self, list_id, todo_title):
        query = "INSERT INTO todos (title, list_id) VALUES (%s, %s)"
        logger.info("Executing query: %s with title: %s and list_id: %s", query, todo_title, list_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (todo_title, list_id,))

    def update_todo_status(self, list_id, todo_id, todo_status):
        query = "UPDATE todos SET completed = %s WHERE list_id = %s and id = %s"
        logger.info("Executing query: %s with todo_status: %s, list_id: %s and id: %s", query, todo_status, list_id, todo_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (todo_status, list_id, todo_id,))

    def delete_todo_from_list(self, list_id, todo_id):
        query = "DELETE FROM todos WHERE list_id = %s and id = %s"
        logger.info("Executing query: %s with list_id: %s and id: %s", query, list_id, todo_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id, todo_id,))
    
    def mark_all_completed(self, list_id):
        query = "UPDATE todos SET completed = True WHERE list_id = %s"
        logger.info("Executing query: %s with list_id: %s", query, list_id)

        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id,))