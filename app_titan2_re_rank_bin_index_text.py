import boto3
from dotenv import load_dotenv
import json
import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
import os

# JSON ファイルのパス
JSON_FILE_PATH = './databricks-dolly-15k-ja-zundamon.json'
# JSON_FILE_PATH = './test_data.json'

# ベクトル長
VECTOR_SIZE = 1024

# データベース接続情報を環境変数から取得
def get_conn_config():
    return {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
    }

# pgvector 有効化
def enable_vector(conn):
    conn.execute('CREATE EXTENSION IF NOT EXISTS vector')

# テーブル作成
def create_table(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS rerank_test (id INTEGER PRIMARY KEY, data TEXT, embedding vector(%d))' % VECTOR_SIZE)
    conn.commit()

# データ行挿入
def insert_data(conn, index, data, embedding):
    conn.execute('INSERT INTO rerank_test (id, data, embedding) VALUES (%s, %s, %s)', (index, data, embedding))
    conn.commit()

# 埋め込みベクトルを生成
def generate_embeddings(input_text, dimensions, normalize):

    # Bedrock client 生成
    client = boto3.client("bedrock-runtime", region_name="us-west-2")

    # モデル ID 指定（Titan Text Embeddings V2）
    model_id = "amazon.titan-embed-text-v2:0"

    # リクエストを生成
    request = {"inputText": input_text, "dimensions": dimensions, "normalize": normalize}

    # リクエストをエンコードして送信
    response = client.invoke_model(
        body=json.dumps(request),
        modelId=model_id,
    )

    # レスポンスをデコード
    model_response = json.loads(response["body"].read())

    # embedding を取り出して返却
    embedding = model_response["embedding"]

    return embedding

def main():
    # .env ファイルを読み込み
    load_dotenv(verbose=True)

    # データベース接続情報を取得
    DB_CONFIG = get_conn_config()

    conn = None
    try:
        # PostgreSQL に接続
        with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:

            # pgvector 有効化
            enable_vector(conn)

            # コネクション（conn）に vector 型を登録
            register_vector(conn)
            
            # テーブル作成
            create_table(conn)

            # JSON ファイルを読み込み
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            # JSON から必要項目を抽出しテーブルに挿入
            for item in json_data:
                index = int(item['index'])
                data = item['input']
                question = item['instruction']
                if data:  # input が空文字でない場合のみ埋め込みベクトルを取得
                    embedding = None
                    try:
                        embedding = generate_embeddings(data, VECTOR_SIZE, True)
                    except Exception as e:
                        # 埋め込みベクトル取得でエラーが発生した場合は無視
                        embedding = None
                    if embedding:   # 埋め込みベクトルが正しく返った場合のみテーブルに行挿入
                        insert_data(conn, index, data, np.array(embedding))
                        # 行挿入できた場合は質問文も登録
                        enbedding = None
                        try:
                            embedding = generate_embeddings(question, VECTOR_SIZE, True)
                        except Exception as e:
                            # 埋め込みベクトル取得でエラーが発生した場合は無視
                            embedding = None
                        if embedding:   # 埋め込みベクトルが正しく返った場合のみテーブルに行挿入
                            insert_data(conn, index + 100000, question, np.array(embedding))
                        print(f"index: {index}")
    
    except Exception as e:
        # エラーが発生した場合はロールバック
        if conn:
            conn.rollback()
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
