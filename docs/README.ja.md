
*[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)*

# ProtoPie Enterprise オンプレミスサーバー用

これは、オンプレミスサーバー上でDocker Composeを使用してProtoPie Enterpriseをデプロイするための公式ガイドです。

始めるには、このリポジトリをクローンし、以下に詳述された必要な設定を行い、簡単にオンプレミスサーバーをデプロイしてください。

## ソフトウェア要件
 * Docker 1.13.0+
 * Docker Compose 1.10.0+
 
## ハードウェア要件
|             	| 数量 	| CPU(コア) 	| メモリ 	|
|-------------	|-----	|-----------	|--------	|
| 最小     	| 1   	| 1コア 64ビット	| 4GB    	|
| 推奨 	| 1   	| 2コア 64ビット | 8GB    	|
* ストレージ：保存されるプロトタイプの数によって異なります。

## OS要件
### Linux
* CentOS 7+
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### Windows
* Windows 10 64ビット: Pro、Enterprise、Education (1607記念日アップデート、ビルド14393以降)
### macOS
* 10.12+

## Docker Composeのサービス

ProtoPie Enterpriseは、Docker Compose内のdockerイメージとして構成された4つのサービスで構成されています。

* `nginx` - ウェブサーバー
* `web` - ウェブアプリケーションインターフェース
* `api` - バックエンドAPI
* `db` - データベースサーバー

docker hubからこれらのdockerイメージをプルするには、`docker login`を介してDocker IDでログインしてください。

## 前提条件

ProtoPie Enterpriseを実行する前に、以下のファイルを開き、以下の手順に従ってこれらのファイルをそれに応じて編集してください。

#### license.pem

`license.pem`ファイルを`docker-compose.yml`と同じディレクトリに移動します。

#### config.yml

`config.yml`ファイルには、ProtoPie Enterpriseの基本的な設定が含まれています。例えば、
* `servers.http`: ProtoPie Enterpriseが実行されるURLです。（例：http://your.domain）
* `mail.smtp`: メールを送信するためのSMTP設定です。（例：メンバーの招待やパスワードの変更）

#### db.env

`xxx.env`ファイルは、アプリケーション内の環境変数を表します。`db.env`には、初期DBを作成するための`root user`と`protopie db`の2つの部分の設定があります。

## 実行

前述のファイルを編集したら、`docker-compose.yml`のdockerコンテナをアップし、ProtoPie Enterpriseを実行する準備ができました。以下のコマンドを実行して、docker-composeを介してバックグラウンドでコンテナを実行します。

```bash
$ docker-compose -p protopie up -d
```

その後、`http://your.domain`でアクセスできます。他のポートを使用したい場合は、`docker-compose.yml`の`services.nginx.port`と`config.yml`の`servers.http`を変更してください。

コンテナが停止または削除されても、`db`データはホストファイルシステムにバインドマウントされているため、持続します。


## SSL/TLS証明書を使用したHTTPS
### OpenSSLでSSL証明書(.crt)を生成する。
OpenSSLを使用してSSL証明書(.crt)を作成する場合、プライベートキー(.key)と証明書署名要求(.csr)ファイルの両方が必要です。
以下のコマンドを使用します。
```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```
```bash
例 =>  openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

セキュリティと安全性の理由から、HTTPSの使用を強くお勧めします。SSL/TLS証明書をお持ちの場合、この設定を`nginx.conf`ファイルに適切に挿入してください。

```nginx conf
          .
          .
          .
     server {
        listen       443;
        server_name  localhost;
        ssl     on;
        ssl_certificate         修正 => dockerコンテナSSLファイルパス  ## /etc/nginx/ssl/protopie.crt;
        ssl_certificate_key     修正 => dockerコンテナSSLファイルパス  ## /etc/nginx/ssl/protopie.key;
        コンテナSSLファイルパス

         ssl_session_timeout  5m;
         ssl_protocols SSLv2 SSLv3 TLSv1;
                 .
                 .
                 .
    }
```

docker-compose.ymlファイルを以下のように修正します

```docker-compose.yml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - ローカルファイルパス : dockerコンテナファイルパス ## 例: ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro
      - ローカルファイルパス : dockerコンテナファイルパス ## 例: ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro
    ports:
      - 443:443    ## 修正 =>ローカルポート : dockerコンテナポート
    links:
      - web
      - api
```


config.ymlファイルを以下のように修正します

```config.yml
servers:
  http: https://your-domain         ## 例 : https://protopie.com
  update: https://autoupdate.protopie.io

```

## Windows用

これらのdockerイメージはLinuxベースです。Windowsを使用している場合は、`Docker for Windows`とhyper-vを使用してWindows上でLinuxコンテナを実行することをお勧めします。詳細については、以下のリンクを参照してください。

* https://docs.docker.com/docker-for-windows

## 注意事項

#### バージョンダウングレード

`api`の場合、ProtoPie Enterpriseはバージョンダウングレードでうまく動作しない可能性があります。各メジャーまたはマイナーバージョンの更新には、DBスキーマの変更が含まれる場合があり、`api`はブートストラップ時に毎回これをチェックし、バージョン更新にDBスキーマの変更が含まれている場合はDBをマイグレーションしようとします。したがって、バージョンダウングレードの場合、マイグレーションされたDBスキーマのために`api`がエラーを発生させる可能性があります。

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### バージョンの不一致

docker-composeサービス名からお気づきかもしれませんが、`web`はデータを取得するために`api`にリクエストを送り、ページに表示します。これらは密接に連携していますが、サービスとしては分離されています。そのため、`web`と`api`のバージョンがマイナーバージョン（パッチバージョンではない）で一致していることを確認してください。バージョンが一致しない場合、`web`からのリクエストはエラーメッセージを含むレスポンスを返します。

#### ディスクスペース不足とバックアップ

画像とデータベースデータを含むアップロードされたPiesは、最も多くのディスクスペースを使用します。利用可能なディスクスペースを確認し、バックアップを作成して予期せぬ問題を防ぐことが必要です。バックアップを作成する場合は、以下のdockerボリュームを確認して、コピーする必要があるものを確認してください。

* `api_upload`: Pieがアップロードされた場所です。
```bash
 docker cp protopie_api_1:/app/upload [[バックアップパス]]
```
 
* `pg_data`: データベースデータが保存されている場所です。
```bash
  docker exec protopie_db_1 pg_dump -c -U protopie_r protopie > [[バックアップパス]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pieファイルとデータベースの復元
* `api_upload`: アップロードされたデータの復元です。

```bash
 docker cp [[バックアップパス]] protopie_api_1:/app/

 例: docker cp ./upload protopie_api_1:/app/ 
```
 
* `pg_data`: データベースデータの復元です。

```bash
cat [[バックアップパス]]/protopie_db_xxx.sql |  docker exec -i app_db_1 psql -U protopie_w protopie
```

# アップデート
アップデートする前に、データの安全を確保するために、サーバーのスナップショットイメージを作成し、上記の方法でデータをバックアップして安全な場所に保管することをお勧めします。
## ProtoPieオンプレミスのアップデート方法（Windows）

1. Windowsエクスプローラーで`docker-compose.yml`ファイルが含まれるディレクトリに移動します（例：=> c:\local\lib\protopie）

2. docker-compose.ymlファイルを開きます

3. 次の部分を見つけて、修正し、保存します

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. ウィンドウキー + r（ショートカットキー）で「cmd」を入力し、実行ウィンドウを開きます

5. cd protopieファイルパスに移動します（例：=> cd c:\local\lib\protopie）

6. 実行中のProtoPieサービスを停止します：
```bash
docker-compose -p protopie stop
```

7. 停止したサービスコンテナを削除します：
```bash
docker-compose -p protopie rm
```

8. 分離モードで更新されたProtoPieサービスを開始します：
```bash
docker-compose -p protopie up -d
```

9. ブラウザ（IE、Chrome）から「protopie URL」にアクセスします

## ProtoPieオンプレミスのアップデート方法（Linux）

1. `docker-compose.yml`ファイルが含まれるディレクトリに移動します：（例：=> cd /home/victor/enterprise-onpremises）

2. テキストエディタを使用して`docker-compose.yml`ファイルを開きます：
```bash
sudo vi docker-compose.yml
```

3. 次の部分を見つけて、修正し、保存します

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. 実行中のProtoPieサービスを停止します：
```bash
docker-compose -p protopie stop
```

5. 停止したサービスコンテナを削除します：
```bash
docker-compose -p protopie rm
```

6. 分離モードで更新されたProtoPieサービスを開始します：
```bash
docker-compose -p protopie up -d
```

7. ブラウザ（IE、Chrome）から「protopie URL」にアクセスします


## トラブルシューティングガイド

このトラブルシューティングガイドを適用した後は、常にブラウザのキャッシュがクリアされている（無効になっている）ことを確認してください。

#### dockerログ（postgres:10.5-alphine dockerコンテナ）で「/bin/bash^M: bad interpreter: no such file or directory」エラーが発生した場合

WindowsまたはMacでSublime Textを使用してスクリプトを編集する場合：
表示 > 行末文字 > Unixをクリックし、ファイルを再保存します。

notepad++では、次の操作でファイル固有に設定できます：
編集 --> EOL変換 --> UNIX/OSX形式

誤ったCR文字を削除します。次のコマンドで行うことができます：
```bash
sed -i -e 's/\r$//' setup.sh
```

viを使用してスクリプトを編集する場合：
```bash
vi run.sh
:set fileformat=unix
```

#### ProtoPieサーバーの再起動（ProtoPieサーバーのインストールパスの移動）
```bash
docker-compose -p protopie restart
```

#### ProtoPieサーバーの停止（ProtoPieサーバーのインストールパスの移動）
```bash
docker-compose -p protopie stop
```

#### ProtoPieサーバーログ（ProtoPieサーバーのインストールパスの移動）
```bash
docker-compose -p protopie logs
```

#### HTTPのみの環境下での一般的な誤設定
`config.yml`の`tls` `ssl`が`false`であることを確認してください

#### サーバーにドメインがなくIPアドレスのみの場合
以下のように`nginx.conf`の45行目を更新します
```
        # FROM
        listen 80;

        location / {
            proxy_pass http://web_server;
        }
```
```
        # TO
        listen 80;

        location / {
            sub_filter_once off;
            sub_filter_types text/html;
            sub_filter "<meta http-equiv=\"Content-Security-Policy\" content=\"upgrade-insecure-requests\"/>" "";
            proxy_pass http://web_server;
        }
```
