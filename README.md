# 保育RAGアプリ

## Demo 

## 起動方法

### 1．Qdrantを立ち上げる
Dockerを利用して立ち上げます。ターミナルに以下を入力。
```
docker run -p 6333:6333 -p 6334:6334 -v ${pwd}/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 2. child_care/qdrant_web_load.pyを実行し、ベクトルDBにデータを格納する
事前準備として：  
・ファイル内にAPIキーを入力  
・参考資料のパスを入力  
を行う  

＊ `localhost:6333/dashboard` でブラウザから格納データを確認可能

### 3. サーバを起動
また事前準備として：  
・makeplans/views.py内に2か所（雑設計ですみません、、）APIキーを入力  
を行う  

ターミナルに以下を入力  
`python manage.py runserver`  

`localhost:8000`でブラウザから挙動を確認

