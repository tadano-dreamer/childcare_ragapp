# 保育RAGアプリ
## Demos  
＊GIFの表示に時間がかかる場合があります。  
デモ1【個別記録の追加】  
![保育RAG_デモ1](https://github.com/user-attachments/assets/7fd2350d-b9d6-44ea-b98a-f04d195be308)

デモ2【LLMによる月案（構成1-4）作成】  
![保育RAG_デモ2](https://github.com/user-attachments/assets/005f7e17-9939-4dea-b618-152f3cb6c830)

デモ3【RAGによる月案（構成5）作成】  
![保育RAG_デモ3](https://github.com/user-attachments/assets/bad4311b-6de8-4cbd-8843-a3f5fb01aa77)

## 起動方法

### 1．任意のフォルダにレポジトリをクローン
` git clone https://github.com/tadano-dreamer/childcare_ragapp.git`  

### 2．必要なモジュールのインストール
＊仮想環境でインストールする場合は先に`python -m venv venv`をターミナルに入力  

-1 `cd childcare_ragapp`  
-2 `pip install -r requirements.txt`　（5分ほどかかります）


### 3. Qdrantを立ち上げる

Dockerを利用して立ち上げます。ターミナルに以下を入力。
```
docker run -p 6333:6333 -p 6334:6334 -v ${pwd}/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### 4. qdrant_web_load.pyを実行し、ベクトルDBにデータを格納する
＊事前準備としてファイル内に：  
　・ファイル内にAPIキーを入力  
　・参考資料のパスを入力  
を行う  

以下をターミナルに入力
```
python ./makeplans/qdrant_load.py
```

＊childcare_ragappフォルダ内にqdrant_strageフォルダが作成されます  
＊ `localhost:6333/dashboard` でブラウザから格納データを確認可能

### 5. サーバを起動
＊事前準備として：  
　・makeplans/views.py内に2か所（雑設計ですが、、）APIキーを入力  
を行う  

ターミナルに以下を入力  
```
python manage.py runserver
```

`localhost:8000`でブラウザから挙動を確認

