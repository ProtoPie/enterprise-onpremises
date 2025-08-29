_[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)_

# ローカルサーバーに ProtoPie Enterprise をデプロイ

これは Docker Compose を使用してローカルサーバーに ProtoPie Enterprise をデプロイするための公式ガイドです。

ProtoPie Enterprise は ProtoPie エコシステムの一部であり、チームコラボレーションのためのクラウド環境を提供します。ProtoPie エコシステムのクラウド環境には次のものが含まれます：

1. **ProtoPie Cloud（パブリッククラウド環境）**：Free、Basic、および Pro プランのユーザー向け、アクセス URL は https://cloud.protopie.io
2. **ProtoPie Enterprise クラウド環境**：以下の 2 つのデプロイ方式があります：
   - **Private Cloud（プライベートクラウド環境）**：AWS 上に特定の顧客用に独立したスペースを提供、アクセス URL は https://your-organization.protopie.cloud
   - **On-Premises（ローカルサーバー）**：組織のローカルサーバーにデプロイ、アクセス URL はサーバーの IP（例： http://192.168.xxx.xxx ）またはサーバーのドメイン名（例： https://protopie.your.domain ）。このドキュメントではこのデプロイ方式について説明します。

ProtoPie エコシステムの詳細については、以下をご参照ください：

- [ProtoPie Ecosystem](https://www.protopie.io/learn/docs/introducing-protopie/protopie-ecosystem)
- [ProtoPie Cloud](https://www.protopie.io/learn/docs/cloud/getting-started)
- [ProtoPie Enterprise](https://www.protopie.io/learn/docs/enterprise/getting-started)

## デプロイの準備

ProtoPie Enterprise をサーバーにデプロイする前に、以下のハードウェア、オペレーティングシステム、およびソフトウェア要件を満たしていることを確認してください。次に、サーバーにアクセスするために計画している URL を提供してください。この URL は、ブラウザでクラウド環境にアクセスするためにも、ProtoPie Studio、ProtoPie Connect、または ProtoPie Player で「Log in with Secure Enterprise」機能を使用する際に入力するためにも使用されます。私たちは提供された URL に基づいて証明書 pem ファイルを生成します。

注意：通常、ProtoPie Enterprise On-Premise を専用の Linux サーバーにデプロイし、他の複数の PC に ProtoPie Studio および ProtoPie Connect をインストールしてサーバーに接続して使用することをお勧めします。特別な状況、例えばテストや一人での使用の場合には、同じ PC（Windows または MacOS）に ProtoPie Enterprise On-Premise をデプロイし、ProtoPie Studio および ProtoPie Connect をインストールすることもできます。

## ハードウェア要件

|          | 数量 | CPU(コア)        | メモリ |
| -------- | ---- | ---------------- | ------ |
| 最低要件 | 1    | 1 コア 64 ビット | 4GB    |
| 推奨構成 | 1    | 2 コア 64 ビット | 8GB    |

- ストレージ：保存するプロトタイプの量によって異なります。

## オペレーティングシステム要件

サーバーのオペレーティングシステムを新規にインストールできる場合は、最新の Debian LTS バージョン 12 をお勧めします。

### Linux

- Debian 9+
- Fedora 28+
- Ubuntu 18.04+

### Windows

- Windows 10 64 ビット：Professional、Enterprise、または Education エディション（1607 年記念アップデート、ビルド 14393 以上）

### macOS

- 10.12+

## ソフトウェア要件

- Docker 1.13.0+
- Docker Compose 1.10.0+

## 準備

### リポジトリのクローン

```bash
git clone https://github.com/ProtoPie/enterprise-onpremises.git
```

### ファイルの修正

ProtoPie Enterprise を実行する前に、以下のファイルを確認し、必要に応じて修正してください。

#### license.pem

生成された pem 証明書ファイルの名前を`license.pem`に変更し、`docker-compose.yml`ファイルがあるディレクトリに移動します。

#### config.yml

`config.yml`ファイルには ProtoPie Enterprise の基本設定が含まれています。例えば：

- `servers.http`：ProtoPie Enterprise が実行される URL（例： `http://192.168.xxx.xxx` または `https://protopie.your.domain`）。
- `mail.smtp`：メンバーを招待するためやパスワードを変更するために使用する SMTP 設定。このオプションを設定しない場合、メンバーを招待するときに招待リンクを手動でコピーして送信する必要があります。

#### db.env

`db.env`ファイルには、データベースの初期化に使用される設定が含まれています。`root user`と`protopie db`を含みます。このファイルは修正しなくてもよいです。

### HTTPS 暗号化の設定または未設定

セキュリティ上の理由から HTTPS の使用を強くお勧めしますが、HTTPS を使用しないことも選択できます。

#### HTTPS 暗号化を使用しない場合

HTTPS を使用しない場合、例えば IP アドレスを使用する場合は、以下の手順で nginx.conf ファイルを修正し、HTTPS を使用しない設定に変更します。

45 行目を以下のように変更します：

```nginx
listen 80;

location / {
    proxy_pass http://web_server;
}
```

#### HTTPS 暗号化を使用する場合

##### OpenSSL を使用して SSL 証明書（.crt）を生成

以下のコマンドを使用して SSL 証明書（.crt）を作成し、同時に秘密鍵（.key）と証明書署名要求（.csr）ファイルを作成します：

```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```

例：

```bash
openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

##### 関連ファイルの修正

SSL/TLS 証明書がある場合は、以下の設定を`nginx.conf`ファイルに正しく挿入します：

```nginx
server {
    listen 443;
    server_name localhost;
    ssl on;
    ssl_certificate /etc/nginx/ssl/protopie.crt; #dockerコンテナのファイルパス
    ssl_certificate_key /etc/nginx/ssl/protopie.key; #dockerコンテナのファイルパス

    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;

    location / {
        proxy_pass http://web_server;
    }
}
```

`docker-compose.yml`ファイルを以下のように修正します：

```yaml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro # ローカルファイルパス : dockerコンテナのファイルパス
      - ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro # ローカルファイルパス : dockerコンテナのファイルパス
    ports:
      - 443:443 # ローカルポート : dockerコンテナのポート
    links:
      - web
      - api
```

`config.yml`ファイルを修正し、https を使用するようにします：

```yaml
servers:
  http: https://protopie.your.domain
  update: https://autoupdate.protopie.io
```

## 起動と実行

上記のファイルを編集した後、`docker-compose.yml`の Docker コンテナを起動して ProtoPie Enterprise を実行します。以下のコマンドを実行して、Docker Compose を使用してコンテナをバックグラウンドで実行します：

```bash
docker-compose -p protopie up -d
```

Docker Hub から Docker イメージをプルするために、`docker login`で Docker ID にログインする必要がある場合があります。

その後、 `http://192.168.xxx.xxx` または `https://protopie.your.domain` でアクセスできます。

### Windows の場合

これらの Docker イメージは Linux ベースです。そのため、Windows を使用している場合は、`Docker for Windows`を使用して、Windows 上で Linux コンテナを実行することをお勧めします。詳細については、以下のリンクを参照してください。

- https://docs.docker.com/docker-for-windows

### MacOS の場合

MacOS を使用している場合、HomeBrew を使用して、以下のコマンドで Docker と Docker Compose をインストールすることをお勧めします。

```bash
brew install docker docker-compose colima
```

## よく使う管理コマンド

デプロイが成功した後、これらのコマンドを使用して Docker コンテナを管理および確認することができます。docker-compose コマンドは、docker-compose.yml が存在するディレクトリで実行する必要があります。

```bash
docker ps
```

現在実行中の Docker コンテナを一覧表示します。ProtoPie Enterprise は Docker Compose の 4 つのサービスで構成されています。これらのサービスはすべて Docker イメージです。

- `nginx` - ウェブサーバー
- `web` - ウェブアプリケーションインターフェース
- `api` - バックエンド API
- `db` - データベースサーバー

```bash
docker-compose -p protopie restart
```

compose プロジェクト`protopie`に定義されているすべてのサービスコンテナを再起動します。

```bash
docker-compose -p protopie stop
```

compose プロジェクト`protopie`に定義されているすべてのサービスコンテナを停止します。

```bash
docker-compose -p protopie down
```

compose プロジェクト`protopie`に定義されているすべてのサービス、ネットワーク、およびキャッシュボリュームを停止して削除します。コンテナが停止または削除されても、`db`データはホストファイルシステムにマウントされているため、持続します。

```bash
docker-compose -p protopie logs
```

compose プロジェクト`protopie`に定義されているすべてのサービスのログを表示します。

```bash
docker network ls
```

すべての Docker ネットワークを一覧表示します。

```bash
docker volume ls
```

すべての Docker ボリュームを一覧表示します。

```bash
docker volume rm protopie_api_logs protopie_api_upload protopie_api_download protopie_pg_data
```

すべての Docker ボリュームを削除します。！！！注意：このコマンドはすべてのデータを削除するため、データをバックアップし、必要な場合にのみ実行してください！！！

## 注意事項

#### ディスク容量不足とバックアップ

アップロードされた Pies とデータベースデータは、最も多くのディスク容量を使用します。ディスク容量を確認し、予期しない問題を防ぐためにバックアップを作成する必要があります。バックアップを作成する場合は、以下の Docker ボリュームを確認し、コピーする必要があります。

- `api_upload`：Pie がアップロードされる場所。

```bash
docker cp protopie_api_1:/app/upload [[バックアップパス]]
```

- `pg_data`：データベースデータが保存される場所。

```bash
docker exec protopie_db_1 pg_dump -c -U postgres protopie > [[バックアップパス]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pie ファイルとデータベースのリカバリ

- `api_upload`：アップロードされたデータのリカバリ。

```bash
docker cp [[バックアップパス]] protopie_api_1:/app/

例: docker cp ./upload protopie_api_1:/app/
```

- `pg_data`：データベースデータのリカバリ。

```bash
cat [[バックアップパス]]/protopie_db_xxx.sql |  docker exec -i protopie_db_1 psql -U postgres protopie
```

## アップグレードとダウングレード

データの安全性を確保するために、更新やダウングレード前にサーバーのスナップショットイメージを作成し、上記の方法でデータをバックアップし、安全な場所に保管することをお勧めします。

#### バージョンの更新

1. `docker-compose.yml`ファイルが含まれるディレクトリに移動します：（例：cd /home/victor/enterprise-onpremises）
   （Windows の場合、Windows エクスプローラーで`docker-compose.yml`ファイルが含まれるディレクトリに移動します（例：c:\local\lib\protopie））

2. テキストエディタで`docker-compose.yml`ファイルを開きます：

```bash
sudo vi docker-compose.yml
```

3. 以下の部分を探して修正し、保存します。

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-15.7.0

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-15.7.1

```

4. 実行中の ProtoPie サービスを停止します：

```bash
docker-compose -p protopie stop
```

（Windows の場合：Win + r のショートカットキーを使用し、"cmd"を入力して実行し、`protopie`フォルダのパスに移動します（例：cd c:\local\lib\protopie））

5. 停止したサービスコンテナを削除します：

```bash
docker-compose -p protopie rm
```

6. 更新された ProtoPie サービスをデタッチモードで起動します：

```bash
docker-compose -p protopie up -d
```

7. ブラウザから"protopie URL"にアクセスします（IE、Chrome）

#### バージョンのダウングレード

`api`の場合、ProtoPie Enterprise はバージョンダウングレードをうまくサポートできない可能性があります。これは、主なまたは副次的なバージョンアップデートごとにデータベーススキーマの変更が含まれている可能性があり、`api`は起動時にそれをチェックし、バージョン更新がデータベーススキーマの変更を含む場合、`api`はデータベースのマイグレーションを試みるためです。したがって、バージョンダウングレードの場合、マイグレーション後のデータベーススキーマにより、`api`はエラーを引き起こす可能性があります。

- enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
- enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### バージョンの不一致

Docker Compose サービス名からもわかるように、`web`はデータを取得してページに表示するために`api`にリクエストを送信します。これらのサービスは緊密に結合されていますが、サービスとしては隔離されています。したがって、`web`と`api`のバージョンがマッチするマイナーバージョン（パッチバージョンではない）を持っていることを確認してください。バージョンが一致しない場合、`web`のリクエストはエラーメッセージを含むレスポンスを返すでしょう。

## トラブルシューティングガイド

このトラブルシューティングガイドを適用した後は、常にブラウザキャッシュがクリアされていることを確認してください（無効にします）。

#### docker ログ（postgres:10.5-alphine docker コンテナ）に"/bin/bash^M: bad interpreter: no such file

or directory"エラーが表示される場合

この問題は通常、LF と CRLF エンコーディングの衝突によって引き起こされます。Windows 上で git を使用してリポジトリをクローンし、Windows 版 Docker を使用してデプロイする場合にこの問題が発生する可能性があります。この問題を解決するには、少なくとも以下の 3 つのファイルが LF エンコーディング形式であることを確認する必要があります：`db-init\01-init.sh`、`db-init\02-init-db.sh`、`db.env`。

Windows または Mac で Sublime Text を使用してスクリプトを編集する場合：
ビュー > 行の終了 > Unix をクリックし、ファイルを再保存します。

notepad++では、以下の手順を行います：
編集 --> EOL 変換 --> UNIX/OSX 形式

余分な CR 文字を削除します。次のコマンドを使用してこれを実行できます：

```bash
sed -i -e 's/\r$//' setup.sh
```

vi を使用してスクリプトを編集する場合：

```bash
vi run.sh
:set fileformat=unix
```

#### HTTP 環境のみでの一般的な構成エラー

`config.yml`の`tls`および`ssl`が`false`になっていることを確認してください。

#### サーバーの 80 ポートが他のアプリケーションによって使用されている場合

一部のお客様のサーバーでは、80 ポートが他のアプリケーションによって使用されていることがわかりました。したがって、ProtoPie ローカルサービスが使用するポートを変更することをお勧めします。`docker-compose.yml`ファイルを編集し、`services.nginx.ports`項目を`80:80`から`8080:80`に変更し、`config.yml`ファイルの`servers.http`項目を`http://192.168.xxx.xxx`から`http://192.168.xxx.xxx:8080`に更新します。これらの手順を完了した後、更新された URL とポート情報を提供してください。新しい証明書を提供します。その後、既存の証明書を置き換える必要があります。

80 ポートは HTTP のデフォルトポートであるため、通常、Web ブラウザには表示されません。しかし、サービスポートを 8080 に変更する場合は、新しいポートを URL に指定する必要があります。例えば、以前は`http://192.168.xxx.xxx`でサービスにアクセスしていた場合、`http://192.168.xxx.xxx:8080`に変更する必要があります。

#### インターネット接続のないサーバーに Docker イメージをデプロイする

デプロイ中、サーバーは Docker イメージを取得するためにインターネット接続が必要です。デプロイが完了した後、必要に応じて組織のセキュリティポリシーに従ってインターネット接続を切断することができます。もし、インターネットに接続できないサーバーにデプロイする必要がある場合、インターネット接続のあるコンピューターから以下の docker コマンドを使って Docker イメージを取得し、保存する必要があります。

```bash
docker pull nginx:1.21.1-alpine
docker pull protopie/enterprise-onpremises:web-15.7.0
docker pull protopie/enterprise-onpremises:api-15.7.1
docker pull postgres:10.5-alpine

docker save -o nginx_1.21.1-alpine.tar nginx:1.21.1-alpine
docker save -o web_latest.tar protopie/enterprise-onpremises:web-15.7.0
docker save -o api_latest.tar protopie/enterprise-onpremises:api-15.7.1
docker save -o postgres_10.5-alpine.tar postgres:10.5-alpine
```

**ヒント：** `15.5.2`は、必要な最新のバージョンに置き換えてください。

その後、安全な方法（USB や内部ネットワークなど）で保存したファイルをターゲットサーバーに転送し、ターゲットサーバーで以下のコマンドを実行して転送したイメージをロードします：

```bash
docker load -i nginx_1.21.1-alpine.tar
docker load -i web_latest.tar
docker load -i api_latest.tar
docker load -i postgres_10.5-alpine.tar
```
