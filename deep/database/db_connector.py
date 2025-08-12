import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from config import Config

class DatabaseConnector:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASS
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def get_biometric_template(self, user_id: str):
        """Recupera o template biométrico criptografado do banco de dados"""
        try:
            with self.conn.cursor(cursor_factory=DictCursor) as cursor:
                query = sql.SQL("""
                    SELECT encrypted_template FROM biometric_templates 
                    WHERE user_id = %s AND is_active = TRUE
                """)
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result['encrypted_template'] if result else None
        except Exception as e:
            print(f"Erro ao buscar template biométrico: {e}")
            return None
    
    def log_access(self, user_id: str, access_granted: bool):
        """Registra uma tentativa de acesso no banco de dados"""
        try:
            with self.conn.cursor() as cursor:
                query = sql.SQL("""
                    INSERT INTO access_logs 
                    (user_id, access_time, access_granted) 
                    VALUES (%s, NOW(), %s)
                """)
                cursor.execute(query, (user_id, access_granted))
                self.conn.commit()
        except Exception as e:
            print(f"Erro ao registrar acesso: {e}")
            self.conn.rollback()
    
    def close(self):
        if self.conn:
            self.conn.close()