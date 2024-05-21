import cohere
from dotenv import load_dotenv
import os

load_dotenv()
COHERE_CRED = os.getenv('COHERE_CRED')

co = cohere.Client(COHERE_CRED) # This is your trial API key

embeddings = co.embed(
  model='embed-multilingual-v3.0',
  texts=[
    '今日は良い天気ですね。',
    '今日は晴れましたね。',
    '昨日は良い天気でしたね。',
    '昨日は晴れましたね。',
    '今日は天気が悪いですね。',
    '今日は雨が降っていますね。',
    '昨日は天気が悪かったですね。',
    '昨日は雨が降りましたね。',
  ],
  input_type='search_document',
  embedding_types=['ubinary']
).embeddings.ubinary

for embedding in embeddings:
    bin_bector = ''
    for item in embedding:
        bin_bector += '{0:0=8b}'.format(item)
    print(bin_bector)
