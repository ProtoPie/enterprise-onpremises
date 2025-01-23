_[English](README.md) ∙ [简体中文](docs/README.zh-Hans.md) ∙ [日本語](docs/README.ja.md) ∙ [한국어](docs/README.ko.md)_

# Deploying ProtoPie Enterprise on an On-Premises Server

This is the official guide for deploying ProtoPie Enterprise using Docker Compose on your on-premises servers.

ProtoPie Enterprise is part of the ProtoPie ecosystem and is a cloud environment designed for team collaboration. The cloud environments within the ProtoPie ecosystem include:

1. **ProtoPie Cloud (Public Cloud Environment)**: For Free, Basic, and Pro plan users, accessible at https://cloud.protopie.io
2. **ProtoPie Enterprise Cloud Environment**: Includes the following deployment options:
   - **Private Cloud**: A dedicated space on AWS for specific customers, accessible at https://your-organization.protopie.cloud
   - **On-Premises**: Deployed on your organization's own servers, accessible via the server's IP (e.g., http://192.168.xxx.xxx) or domain name (e.g., https://protopie.your.domain). This document will discuss this deployment method.

To learn more about the ProtoPie ecosystem, please visit:

- [ProtoPie Ecosystem](https://www.protopie.io/learn/docs/introducing-protopie/protopie-ecosystem)
- [ProtoPie Cloud](https://www.protopie.io/learn/docs/cloud/getting-started)
- [ProtoPie Enterprise](https://www.protopie.io/learn/docs/enterprise/getting-started)

## Deployment Preparation

Before deploying ProtoPie Enterprise on your server, ensure you meet the following hardware, operating system, and software requirements. Also, provide us with the URL you plan to use to access the server. This URL will be used for browser access to the cloud environment and for logging in via ProtoPie Studio, ProtoPie Connect, or ProtoPie Player using the “Log in with Secure Enterprise” feature. We will generate a certificate pem file based on the URL you provide.

Note: We generally recommend deploying ProtoPie Enterprise On-Premise on a dedicated Linux server and installing ProtoPie Studio and ProtoPie Connect on separate PCs to connect to the server. In special cases, such as for testing or if you are the sole user, you can deploy ProtoPie Enterprise On-Premise and install ProtoPie Studio and ProtoPie Connect on the same PC (Windows or macOS).

## Hardware Requirements

|             | Qty | CPU(core)      | Memory |
| ----------- | --- | -------------- | ------ |
| Minimum     | 1   | 1 core 64bits  | 4GB    |
| Recommended | 1   | 2 cores 64bits | 8GB    |

- Storage: Depends on how many prototypes will be saved.

## Operating System Requirements

If you can perform a fresh installation of the server operating system, it is recommended to use the latest LTS version of Linux Debian 12.

### Linux

- Debian 9+
- Fedora 28+
- Ubuntu 18.04+

### Windows

- Windows 10 64-bit: Professional, Enterprise, or Education editions (1607 Anniversary Update, Build 14393 or higher)

### macOS

- 10.12+

## Software Requirements

- Docker 1.13.0+
- Docker Compose 1.10.0+

## Preparatory Work

### Clone the Repository

```bash
git clone https://github.com/ProtoPie/enterprise-onpremises.git
```

### Modify Files

Before running ProtoPie Enterprise, check and modify the following files:

#### license.pem

Rename the pem certificate file we generate to `license.pem` and move it to the same directory as the `docker-compose.yml` file.

#### config.yml

The `config.yml` file contains basic configuration for ProtoPie Enterprise, such as:

- `servers.http`: URL where ProtoPie Enterprise will run (e.g., `http://192.168.xxx.xxx` or `https://protopie.your.domain`).
- `mail.smtp`: SMTP configuration for sending emails (e.g., for inviting members or changing passwords). If not configured, you will need to manually copy the invitation link and send it to the invitees.

#### db.env

The `db.env` file contains configuration for initializing the database, including `root user` and `protopie db`. This file may not need modification.

### Configure HTTPS or No Encryption

We strongly recommend using HTTPS for security reasons, but you can choose not to use HTTPS.

#### If Not Using HTTPS

If not using HTTPS, such as using an IP address without a domain, modify the `nginx.conf` file as follows to support non-HTTPS operation:

Change line 45 from:

```nginx
listen 80;

location / {
    proxy_pass http://web_server;
}
```

To:

```nginx
listen 80;

location / {
    sub_filter_once off;
    sub_filter_types text/html;
    sub_filter "<meta http-equiv=\"Content-Security-Policy\" content=\"upgrade-insecure-requests\"/>" "";
    proxy_pass http://web_server;
}
```

#### If Using HTTPS

##### Generate SSL Certificate (.crt) Using OpenSSL

Use the following command to create an SSL certificate (.crt), ensuring you have both the private key (.key) and certificate signing request (.csr) files:

```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```

For example:

```bash
openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

##### Modify Relevant Files

If you have an SSL/TLS certificate, insert the following configuration into the `nginx.conf` file properly:

```nginx
server {
    listen 443;
    server_name localhost;
    ssl on;
    ssl_certificate /etc/nginx/ssl/protopie.crt; # docker container file path
    ssl_certificate_key /etc/nginx/ssl/protopie.key; # docker container file path

    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;

    location / {
        proxy_pass http://web_server;
    }
}
```

Modify the `docker-compose.yml` file as follows:

```yaml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro # Local file path : docker container file path
      - ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro # Local file path : docker container file path
    ports:
      - 443:443 # Local port : docker container port
    links:
      - web
      - api
```

Modify the `config.yml` file to ensure HTTPS usage:

```yaml
servers:
  http: https://protopie.your.domain
  update: https://autoupdate.protopie.io
```

## Start and Run

After editing the above files, you can start the Docker containers and run ProtoPie Enterprise. Use the following command to run the containers in the background:

```bash
docker-compose -p protopie up -d
```

You may need to log in to your Docker ID using `docker login` to pull these Docker images from Docker Hub.

You can then access it at `http://192.168.xxx.xxx` or `https://protopie.your.domain`.

### For Windows

These Docker images are based on Linux. If you are using Windows, it is recommended to use `Docker for Windows` with Hyper-V to run Linux containers on Windows. For more details, please refer to the following link.

- https://docs.docker.com/docker-for-windows

### For macOS

If you are using macOS, it is recommended to use HomeBrew and install Docker and Docker Compose with the following commands:

```bash
brew install docker docker-compose colima
```

## Common Management Commands

After successfully deployed, you may need these commands to help you manage and view Docker containers. Note that `docker-compose` commands need to be run in the directory where the `docker-compose.yml` file is located.

```bash
docker ps
```

Lists the currently running Docker containers. ProtoPie Enterprise consists of four services in Docker Compose, all based on Docker images:

- `nginx` - Network server
- `web` - Web application interface
- `api` - Backend API
- `db` - Database server

```bash
docker-compose -p protopie restart
```

Restarts all service containers defined in the `protopie` compose project.

```bash
docker-compose -p protopie stop
```

Stops all service containers defined in the `protopie` compose project.

```bash
docker-compose -p protopie down
```

Stops and removes all services, networks, and cache volumes defined in the `protopie` compose project.
Note that even if containers are stopped or removed, the `db` data will persist as it is bound to the host file system.

```bash
docker-compose -p protopie logs
```

Displays logs for all services defined in the `protopie` compose project.

```bash
docker network ls
```

Lists all Docker networks.

```bash
docker volume ls
```

Lists all Docker volumes.

```bash
docker volume rm protopie_api_logs protopie_api_upload protopie_api_download protopie_pg_data
```

Deletes all specified Docker volumes. WARNING: This command will delete all data. Only execute this if you have backed up the data and confirmed you need to do so!

## Notes

#### Disk Space and Backup

Uploaded Pies with images and database data will use the most disk space. You must check available disk space regularly and create backups to prevent any unexpected issues. To create backups, check the following Docker volumes for what needs to be copied:

- `api_upload`: Location where Pies are uploaded.

```bash
 docker cp protopie_api_1:/app/upload [[BACKUP_PATH]]
```

- `pg_data`: Location where database data is stored.

```bash
docker exec protopie_db_1 pg_dump -c -U postgres protopie > [[BACKUP_PATH]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Restore Pie Files and Database

- `api_upload`: Restore uploaded data.

```bash
 docker cp [[BACKUP_PATH]] protopie_api_1:/app/

 For example: docker cp ./upload protopie_api_1:/app/
```

- `pg_data`: Restore database data.

```bash
cat [[BACKUP_PATH]]/protopie_db_xxx.sql |  docker exec -i protopie_db_1 psql -U postgres protopie
```

## Upgrading and Downgrading

Before updating or downgrading, it is recommended to create a snapshot of the server for data safety and also use the backup methods above to store the data in a secure location.

#### Updating Version

1. Navigate to the directory containing the `docker-compose.yml` file (e.g., `cd /home/victor/enterprise-onpremises`)
   (For Windows, navigate to the directory containing the `docker-compose.yml` file in Windows Explorer (e.g., `c:\local\lib\protopie`))

2. Open the `docker-compose.yml` file with a text editor:

```bash
vi docker-compose.yml
```

3. Find, modify, and save the following sections

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-15.1.0

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-15.1.0

```

4. Stop the running ProtoPie services:

```bash
docker-compose -p protopie stop
```

(For Windows: Use Win + R shortcut to open the Run window, type "cmd" to open it, and navigate to the above file path (e.g., `cd c:\local\lib\protopie`))

5. Remove the stopped service containers:

```bash
docker-compose -p protopie rm
```

Note that even if containers are stopped or removed, the `db` data will persist as it is bound to the host file system.

6. Start the updated ProtoPie services in detached mode:

```bash
docker-compose -p protopie up -d
```

7. Access the "protopie URL" from a browser (IE, Chrome)

#### Downgrading Version

Note that ProtoPie Enterprise may not support version downgrades well in the `api` case. This is because major or minor version updates might include database schema changes, and the `api` checks this when starting. If a version downgrade occurs, due to the migrated database schema, the `api` might encounter errors.

- enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
- enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### Version Mismatch

As you might notice from the Docker Compose service names, `web` sends requests to `api` to fetch data and display it on the page. Although these services are closely coupled, they are isolated as services. Therefore, ensure that `web` and `api` versions have matching minor versions (not patch versions). If versions mismatch, `web` requests will return error messages.

## Troubleshooting Guide

Always ensure that browser cache is cleared(disabled) after applying this troubleshooting guide.

#### docker logs (postgres:10.5-alphine docker container) "/bin/bash^M: bad interpreter: no such file or directory" error

This issue is often caused by LF and CRLF encoding conflicts. If you cloned the repository on Windows with git and then deployed using Docker for Windows, you might encounter this issue. Ensure at least the following three files are in LF encoding format: `db-init\01-init.sh`, `db-init\02-init-db.sh`, and `db.env`.

If you use Sublime Text to edit scripts on Windows or macOS:
Click View > Line Endings > Unix and save the file again.

In Notepad++, you can:
Edit --> EOL Conversion --> UNIX/OSX Format

Remove extra CR characters. You can use the following command to do this:

```bash
sed -i -e 's/\r$//' setup.sh
```

If you use `vi` to edit the script:

```bash
vi run.sh
:set fileformat=unix
```

#### Common Configuration Errors in HTTP Only Environments

Check if `tls` `ssl` is set to `false` in `config.yml`

#### Port 80 on the Server is Being Used by Another Application

We have found that some customer servers have port 80 occupied by other applications. In such cases, you can change the port used by ProtoPie On-Premises services. You can modify the `docker-compose.yml` file to change `services.nginx.ports` from `80:80` to `8080:80`, and update the `config.yml` file's `servers.http` entry from `http://192.168.xxx.xxx` to `http://192.168.xxx.xxx:8080`. After completing these steps, provide us with the updated URL and port information so that we can generate a new certificate for your service. You will need to replace the existing certificate.

Note that since port 80 is the default port for HTTP, web browsers typically do not show the port. If the service port changes to 8080, you will need to specify the new port in the URL. For example, if the service was accessed via `http://192.168.xxx.xxx`, it should now be `http://192.168.xxx.xxx:8080`.

#### Deploy Docker images on servers without internet access

During deployment, the server requires internet access to pull Docker images. After deployment, you may disconnect the internet connection according to your organization's security policy if needed. If your organization requires deployment on a server without internet access, you can pull and save the Docker images from a computer with internet access using the following Docker commands:

```bash
docker pull nginx:1.21.1-alpine
docker pull protopie/enterprise-onpremises:web-15.1.0
docker pull protopie/enterprise-onpremises:api-15.1.0
docker pull postgres:10.5-alpine

docker save -o nginx_1.21.1-alpine.tar nginx:1.21.1-alpine
docker save -o web_latest.tar protopie/enterprise-onpremises:web-15.1.0
docker save -o api_latest.tar protopie/enterprise-onpremises:api-15.1.0
docker save -o postgres_10.5-alpine.tar postgres:10.5-alpine
```

**Note:** Please replace `15.1.0` with the latest version you need.

Then, transfer the saved files to the target server through secure methods (such as USB or internal network), and run the following commands on the target server to load the transferred images:

```bash
docker load -i nginx_1.21.1-alpine.tar
docker load -i web_latest.tar
docker load -i api_latest.tar
docker load -i postgres_10.5-alpine.tar
```
