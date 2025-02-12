_[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국어](README.ko.md)_

# 로컬 서버에서 ProtoPie Enterprise 배포

이것은 Docker Compose를 사용하여 로컬 서버에서 ProtoPie Enterprise를 배포하는 공식 가이드입니다.

ProtoPie Enterprise는 팀 협업을 용이하게 하기 위해 ProtoPie 생태계의 일부입니다. ProtoPie 생태계의 클라우드 환경에는 다음이 포함됩니다:

1. **ProtoPie Cloud (공용 클라우드 환경)**: Free, Basic 및 Pro 플랜 사용자를 위한 클라우드 환경으로, URL은 https://cloud.protopie.io 입니다.
2. **ProtoPie Enterprise 클라우드 환경**: 두 가지 배포 방법으로 나뉩니다:
   - **Private Cloud (사설 클라우드 환경)**: AWS에서 특정 고객을 위해 독립적으로 할당된 공간으로, URL은 https://your-organization.protopie.cloud 입니다.
   - **On-Premises (로컬 서버)**: 조직의 로컬 서버에 배포되며, 서버의 IP(예: http://192.168.xxx.xxx) 또는 서버의 도메인(예: https://protopie.your.domain)으로 액세스할 수 있습니다. 이 문서에서는 이 배포 방법에 대해 설명합니다.

ProtoPie 생태계에 대해 더 알고 싶으시면 다음 링크를 참조하세요:

- [ProtoPie Ecosystem](https://www.protopie.io/learn/docs/introducing-protopie/protopie-ecosystem)
- [ProtoPie Cloud](https://www.protopie.io/learn/docs/cloud/getting-started)
- [ProtoPie Enterprise](https://www.protopie.io/learn/docs/enterprise/getting-started)

## 배포 준비

로컬 서버에 ProtoPie Enterprise를 배포하기 전에 다음 하드웨어, 운영 체제 및 소프트웨어 요구 사항을 충족해야 합니다. 다음으로 서버에 액세스하는 데 사용할 URL을 제공해 주세요. 이 URL은 브라우저에서 클라우드 환경에 액세스하는 데 사용되며, ProtoPie Studio, ProtoPie Connect 또는 ProtoPie Player의 "Log in with Secure Enterprise" 기능을 통해 입력됩니다. 이 URL을 바탕으로 인증서 pem 파일을 생성합니다.

참고: 일반적으로 ProtoPie Enterprise On-Premise를 전용 Linux 서버에 배포하고, 여러 대의 PC에 ProtoPie Studio와 ProtoPie Connect를 설치한 후 서버에 연결하여 사용하는 것을 권장합니다. 특별한 경우, 예를 들어 테스트 목적으로 사용하거나 혼자 사용할 때는 같은 PC(Windows 또는 MacOS)에 ProtoPie Enterprise On-Premise를 배포하고 ProtoPie Studio와 ProtoPie Connect를 설치할 수 있습니다.

## 하드웨어 요구 사항

|                | 수량 | CPU(코어)    | 메모리 |
| -------------- | ---- | ------------ | ------ |
| 최소 요구 사항 | 1    | 1코어 64비트 | 4GB    |
| 권장 구성      | 1    | 2코어 64비트 | 8GB    |

- 저장 공간: 저장할 프로토타입의 양에 따라 다름.

## 운영 체제 요구 사항

서버 운영 체제를 새로 설치할 수 있다면, 최신 버전의 Debian LTS 12를 권장합니다.

### Linux

- Debian 9+
- Fedora 28+
- Ubuntu 18.04+

### Windows

- Windows 10 64비트: 프로페셔널, 엔터프라이즈 또는 교육용(1607 주년 업데이트, 빌드 14393 이상)

### macOS

- 10.12+

## 소프트웨어 요구 사항

- Docker 1.13.0+
- Docker Compose 1.10.0+

## 준비 작업

### 저장소 복제

```bash
git clone https://github.com/ProtoPie/enterprise-onpremises.git
```

### 파일 수정

ProtoPie Enterprise를 실행하기 전에 다음 파일을 확인하고 수정하세요.

#### license.pem

생성된 pem 인증서 파일을 `license.pem`으로 이름을 변경하고 `docker-compose.yml` 파일이 있는 디렉터리로 이동합니다.

#### config.yml

`config.yml` 파일에는 ProtoPie Enterprise의 기본 설정이 포함되어 있습니다. 예를 들어:

- `servers.http`: ProtoPie Enterprise가 실행되는 URL (예: `http://192.168.xxx.xxx` 또는 `https://protopie.your.domain`).
- `mail.smtp`: 이메일을 보내기 위한 SMTP 설정 (예: 멤버 초대 또는 비밀번호 변경). 이 옵션을 설정하지 않으면 멤버를 초대할 때 초대 링크를 복사하여 수동으로 보낼 필요가 있습니다.

#### db.env

`db.env` 파일은 데이터베이스 초기화에 필요한 설정을 포함하고 있으며, `root user`와 `protopie db`를 포함합니다. 이 파일은 수정할 필요가 없습니다.

### HTTPS 암호화 설정 또는 미설정

보안상의 이유로 HTTPS를 사용하는 것을 강력히 권장하지만, HTTPS를 사용하지 않도록 선택할 수도 있습니다.

#### HTTPS 암호화를 사용하지 않는 경우

HTTPS를 사용하지 않는 경우, 예를 들어 IP 주소를 사용하는 경우, nginx.conf 파일을 수정하여 HTTPS를 사용하지 않도록 설정할 수 있습니다.

45번째 줄을 다음과 같이 수정합니다:

```nginx
listen 80;

location / {
    proxy_pass http://web_server;
}
```

수정 후:

```nginx
listen 80;

location / {
    sub_filter_once off;
    sub_filter_types text/html;
    sub_filter "<meta http-equiv=\"Content-Security-Policy\" content=\"upgrade-insecure-requests\"/>" "";
    proxy_pass http://web_server;
}
```

#### HTTPS 암호화를 사용하는 경우

##### OpenSSL을 사용하여 SSL 인증서 생성 (.crt)

SSL 인증서(.crt)를 생성하려면 다음 명령어를 사용합니다. 개인 키(.key)와 인증서 서명 요청(.csr) 파일도 함께 생성합니다:

```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```

예:

```bash
openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

##### 관련 파일 수정

SSL/TLS 인증서가 있는 경우, 다음 설정을 `nginx.conf` 파일에 올바르게 삽입합니다:

```nginx
server {
    listen 443;
    server_name localhost;
    ssl on;
    ssl_certificate /etc/nginx/ssl/protopie.crt; #docker 컨테이너 파일 경로
    ssl_certificate_key /etc/nginx/ssl/protopie.key; #docker 컨테이너 파일 경로

    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;

    location / {
        proxy_pass http://web_server;
    }
}
```

`docker-compose.yml` 파일을 다음과 같이 수정합니다:

```yaml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro # 로컬 파일 경로 : docker 컨테이너 파일 경로
      - ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro # 로컬 파일 경로 : docker 컨테이너 파일 경로
    ports:
      - 443:443 # 로컬 포트 : docker 컨테이너 포트
    links:
      - web
      - api
```

`config.yml` 파일을 수정하여 https를 사용하도록 합니다:

```yaml
servers:
  http: https://protopie.your.domain
  update: https://autoupdate.protopie.io
```

## 시작 및 실행

위의 파일을 편집한 후, `docker-compose.yml`에 정의된 Docker 컨테이너를 시작하고 ProtoPie Enterprise를 실행합니다. Docker Compose를 사용하여 백그라운드에서 컨테이너를 실행하려면 다음 명령어를 실행합니다:

```bash
docker-compose -p protopie up -d
```

docker hub에서 이러한 docker 이미지를 가져오려면 `docker login`을 통해 Docker ID로 로그인해야 할 수도 있습니다.

그런 다음, `http://192.168.xxx.xxx` 또는 `https://protopie.your.domain`에서 액세스할 수 있습니다.

### Windows의 경우

이 Docker 이미지는 linux 기반입니다. 따라서 Windows를 사용하는 경우, `Docker for Windows`를 사용하여 Windows에서 linux 컨테이너를 실행하는 것을 권장합니다. 자세한 내용은 아래 링크를 참조하세요.

- https://docs.docker.com/docker-for-windows

### macOS의 경우

macOS를 사용하는 경우, HomeBrew를 사용하고 다음 명령어를 통해 docker 및 docker-compose를 설치하는 것이 좋습니다:

```bash
brew install docker docker-compose colima
```

## 자주 사용하는 관리 명령어

배포가 완료되면 Docker 컨테이너를 관리하고 확인하는 데 필요한 다음 명령어들을 사용할 수 있습니다. `docker-compose` 명령어는 `docker-compose.yml` 파일이 있는 폴더에서 실행해야 합니다.

```bash
docker ps
```

현재 실행 중인 Docker 컨테이너 목록을 나열합니다. ProtoPie Enterprise는 Docker Compose의 네 가지 서비스로 구성된 Docker 이미지로 구성됩니다.

- `nginx` - 웹 서버
- `web` - 웹 애플리케이션 인터페이스
- `api` - 백엔드 API
- `db` - 데이터베이스 서버

```bash
docker-compose -p protopie restart
```

`protopie` 프로젝트에 정의된 모든 서비스 컨테이너를 재시작합니다.

```bash
docker-compose -p protopie stop
```

`protopie` 프로젝트에 정의된 모든 서비스 컨테이너를 중지합니다.

```bash
docker-compose -p protopie down
```

`protopie` 프로젝트에 정의된 모든 서비스, 네트워크 및 캐시 볼륨을 중지하고 제거합니다.
참고: 컨테이너가 중지되거나 제거되더라도 `db` 데이터는 유지됩니다. 왜냐하면 `db`는 호스트 파일 시스템에 마운트되었기 때문입니다.

```bash
docker-compose -p protopie logs
```

`protopie` 프로젝트에 정의된 모든 서비스의 로그를 표시합니다.

```bash
docker network ls
```

모든 Docker 네트워크를 나열합니다.

```bash
docker volume ls
```

모든 Docker 볼륨을 나열합니다.

```bash
docker volume rm protopie_api_logs protopie_api_upload protopie_api_download protopie_pg_data
```

모든 Docker 볼륨을 삭제합니다. !!!위험 주의: 이 명령어는 모든 데이터를 삭제합니다. 데이터를 백업하고 삭제해야 할 경우에만 실행하세요!!!

## 주의 사항

#### 디스크 공간 부족 및 백업

업로드된 파이와 데이터베이스 데이터는 가장 많은 디스크 공간을 사용합니다. 사용 가능한 디스크 공간을 확인하고 백업을 생성하여 예기치 않은 문제를 방지해야 합니다. 백업을 생성하려면 다음 Docker 볼륨을 확인하고 복사할 내용을 파악하세요.

- `api_upload`: 파이가 업로드되는 위치.

```bash
docker cp protopie_api_1:/app/upload [[백업 경로]]
```

- `pg_data`: 데이터베이스 데이터가 저장되는 위치.

```bash
docker exec protopie_db_1 pg_dump -c -U postgres protopie > [[백업 경로]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pie 파일 및 데이터베이스 복원

- `api_upload`: 업로드된 데이터 복원.

```bash
docker cp [[백업 경로]] protopie_api_1:/app/

예: docker cp ./upload protopie_api_1:/app/
```

- `pg_data`: 데이터베이스 데이터 복원.

```bash
cat [[백업 경로]]/protopie_db_xxx.sql |  docker exec -i protopie_db_1 psql -U postgres protopie
```

## 업그레이드 및 다운그레이드

업데이트 및 다운그레이드 전에 데이터 안전을 보장하기 위해 서버의 스냅샷 이미지를 생성하고 위의 방법으로 데이터를 백업하여 안전한 위치에 보관하는 것이 좋습니다.

#### 버전 업데이트

1. `docker-compose.yml` 파일이 포함된 디렉토리로 이동합니다: (예: cd /home/victor/enterprise-onpremises)
   (Windows의 경우, Windows 탐색기에서 `docker-compose.yml` 파일이 포함된 디렉토리로 이동합니다(예: c:\local\lib\protopie))

2. 텍스트 편집기로 `docker-compose.yml` 파일을 엽니다:

```bash
sudo vi docker-compose.yml
```

3. 다음 부분을 찾아 수정하고 저장합니다:

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-15.2.0

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-15.2.0
```

4. 실행 중인 ProtoPie 서비스를 중지합니다:

```bash
docker-compose -p protopie stop
```

(Windows의 경우: Win + r 단축키 => 실행 창에 "cmd"를 입력하고 열기, `cd` 명령어로 protopie 파일 경로로 이동합니다(예: cd c:\local\lib\protopie))

5. 중지된 서비스 컨테이너를 제거합니다:

```bash
docker-compose -p protopie rm
```

6. 업데이트된 ProtoPie 서비스를 백그라운드 모드로 시작합니다:

```bash
docker-compose -p protopie up -d
```

7. 브라우저에서 "protopie URL"에 접근합니다(IE, Chrome).

#### 버전 다운그레이드

`api`의 경우 ProtoPie Enterprise는 버전 다운그레이드를 잘 지원하지 않을 수 있습니다. 주요 또는 부차적 버전 업데이트에는 데이터베이스 스키마 변경이 포함될 수 있으며, `api`는 시작 시 이를 검사하고 데이터베이스 스키마 변경이 포함된 경우 데이터베이스 마이그레이션을 시도합니다. 따라서 버전 다운그레이드 시 마이그레이션된 데이터베이스 스키마로 인해 `api`가 오류를 발생시킬 수 있습니다.

- enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
- enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### 버전 불일치

`docker-compose` 서비스 이름에서 알 수 있듯이, `web`은 데이터를 가져와 페이지에 표시하기 위해 `api`로 요청을 보냅니다. 이 서비스들은 긴밀하게 결합되어 있지만 독립적인 서비스입니다. 따라서 `web`과 `api`의 버전이 일치하는 부차적 버전(패치 버전이 아님)을 사용해야 합니다. 버전이 일치하지 않으면 `web`의 요청이 오류 메시지와 함께 응답될 수 있습니다.

## 문제 해결 가이드

이 문제 해결 가이드를 적용한 후 항상 브라우저 캐시를 비우고(비활성화) 확인하세요.

#### Docker 로그에서 "/bin/bash^M: bad interpreter: no such file or directory" 오류 발생 시(postgres:10.5-alphine Docker 컨테이너)

이 문제는 주로 LF와 CRLF 인코딩 충돌로 인해 발생합니다. Windows에서 git을 사용해 리포지토리를 클론한 후 Windows 버전 Docker로 배포하면 이 문제가 발생할 수 있습니다. 이를 해결하려면 최소한 다음 세 가지 파일이 LF 인코딩 형식인지 확인해야 합니다: `db-init\01-init.sh`, `db-init\02-init-db.sh`, `db.env`.

Windows 또는 Mac에서 Sublime Text로 스크립트를 편집하는 경우:
보기 > 줄 끝 > Unix로 설정하고 파일을 다시 저장합니다.

notepad++에서는:
편집 > EOL 변환 > UNIX/OSX 형식으로 설정합니다.

여분의 CR 문자를 제거하려면 다음 명령어를 사용할 수 있습니다:

```bash
sed -i -e 's/\r$//' setup.sh
```

vi로 스크립트를 편집하는 경우:

```bash
vi run.sh
:set fileformat=unix
```

#### HTTP 환경에서 발생하는 일반적인 구성 오류

`config.yml`에서 `tls` 및 `ssl`이 `false`로 설정되었는지 확인하세요.

#### 서버의 80번 포트가 다른 애플리케이션에 의해 사용 중인 경우

일부 고객의 서버에서 80번 포트가 다른 애플리케이션에 의해 사용 중인 경우가 있습니다. 따라서 ProtoPie 로컬 서비스가 사용할 포트를 변경하는 것이 좋습니다. `docker-compose.yml` 파일을 수정하여 `services.nginx.ports` 항목을 `80:80`에서 `8080:80`으로 조정하고, `config.yml` 파일의 `servers.http` 항목을 `http://192.168.xxx.xxx`에서 `http://192.168.xxx.xxx:8080`으로 변경합니다. 이 단계를 완료한 후 업데이트된 URL 및 포트 정보를 제공해 주시면 해당 포트로 새 인증서를 제공해 드리겠습니다. 이후 기존 인증서를 교체해야 합니다.

참고: 80번 포트는 HTTP의 기본 포트이므로 웹 브라우저에서 일반적으로 표시되지 않습니다. 그러나 서비스 포트를 8080으로 변경한 경우 URL에 새 포트를 명시해야 합니다. 예를 들어, 원래 `http://192.168.xxx.xxx`에서 서비스를 사용했다면 이제는 `http://192.168.xxx.xxx:8080`으로 변경해야 합니다.

#### 인터넷 연결이 없는 서버에 Docker 이미지 배포

배포 중에는 서버가 Docker 이미지를 가져오기 위해 인터넷 연결이 필요합니다. 배포가 완료된 후에는 필요에 따라 조직의 보안 정책에 따라 인터넷 연결을 해제할 수 있습니다. 인터넷에 연결되지 않은 서버에 배포해야 하는 경우, 인터넷에 연결된 컴퓨터에서 아래 Docker 명령을 사용하여 이미지를 가져오고 저장할 수 있습니다:

```bash
docker pull nginx:1.21.1-alpine
docker pull protopie/enterprise-onpremises:web-15.2.0
docker pull protopie/enterprise-onpremises:api-15.2.0
docker pull postgres:10.5-alpine

docker save -o nginx_1.21.1-alpine.tar nginx:1.21.1-alpine
docker save -o web_latest.tar protopie/enterprise-onpremises:web-15.2.0
docker save -o api_latest.tar protopie/enterprise-onpremises:api-15.2.0
docker save -o postgres_10.5-alpine.tar postgres:10.5-alpine
```

**참고:** `15.2.0`을 필요한 최신 버전으로 교체하십시오.

그런 다음 안전한 방법(USB 또는 내부 네트워크)을 통해 저장된 파일을 대상 서버로 전송하고, 대상 서버에서 다음 명령을 실행하여 전송된 이미지를 로드합니다:

```bash
docker load -i nginx_1.21.1-alpine.tar
docker load -i web_latest.tar
docker load -i api_latest.tar
docker load -i postgres_10.5-alpine.tar
```
