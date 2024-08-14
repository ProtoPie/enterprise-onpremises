
*[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)*

# ローカルサーバーにProtoPie Enterpriseをデプロイ

これはDocker Composeを使用してローカルサーバーにProtoPie Enterpriseをデプロイするための公式ガイドです。

ProtoPie EnterpriseはProtoPieエコシステムの一部であり、チームコラボレーションのためのクラウド環境を提供します。ProtoPieエコシステムのクラウド環境には次のものが含まれます：

1. **ProtoPie Cloud（パブリッククラウド環境）**：Free、Basic、およびProプランのユーザー向け、アクセスURLは https://cloud.protopie.io
2. **ProtoPie Enterpriseクラウド環境**：以下の2つのデプロイ方式があります：
   - **Private Cloud（プライベートクラウド環境）**：AWS上に特定の顧客用に独立したスペースを提供、アクセスURLは https://your-organization.protopie.cloud
   - **On-Premises（ローカルサーバー）**：組織のローカルサーバーにデプロイ、アクセスURLはサーバーのIP（例： http://192.168.xxx.xxx ）またはサーバーのドメイン名（例： https://protopie.your.domain ）。このドキュメントではこのデプロイ方式について説明します。

ProtoPieエコシステムの詳細については、以下をご参照ください：
- [ProtoPie Ecosystem](https://www.protopie.io/learn/docs/introducing-protopie/protopie-ecosystem)
- [ProtoPie Cloud](https://www.protopie.io/learn/docs/cloud/getting-started)
- [ProtoPie Enterprise](https://www.protopie.io/learn/docs/enterprise/getting-started)

## デプロイの準備
ProtoPie Enterpriseをサーバーにデプロイする前に、以下のハードウェア、オペレーティングシステム、およびソフトウェア要件を満たしていることを確認してください。次に、サーバーにアクセスするために計画しているURLを提供してください。このURLは、ブラウザでクラウド環境にアクセスするためにも、ProtoPie Studio、ProtoPie Connect、またはProtoPie Playerで「Log in with Secure Enterprise」機能を使用する際に入力するためにも使用されます。

私たちは提供されたURLに基づいて証明書pemファイルを生成します。デプロイの過程で、サーバーはDockerイメージを取得するためにインターネットにアクセスする必要があります。デプロイが完了した後、必要に応じて組織のセキュリティポリシーに従ってインターネット接続を切断することができます。

注意：通常、ProtoPie Enterprise On-Premiseを専用のLinuxサーバーにデプロイし、他の複数のPCにProtoPie StudioおよびProtoPie Connectをインストールしてサーバーに接続して使用することをお勧めします。特別な状況、例えばテストや一人での使用の場合には、同じPC（WindowsまたはMacOS）にProtoPie Enterprise On-Premiseをデプロイし、ProtoPie StudioおよびProtoPie Connectをインストールすることもできます。

## ハードウェア要件
|              	| 数量 	| CPU(コア) 	| メモリ 	|
|--------------	|-----	|-----------	|--------	|
| 最低要件     	| 1   	| 1コア 64ビット	| 4GB    	|
| 推奨構成 	| 1   	| 2コア 64ビット	| 8GB    	|
* ストレージ：保存するプロトタイプの量によって異なります。

## オペレーティングシステム要件
サーバーのオペレーティングシステムを新規にインストールできる場合は、最新のDebian LTSバージョン12をお勧めします。
### Linux
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### Windows
* Windows 10 64ビット：Professional、Enterprise、またはEducationエディション（1607年記念アップデート、ビルド14393以上）
### macOS
* 10.12+

## ソフトウェア要件
* Docker 1.13.0+
* Docker Compose 1.10.0+

## 準備

### リポジトリのクローン

```bash
git clone https://github.com/ProtoPie/enterprise-onpremises.git
```

### ファイルの修正

ProtoPie Enterpriseを実行する前に、以下のファイルを確認し、必要に応じて修正してください。

#### license.pem

生成されたpem証明書ファイルの名前を`license.pem`に変更し、`docker-compose.yml`ファイルがあるディレクトリに移動します。

#### config.yml

`config.yml`ファイルにはProtoPie Enterpriseの基本設定が含まれています。例えば：

- `servers.http`：ProtoPie Enterpriseが実行されるURL（例： `http://192.168.xxx.xxx` または `https://protopie.your.domain`）。
- `mail.smtp`：メンバーを招待するためやパスワードを変更するために使用するSMTP設定。このオプションを設定しない場合、メンバーを招待するときに招待リンクを手動でコピーして送信する必要があります。

#### db.env

`db.env`ファイルには、データベースの初期化に使用される設定が含まれています。`root user`と`protopie db`を含みます。このファイルは修正しなくてもよいです。

### HTTPS暗号化の設定または未設定

セキュリティ上の理由からHTTPSの使用を強くお勧めしますが、HTTPSを使用しないことも選択できます。

#### HTTPS暗号化を使用しない場合

HTTPSを使用しない場合、例えばIPアドレスを使用する場合は、以下の手順でnginx.confファイルを修正し、HTTPSを使用しない設定に変更します。

45行目を以下のように変更します：

```nginx
listen 80;

location / {
    proxy_pass http://web_server;
}
```

#### HTTPS暗号化を使用する場合

##### OpenSSLを使用してSSL証明書（.crt）を生成

以下のコマンドを使用してSSL証明書（.crt）を作成し、同時に秘密鍵（.key）と証明書署名要求（.csr）ファイルを作成します：

```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```

例：

```bash
openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

##### 関連ファイルの修正

SSL/TLS証明書がある場合は、以下の設定を`nginx.conf`ファイルに正しく挿入します：

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
      - ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro  # ローカルファイルパス : dockerコンテナのファイルパス
      - ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro  # ローカルファイルパス : dockerコンテナのファイルパス
    ports:
      - 443:443  # ローカルポート : dockerコンテナのポート
    links:
      - web
      - api
```

`config.yml`ファイルを修正し、httpsを使用するようにします：

```yaml
servers:
  http: https://protopie.your.domain  
  update: https://autoupdate.protopie.io
```

## 起動と実行

上記のファイルを編集した後、`docker-compose.yml`のDockerコンテナを起動してProtoPie Enterpriseを実行します。以下のコマンドを実行して、Docker Composeを使用してコンテナをバックグラウンドで実行します：

```bash
docker-compose -p protopie up -d
```

Docker HubからDockerイメージをプルするために、`docker login`でDocker IDにログインする必要がある場合があります。

その後、 `http://192.168.xxx.xxx` または `https://protopie.your.domain` でアクセスできます。

### Windowsの場合

これらのDockerイメージはLinuxベースです。そのため、Windowsを使用している場合は、`Docker for Windows`を使用して、Windows上でLinuxコンテナを実行することをお勧めします。詳細については、以下のリンクを参照してください。

* https://docs.docker.com/docker-for-windows

### MacOSの場合

MacOSを使用している場合、HomeBrewを使用して、以下のコマンドでDockerとDocker Composeをインストールすることをお勧めします。

```bash
brew install docker docker-compose colima
```

## よく使う管理コマンド
デプロイが成功した後、これらのコマンドを使用してDockerコンテナを管理および確認することができます。docker-composeコマンドは、docker-compose.ymlが存在するディレクトリで実行する必要があります。

```bash
docker ps
```
現在実行中のDockerコンテナを一覧表示します。ProtoPie EnterpriseはDocker Composeの4つのサービスで構成されています。これらのサービスはすべてDockerイメージです。

* `nginx` - ウェブサーバー
* `web` - ウェブアプリケーションインターフェース
* `api` - バックエンドAPI
* `db` - データベースサーバー

```bash
docker-compose -p protopie restart
```
composeプロジェクト`protopie`に定義されているすべてのサービスコンテナを再起動します。

```bash
docker-compose -p protopie stop
```
composeプロジェクト`protopie`に定義されているすべてのサービスコンテナを停止します。

```bash
docker-compose -p protopie down
```
composeプロジェクト`protopie`に定義されているすべてのサービス、ネットワーク、およびキャッシュボリュームを停止して削除します。コンテナが停止または削除されても、`db`データはホストファイルシステムにマウントされているため、持続します。

```bash
docker-compose -p protopie logs
```
composeプロジェクト`protopie`に定義されているすべてのサービスのログを表示します。

```bash
docker network ls
```
すべてのDockerネットワークを一覧表示します。

```bash
docker volume ls
```
すべてのDockerボリュームを一覧表示します。

```bash
docker volume rm protopie_api_logs protopie_api_upload protopie_api_download protopie_pg_data
```
すべてのDockerボリュームを削除します。！！！注意：このコマンドはすべてのデータを削除するため、データをバックアップし、必要な場合にのみ実行してください！！！

## 注意事項

#### ディスク容量不足とバックアップ

アップロードされたPiesとデータベースデータは、最も多くのディスク容量を使用します。ディスク容量を確認し、予期しない問題を防ぐためにバックアップを作成する必要があります。バックアップを作成する場合は、以下のDockerボリュームを確認し、コピーする必要があります。

* `api_upload`：Pieがアップロードされる場所。
```bash
docker cp protopie_api_1:/app/upload [[バックアップパス]]
```
 
* `pg_data`：データベースデータが保存される場所。
```bash
docker exec protopie_db_1 pg_dump -c -U postgres protopie > [[バックアップパス]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pieファイルとデータベースのリカバリ
* `api_upload`：アップロードされたデータのリカバリ。

```bash
docker cp [[バックアップパス]] protopie_api_1:/app/

例: docker cp ./upload protopie_api_1:/app/ 
```
 
* `pg_data`：データベースデータのリカバリ。

```bash
cat [[バックアップパス]]/protopie_db_xxx.sql |  docker exec -i protopie_db_1 psql -U postgres protopie
```
## アップグレードとダウングレード
データの安全性を確保するために、更新やダウングレード前にサーバーのスナップショットイメージを作成し、上記の方法でデータをバックアップし、安全な場所に保管することをお勧めします。

#### バージョンの更新

1. `docker-compose.yml`ファイルが含まれるディレクトリに移動します：（例：cd /home/victor/enterprise-onpremises）
（Windowsの場合、Windowsエクスプローラーで`docker-compose.yml`ファイルが含まれるディレクトリに移動します（例：c:\local\lib\protopie））

2. テキストエディタで`docker-compose.yml`ファイルを開きます：
```bash
sudo vi docker-compose.yml
```

3. 以下の部分を探して修正し、保存します。

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-13.1.0

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-13.1.0

```

4. 実行中のProtoPieサービスを停止します：
```bash
docker-compose -p protopie stop
```
（Windowsの場合：Win + rのショートカットキーを使用し、"cmd"を入力して実行し、`protopie`フォルダのパスに移動します（例：cd c:\local\lib\protopie））

5. 停止したサービスコンテナを削除します：
```bash
docker-compose -p protopie rm
```

6. 更新されたProtoPieサービスをデタッチモードで起動します：
```bash
docker-compose -p protopie up -d
```

7. ブラウザから"protopie URL"にアクセスします（IE、Chrome）

#### バージョンのダウングレード

`api`の場合、ProtoPie Enterpriseはバージョンダウングレードをうまくサポートできない可能性があります。これは、主なまたは副次的なバージョンアップデートごとにデータベーススキーマの変更が含まれている可能性があり、`api`は起動時にそれをチェックし、バージョン更新がデータベーススキーマの変更を含む場合、`api`はデータベースのマイグレーションを試みるためです。したがって、バージョンダウングレードの場合、マイグレーション後のデータベーススキーマにより、`api`はエラーを引き起こす可能性があります。

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### バージョンの不一致

Docker Composeサービス名からもわかるように、`web`はデータを取得してページに表示するために`api`にリクエストを送信します。これらのサービスは緊密に結合されていますが、サービスとしては隔離されています。したがって、`web`と`api`のバージョンがマッチするマイナーバージョン（パッチバージョンではない）を持っていることを確認してください。バージョンが一致しない場合、`web`のリクエストはエラーメッセージを含むレスポンスを返すでしょう。

## トラブルシューティングガイド

このトラブルシューティングガイドを適用した後は、常にブラウザキャッシュがクリアされていることを確認してください（無効にします）。

#### dockerログ（postgres:10.5-alphine dockerコンテナ）に"/bin/bash^M: bad interpreter: no such file

 or directory"エラーが表示される場合

この問題は通常、LFとCRLFエンコーディングの衝突によって引き起こされます。Windows上でgitを使用してリポジトリをクローンし、Windows版Dockerを使用してデプロイする場合にこの問題が発生する可能性があります。この問題を解決するには、少なくとも以下の3つのファイルがLFエンコーディング形式であることを確認する必要があります：`db-init\01-init.sh`、`db-init\02-init-db.sh`、`db.env`。

WindowsまたはMacでSublime Textを使用してスクリプトを編集する場合：
ビュー > 行の終了 > Unixをクリックし、ファイルを再保存します。

notepad++では、以下の手順を行います：
編集 --> EOL変換 --> UNIX/OSX形式

余分なCR文字を削除します。次のコマンドを使用してこれを実行できます：
```bash
sed -i -e 's/\r$//' setup.sh
```

viを使用してスクリプトを編集する場合：
```bash
vi run.sh
:set fileformat=unix
```

#### HTTP環境のみでの一般的な構成エラー
`config.yml`の`tls`および`ssl`が`false`になっていることを確認してください。

#### サーバーの80ポートが他のアプリケーションによって使用されている場合
一部のお客様のサーバーでは、80ポートが他のアプリケーションによって使用されていることがわかりました。したがって、ProtoPieローカルサービスが使用するポートを変更することをお勧めします。`docker-compose.yml`ファイルを編集し、`services.nginx.ports`項目を`80:80`から`8080:80`に変更し、`config.yml`ファイルの`servers.http`項目を`http://192.168.xxx.xxx`から`http://192.168.xxx.xxx:8080`に更新します。これらの手順を完了した後、更新されたURLとポート情報を提供してください。新しい証明書を提供します。その後、既存の証明書を置き換える必要があります。

80ポートはHTTPのデフォルトポートであるため、通常、Webブラウザには表示されません。しかし、サービスポートを8080に変更する場合は、新しいポートをURLに指定する必要があります。例えば、以前は`http://192.168.xxx.xxx`でサービスにアクセスしていた場合、`http://192.168.xxx.xxx:8080`に変更する必要があります。
