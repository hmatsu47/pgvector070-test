import boto3
from dotenv import load_dotenv
import json
import numpy as np
import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector
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

# ベクトル長
VECTOR_SIZE = 1024

# テーブル作成
def create_table(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS rerank_test (id INTEGER PRIMARY KEY, data TEXT, embedding vector(%d))', VECTOR_SIZE)
    conn.commit()

# データ行挿入
def insert_data(conn, index, data, embedding):
    conn.execute('INSERT INTO your_table_name (id, data, embedding) VALUES (%s, %s, %s)', (index, data, embedding,))

# 埋め込みベクトルを生成
def generate_embeddings(input_text, dimensions, normalize, client=None):
    """
    Invoke Amazon Titan Text Embeddings G1 and print the response.

    :param input_text: The text to convert to an embedding.
    :param dimensions: The number of dimensions the output embeddings should have.
    :param normalize:  flag indicating whether or not to normalize the output embeddings.
    :param client:     An optional Bedrock Runtime client instance.
                       Defaults to None if not provided.
    :return: The model's response object.
    """

    # Create a Bedrock Runtime client if not provided.
    client = client or boto3.client("bedrock-runtime", region_name="us-west-2")

    # Set the model ID, e.g., Titan Text Embeddings V2.
    model_id = "amazon.titan-embed-text-v2:0"

    # Create the request for the model.
    request = {"inputText": input_text, "dimensions": dimensions, "normalize": normalize}

    # Encode and send the request.
    response = client.invoke_model(
        body=json.dumps(request),
        modelId=model_id,
    )

    # Decode the response
    model_response = json.loads(response["body"].read())

    # Extract the generated embedding.
    embedding = model_response["embedding"]

    return embedding

def main():
    try:
        # PostgreSQL に接続
        with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
            # 自動コミットを無効にしてトランザクションを管理
            conn.autocommit = False

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
                if data:  # input が空文字でない場合のみ埋め込みベクトルを取得してテーブルに行挿入
                    embedding = generate_embeddings(data, VECTOR_SIZE, True)
                    insert_data(conn, index, data, np.array(embedding))
            
            # 全行挿入後にコミット
            conn.commit()
    
    except Exception as e:
        # エラーが発生した場合はロールバック
        conn.rollback()
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
