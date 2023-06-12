# ProtoPie Enterprise with On-Premises Server

This is the official bootstrap repository for running ProtoPie Enterprise using Docker Compose as an on-premises server.

Clone me. Edit me. Use me.

## Software Requirements
 * Docker 1.13.0+
 * Docker Compose 1.10.0+
 
## Hardware Requirements
|             	| Qty 	| CPU(core) 	| Memory 	|
|-------------	|-----	|-----------	|--------	|
| Minimum     	| 1   	| 1 core 64bits	| 4GB    	|
| Recommended 	| 1   	| 2 cores 64bits| 8GB    	|
* Storage: Depends on how many prototypes will be saved. 

## OS Requirements
### Linux
* CentOS 7+
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### Windows
* Windows 10 64bit : Pro, Enterprise or Education (1607 Anniversary Update, Build 14393 or later)
### macOS
* 10.12+

## Services in Docker Compose

ProtoPie Enterprise is composed of four services as docker images in Docker Compose. 

* `nginx`
* `web`
* `api`
* `db`

Note that please login with your Docker ID via `docker login` to pull these docker images from docker hub.

## Prerequisites

Open the following files, follow the steps below, and edit these files accordingly, before getting ProtoPie Enterprise up and running.

#### license.pem

Move the `license.pem` file to the same directory as `docker-compose.yml`.

#### config.yml

The `config.yml` file holds the basic configurations of ProtoPie Enterprise. For example, 
* `servers.http`: The URL that ProtoPie Enterprise runs on. (e.g. http://your.domain)
* `mail.smtp`: SMTP configuration to send emails. (e.g. inviting members or changing password.)

#### db.env

The `xxx.env` files represent environment variables in the application. `db.env` that has two parts of configurations `root user` and `protopie db` for initial db to create user and database.

## Up and Running

Once you have edited the aforementioned files, you are ready to up the docker containers in `docker-compose.yml` and run ProtoPie Enterprise. Execute below command to run the containers in the background via docker-compose. 

```bash
$ docker-compose -p protopie up -d
```

Then, you can access it at `http://your.domain`. If you want to use another port, modify `services.nginx.port` in `docker-compose.yml` and `servers.http` in `config.yml`.

Note that `db` data will persist even if the container stops or is removed because `db` is bind-mounted to the host file system. 


## HTTPS with a SSL/TLS Certificate
### When you create SSL certificates (.crt) with Openssl.
Private issued by the SSL certificate issuing authority.You must have a key and a certificate signing file.(.csr)
Use the command below.

openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
 ex =>  openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt



We highly recommend that you use HTTPS for security and safety reasons. If you have a SSL/TLS certificate, insert this configuration into the `nginx.conf` file properly.

```nginx conf
          .
          .
          .
     server {
        listen       443;
        server_name  localhost;
        ssl     on;
        ssl_certificate         modify => docker container SSL file path  ## /etc/nginx/ssl/protopie.crt;
        ssl_certificate_key     modify => docker container SSL file path  ## /etc/nginx/ssl/protopie.key;
        container SSL file path

         ssl_session_timeout  5m;
         ssl_protocols SSLv2 SSLv3 TLSv1;
                 .
                 .
                 .
    }
```

Modify the docker-compose.yml file as follows

```docker-compose.yml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - locla file path : docker container file path ## ex: ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro
      - locla file path : docker container file path ## ex: ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro
    ports:
      - 443:443    ## modify =>locla port : docker container port
    links:
      - web
      - api
```


Modify the config.yml file as follows

```config.yml
servers:
  http: https://your-domain         ## ex : https://protopie.com
  update: https://autoupdate.protopie.io

```

## For Windows

These docker images is based on linux. So if you are on windows, recommend that using `Docker for Windows` with hyper-v to run linux container on windows. See below link for the details. 

* https://docs.docker.com/docker-for-windows

## Caveats

#### Version Downgrading

Note that in case of `api`, ProtoPie Enterprise may not work well with version downgrading. Because each major or minor version updates may contain changes in the db scheme, every time `api` checks it while bootstrapping and `api` will try to migrate db if a version update contains changes in the db scheme. Hence, in case of version downgrading, `api` might raise an error due to a migrated db scheme.

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### Version Mismatch

As you might have noticed from the docker-compose services name, `web` sends requests to `api` to get data and shows in page. These are coupled tightly but isolated as a service. Therefore, make sure that `web` and `api` versions have a matching minor version (not patch version). If the versions are mismatched, requests from `web` will return a response with an error message.

#### Running out of Disk Space & Backup

Uploaded Pies with images and database data would use the most disk space. It's needed to check for available disk space and create backups in case of unexpected issues. If you want create a backup, see the docker volumes below for what you need to copy.

* `api_upload`: where a Pie has been uploaded to.

 docker cp protopie_api_1:/app/upload [[BACKUP_PATH]]
 
* `pg_data`: where the database data is stored.

  docker exec protopie_db_1 pg_dump -c -U protopie_r protopie > [[BACKUP_PATH]]/protopie_db_`date +%y%m%d%H%M%S`.sql

#### Pie file and DataBases Restore
* `api_upload`: uploaded data is restore

 docker cp [[BACKUP_PATH]] protopie_api_1:/app/

 ex: docker cp ./upload protopie_api_1:/app/ 
 
* `pg_data`: database data is restore.

cat [[BACKUP_PATH]]/protopie_db_xxx.sql |  docker exec -i app_db_1 psql -U protopie_w protopie


# update
## How to update ProtoPie On-Premises (Windows)

1. Navigate to the path of the protopie file in Windows Explorer (e.g.=> (c:\local\lib\protopie)

2. Open the docker-compose.yml file

3. Find, modify, and save the following parts

```
web:
image: protopie/enterprise-onpremises:web-2021.1.1 => image: protopie/enterprise-onpremises:web-9.20.0

api:
image: protopie/enterprise-onpremises:api-2021.1.1 => image: protopie/enterprise-onpremises:api-9.20.0

```

4. Enter "cmd" in window key + r (short key) => Run window

5. Move to cd protopie file path (e.g.=> cd c:\local\lib\protopie )

6. docker-compose stop

7. docker-compose rm (delete service)

8. docker-compose up -d (install and run updated version)

9. Access "protopie URL" from browser (IE, Chrome)

## How to update ProtoPie On-Premises (Linux)

1. cd "moving the path of a protocol file" (e.g.=> cd /home/victor)

2. sudo vi docker-compose.yml (file open)

3. Find, modify, and save the following parts

```
web:
image: protopie/enterprise-onpremises:web-2021.1.1 => image: protopie/enterprise-onpremises:web-9.20.0

api:
image: protopie/enterprise-onpremises:api-2021.1.1 => image: protopie/enterprise-onpremises:api-9.20.0

```

4. $/home/victor docker-compose stop

5. $/home/victor docker-compose rm (delete service)

6. $/home/victor docker-compose up -d (install and run the update version)

7. Connect "protopie URL" from browser (IE, Chrome)


## Trouble Shooting Guide
#### docker logs (postgres:10.5-alphine docker container) "/bin/bash^M: bad interpreter: no such file or directory" error when it occurs

If you use Sublime Text on Windows or Mac to edit your scripts:
Click on View > Line Endings > Unix and save the file again.

In  notepad++ you can set it for the file specifically by pressing:
Edit --> EOL Conversion --> UNIX/OSX Format

Remove the spurious CR characters. You can do it with the following command:
sed -i -e 's/\r$//' setup.sh

If you use vi to edit your scripts:
vi run.sh
:set fileformat=unix

#### ProtoPie Server restart (move ProtoPie Server install path)
docker-compose protopie restart

#### ProtoPie Server stop (move ProtoPie Server install path)
docker-compose protopie stop

#### ProtoPie Server logs  (move ProtoPie Server install path)
docker-compose protopie logs

