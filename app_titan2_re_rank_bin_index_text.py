import json
import psycopg
from psycopg.rows import dict_row
from psycopg import extras
from dotenv import load_dotenv
import os

# .env ファイルを読み込み
load_dotenv()

# データベース接続情報を環境変数から取得
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'sslmode': os.getenv('SSL_MODE'),
    'sslcert': os.getenv('SSL_CERT'),
    'sslkey': os.getenv('SSL_KEY'),
    'sslrootcert': os.getenv('SSL_ROOT_CERT')
}

# JSON ファイルのパス
JSON_FILE_PATH = './databricks-dolly-15k-ja-zundamon.json'

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS your_table_name (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

def insert_data(conn, data_list):
    insert_query = 'INSERT INTO your_table_name (id, data) VALUES %s'
    extras.execute_values(conn.cursor(), insert_query, data_list)

def main():
    try:
        # PostgreSQL に接続（Titan の呼び出しと Embedding には未対応）
        with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
            # 自動コミットを無効にしてトランザクションを管理
            conn.autocommit = False
            
            # テーブル作成
            create_table(conn)

            # JSON ファイルを読み込み
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

                # データリストの作成
                data_list = [
                    (int(item['index']), item['input']) 
                    for item in json_data if item['input']
                ]

                # データをバッチ挿入
                insert_data(conn, data_list)
            
            # 全行挿入後にコミット
            conn.commit()
    
    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.rollback()
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
