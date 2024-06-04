# pgvector070-test

pgvector 0.7.0 および関連テスト

## テストの内容

- Cohere Embeds Multilingual 3.0 のバイナリベクトルを pgvector 0.7.0 で使えるよう文字列形式に加工するテスト

  - [`app_cohere_embed_bin_vector_test.py`](app_cohere_embed_bin_vector_test.py)
    - 現時点で pgvector にベクトルを保存する処理は未実装
  - https://cohere.com/blog/int8-binary-embeddings
  - https://docs.cohere.com/docs/embed-api
  - https://docs.cohere.com/reference/embed

- Titan Text Embeddings V2 の通常精度のベクトルをバイナリ量子化して DB に入れるテスト

  - [`app_titan2_re_rank_bin_index_text.py`](app_titan2_re_rank_bin_index_text.py)
    - Zenn の「[pgvector 0.7.0 でバイナリインデックス＆量子化を試してみた](https://zenn.dev/hmatsu47/articles/pgvector070-binaryvector)」を参照

- `.env`ファイルの内容はこちら。

```
COHERE_CRED='【Cohere EmbedのAPIキー】'
DB_NAME='【データベース名】'
DB_USER='【同・接続ユーザー名】'
DB_PASSWORD='【同・接続ユーザーのパスワード】'
DB_HOST='【データベースサーバーのエンドポイントURLまたはIPアドレス】'
DB_PORT='【同・ポート番号】'
```

---

後者のテストに使うために組み込んでいるデータはこちら。

- https://huggingface.co/datasets/takaaki-inada/databricks-dolly-15k-ja-zundamon
  - [`app_titan2_re_rank_bin_index_text.py`](app_titan2_re_rank_bin_index_text.py)と同じディレクトリに`databricks-dolly-15k-ja-zundamon.json`として配置

> This dataset was based on "kunishou/databricks-dolly-15k-ja". This dataset is licensed under CC BY SA 3.0
>
> Last Update : 2023-05-11
>
> databricks-dolly-15k-ja
> https://github.com/kunishou/databricks-dolly-15k-ja
> databricks-dolly-15k
> https://github.com/databrickslabs/dolly/tree/master/data
