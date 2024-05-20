*[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)*

# ProtoPie Enterprise 온프레미스 서버용

이 문서는 온프레미스 서버에서 Docker Compose를 사용하여 ProtoPie Enterprise를 배포하기 위한 공식 가이드입니다.

시작하려면 이 저장소를 복제하고, 아래에 자세히 설명된 필요한 구성을 만든 다음, 온프레미스 서버를 쉽게 배포하세요.

## 소프트웨어 요구사항
 * Docker 1.13.0+
 * Docker Compose 1.10.0+
 
## 하드웨어 요구사항
|             	| 수량 	| CPU(코어) 	| 메모리 	|
|-------------	|-----	|-----------	|--------	|
| 최소     	| 1   	| 1 코어 64비트	| 4GB    	|
| 권장 	| 1   	| 2 코어 64비트 | 8GB    	|
* 저장공간: 저장할 프로토타입의 양에 따라 다릅니다.

## OS 요구사항
### 리눅스
* CentOS 7+
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### 윈도우
* Windows 10 64비트: 프로, 엔터프라이즈 또는 교육용 (1607 기념일 업데이트, 빌드 14393 이상)
### macOS
* 10.12+

## Docker Compose의 서비스

ProtoPie Enterprise는 Docker Compose에서 도커 이미지로 구성된 네 가지 서비스로 구성됩니다.

* `nginx` - 웹 서버
* `web` - 웹 애플리케이션 인터페이스
* `api` - 백엔드 API
* `db` - 데이터베이스 서버

도커 허브에서 이러한 도커 이미지를 가져오려면 `docker login`을 통해 도커 ID로 로그인하세요.

## 사전 요구사항

ProtoPie Enterprise를 실행하기 전에 다음 파일을 열고, 아래 단계를 따라 이 파일들을 적절히 편집하세요.

#### license.pem

`license.pem` 파일을 `docker-compose.yml`과 같은 디렉토리로 이동하세요.

#### config.yml

`config.yml` 파일은 ProtoPie Enterprise의 기본 구성을 보유하고 있습니다. 예를 들어,
* `servers.http`: ProtoPie Enterprise가 실행되는 URL입니다. (예: http://your.domain)
* `mail.smtp`: 이메일을 보내는 SMTP 구성입니다. (예: 회원 초대 또는 비밀번호 변경)

#### db.env

`xxx.env` 파일은 애플리케이션에서 환경 변수를 나타냅니다. `db.env`는 사용자 및 데이터베이스를 생성하기 위한 초기 DB에 대한 `root user` 및 `protopie db`의 두 부분 구성을 가지고 있습니다.

## 실행 및 작동

앞서 언급한 파일을 편집하면 `docker-compose.yml`의 도커 컨테이너를 실행하고 ProtoPie Enterprise를 실행할 준비가 됩니다. docker-compose를 통해 백그라운드에서 컨테이너를 실행하려면 아래 명령을 실행하세요.

```bash
$ docker-compose -p protopie up -d
```

그런 다음 `http://your.domain`에서 접근할 수 있습니다. 다른 포트를 사용하려면 `docker-compose.yml`의 `services.nginx.port`와 `config.yml`의 `servers.http`를 수정하세요.

컨테이너가 중지되거나 제거되더라도 `db` 데이터는 `db`가 호스트 파일 시스템에 바인드 마운트되기 때문에 지속됩니다.


## SSL/TLS 인증서를 사용한 HTTPS
### Openssl로 SSL 인증서(.crt) 생성하기.
OpenSSL을 사용하여 SSL 인증서(.crt)를 생성할 때는 개인 키(.key)와 인증서 서명 요청(.csr) 파일이 모두 필요합니다.
아래 명령을 사용하세요.
```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```
```bash
예 =>  openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

보안 및 안전상의 이유로 HTTPS 사용을 강력히 권장합니다. SSL/TLS 인증서가 있으면 이 구성을 `nginx.conf` 파일에 적절히 삽입하세요.

```nginx conf
          .
          .
          .
     server {
        listen       443;
        server_name  localhost;
        ssl     on;
        ssl_certificate         수정 => 도커 컨테이너 SSL 파일 경로  ## /etc/nginx/ssl/protopie.crt;
        ssl_certificate_key     수정 => 도커 컨테이너 SSL 파일 경로  ## /etc/nginx/ssl/protopie.key;
        컨테이너 SSL 파일 경로

         ssl_session_timeout  5m;
         ssl_protocols SSLv2 SSLv3 TLSv1;
                 .
                 .
                 .
    }
```

docker-compose.yml 파일을 다음과 같이 수정하세요

```docker-compose.yml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - 로컬 파일 경로 : 도커 컨테이너 파일 경로 ## 예: ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro
      - 로컬 파일 경로 : 도커 컨테이너 파일 경로 ## 예: ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro
    ports:
      - 443:443    ## 수정 =>로컬 포트 : 도커 컨테이너 포트
    links:
      - web
      - api
```


config.yml 파일을 다음과 같이 수정하세요

```config.yml
servers:
  http: https://your-domain         ## 예 : https://protopie.com
  update: https://autoupdate.protopie.io

```

## 윈도우용

이 도커 이미지는 리눅스 기반입니다. 윈도우에서는 `Docker for Windows`와 하이퍼-V를 사용하여 윈도우에서 리눅스 컨테이너를 실행하는 것이 좋습니다. 자세한 내용은 아래 링크를 참조하세요.

* https://docs.docker.com/docker-for-windows

## 주의사항

#### 버전 다운그레이드

`api`의 경우, ProtoPie Enterprise는 버전 다운그레이드와 잘 작동하지 않을 수 있습니다. 각 주요 또는 부 버전 업데이트에는 DB 스키마 변경이 포함될 수 있으며, `api`는 부팅할 때마다 이를 확인하고 버전 업데이트에 DB 스키마 변경이 포함된 경우 DB를 마이그레이션하려고 시도합니다. 따라서 버전 다운그레이드의 경우, 마이그레이션된 DB 스키마로 인해 `api`에서 오류가 발생할 수 있습니다.

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### 버전 불일치

docker-compose 서비스 이름에서 알 수 있듯이, `web`은 데이터를 얻기 위해 `api`로 요청을 보내고 페이지에 표시합니다. 이러한 서비스는 긴밀하게 연결되어 있지만 서비스로서 분리되어 있습니다. 따라서 `web`과 `api` 버전이 부 버전(패치 버전이 아님)에서 일치하는지 확인하세요. 버전이 일치하지 않으면 `web`에서의 요청이 오류 메시지와 함께 응답을 반환합니다.

#### 디스크 공간 부족 및 백업

이미지와 데이터베이스 데이터가 포함된 업로드된 Pies는 가장 많은 디스크 공간을 사용합니다. 예상치 못한 문제를 방지하기 위해 사용 가능한 디스크 공간을 확인하고 백업을 생성하는 것이 필요합니다. 백업을 생성하려면 아래 도커 볼륨을 확인하여 복사해야 할 내용을 확인하세요.

* `api_upload`: Pie가 업로드된 위치입니다.
```bash
 docker cp protopie_api_1:/app/upload [[백업_경로]]
```
 
* `pg_data`: 데이터베이스 데이터가 저장된 위치입니다.
```bash
  docker exec protopie_db_1 pg_dump -c -U protopie_r protopie > [[백업_경로]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pie 파일 및 데이터베이스 복원
* `api_upload`: 업로드된 데이터 복원입니다.

```bash
 docker cp [[백업_경로]] protopie_api_1:/app/

 예: docker cp ./upload protopie_api_1:/app/ 
```
 
* `pg_data`: 데이터베이스 데이터 복원입니다.

```bash
cat [[백업_경로]]/protopie_db_xxx.sql |  docker exec -i app_db_1 psql -U protopie_w protopie
```

# 업데이트
업데이트하기 전에, 데이터 안전을 보장하기 위해 서버의 스냅샷 이미지를 생성하고 위의 방법을 사용하여 데이터를 백업하고 안전한 위치에 저장하는 것이 권장됩니다.
## ProtoPie 온프레미스 업데이트 방법 (윈도우)

1. 윈도우 탐색기에서 `docker-compose.yml` 파일이 포함된 디렉토리로 이동하세요 (예:=> c:\local\lib\protopie)

2. docker-compose.yml 파일을 엽니다

3. 다음 부분을 찾아 수정하고 저장하세요

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. 윈도우 키 + r(단축키)에서 "cmd"를 입력하여 실행 창을 엽니다

5. cd protopie 파일 경로로 이동합니다 (예:=> cd c:\local\lib\protopie )

6. 실행 중인 ProtoPie 서비스를 중지합니다:
```bash
docker-compose -p protopie stop
```

7. 중지된 서비스 컨테이너를 제거합니다:
```bash
docker-compose -p protopie rm
```

8. 분리 모드에서 업데이트된 ProtoPie 서비스를 시작합니다:
```bash
docker-compose -p protopie up -d
```

9. 브라우저(IE, Chrome)에서 "protopie URL"에 접속합니다

## ProtoPie 온프레미스 업데이트 방법 (리눅스)

1. `docker-compose.yml` 파일이 포함된 디렉토리로 이동합니다: (예:=> cd /home/victor/enterprise-onpremises)

2. 텍스트 편집기를 사용하여 `docker-compose.yml` 파일을 엽니다:
```bash
sudo vi docker-compose.yml
```

3. 다음 부분을 찾아 수정하고 저장하세요

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. 실행 중인 ProtoPie 서비스를 중지합니다:
```bash
docker-compose -p protopie stop
```

5. 중지된 서비스 컨테이너를 제거합니다:
```bash
docker-compose -p protopie rm
```

6. 분리 모드에서 업데이트된 ProtoPie 서비스를 시작합니다:
```bash
docker-compose -p protopie up -d
```

7. 브라우저(IE, Chrome)에서 "protopie URL"에 접속합니다


## 문제 해결 가이드

이 문제 해결 가이드를 적용한 후에는 항상 브라우저 캐시가 지워졌는지(비활성화됐는지) 확인하세요.

#### docker 로그(postgres:10.5-alphine 도커 컨테이너) "/bin/bash^M: bad interpreter: no such file or directory" 오류가 발생했을 때

Windows 또는 Mac에서 Sublime Text를 사용하여 스크립트를 편집하는 경우:
보기 > 줄 끝 > Unix를 클릭하고 파일을 다시 저장하세요.

notepad++에서는 다음을 눌러 파일별로 설정할 수 있습니다:
편집 --> EOL 변환 --> UNIX/OSX 포맷

잘못된 CR 문자를 제거하세요. 다음 명령으로 수행할 수 있습니다:
```bash
sed -i -e 's/\r$//' setup.sh
```

vi를 사용하여 스크립트를 편집하는 경우:
```bash
vi run.sh
:set fileformat=unix
```

#### ProtoPie 서버 재시작 (ProtoPie 서버 설치 경로 이동)
```bash
docker-compose -p protopie restart
```

#### ProtoPie 서버 중지 (ProtoPie 서버 설치 경로 이동)
```bash
docker-compose -p protopie stop
```

#### ProtoPie 서버 로그 (ProtoPie 서버 설치 경로 이동)
```bash
docker-compose -p protopie logs
```

#### HTTP 전용 환경에서의 일반적인 잘못된 구성
`config.yml`에서 `tls` `ssl`이 `false`인지 확인하세요

#### 서버에 도메인이 없고 IP 주소만 있는 경우
아래와 같이 `nginx.conf`의 45번 줄을 업데이트하세요
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
