# pgvector070-test

pgvector 0.7.0 のテスト

## テストの内容

- Cohere Embeds Multilingual 3.0 のバイナリベクトルを文字列形式に加工するテスト
- Titan Text Embeddings V2 の通常精度のベクトルをバイナリ量子化して DB に入れるテスト

---

テストに使うために組み込んでいるデータはこちら。

- https://huggingface.co/datasets/takaaki-inada/databricks-dolly-15k-ja-zundamon

> This dataset was based on "kunishou/databricks-dolly-15k-ja". This dataset is licensed under CC BY SA 3.0
>
> Last Update : 2023-05-11
>
> databricks-dolly-15k-ja
> https://github.com/kunishou/databricks-dolly-15k-ja
> databricks-dolly-15k
> https://github.com/databrickslabs/dolly/tree/master/data
