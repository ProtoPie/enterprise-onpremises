*[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)*

# ProtoPie Enterprise 带有本地服务器

这是使用Docker Compose在您的本地服务器上部署ProtoPie Enterprise的官方指南。

首先，克隆这个仓库，按照下面详细的配置进行必要的设置，然后轻松部署您的本地服务器。

## 软件要求
 * Docker 1.13.0+
 * Docker Compose 1.10.0+
 
## 硬件要求
|             	| 数量 	| CPU(核心) 	| 内存 	|
|-------------	|-----	|-----------	|--------	|
| 最低要求     	| 1   	| 1核 64位	| 4GB    	|
| 推荐配置 	| 1   	| 2核 64位	| 8GB    	|
* 存储：取决于将保存多少原型。

## 操作系统要求
### Linux
* CentOS 7+
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### Windows
* Windows 10 64位：专业版、企业版或教育版（1607周年更新，构建14393或更高版本）
### macOS
* 10.12+

## Docker Compose中的服务

ProtoPie Enterprise由Docker Compose中的四个服务组成，这些服务都是docker镜像。

* `nginx` - 网络服务器
* `web` - 网络应用程序接口
* `api` - 后端API
* `db` - 数据库服务器

请注意，您可能需要通过`docker login`登录您的Docker ID才能从docker hub拉取这些docker镜像。

## 准备工作

在运行ProtoPie Enterprise之前，请打开以下文件，按照下面的步骤进行编辑。

#### license.pem

将`license.pem`文件移动到`docker-compose.yml`文件所在的同一目录。

#### config.yml

`config.yml`文件包含了ProtoPie Enterprise的基本配置。例如，
* `servers.http`：ProtoPie Enterprise运行的URL。（例如 http://your.domain）
* `mail.smtp`：用来发送电子邮件的SMTP配置。（例如，邀请成员或更改密码。）

#### db.env

`xxx.env`文件代表应用程序中的环境变量。`db.env`包含两部分配置`root user`和`protopie db`，用于初始化数据库以创建用户和数据库。

## 启动和运行

编辑上述文件后，您就可以启动`docker-compose.yml`中的docker容器，并运行ProtoPie Enterprise。执行以下命令通过docker-compose在后台运行容器。

```bash
$ docker-compose -p protopie up -d
```

然后，您可以在`http://your.domain`访问它。如果您想使用其他端口，请修改`docker-compose.yml`中的`services.nginx.port`和`config.yml`中的`servers.http`。

请注意，即使容器停止或被移除，`db`数据也会持续存在，因为`db`绑定挂载到了主机文件系统。

## 使用SSL/TLS证书进行HTTPS加密
### 使用Openssl生成SSL证书（.crt）
使用OpenSSL创建SSL证书（.crt）时，必须同时拥有私钥（.key）和证书签名请求（.csr）文件。
使用以下命令。
```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```
```bash
例如 =>  openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

我们强烈建议您出于安全原因使用HTTPS。如果您有SSL/TLS证书，请将此配置正确插入到`nginx.conf`文件中。

```nginx conf
          .
          .
          .
     server {
        listen       443;
        server_name  localhost;
        ssl     on;
        ssl_certificate         修改为 => docker容器SSL文件路径  ## /etc/nginx/ssl/protopie.crt;
        ssl_certificate_key     修改为 => docker容器SSL文件路径  ## /etc/nginx/ssl/protopie.key;
        容器SSL文件路径

         ssl_session_timeout  5m;
         ssl_protocols SSLv2 SSLv3 TLSv1;
                 .
                 .
                 .
    }
```

按照以下方式修改docker-compose.yml文件

```docker-compose.yml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - 本地文件路径 : docker容器文件路径 ## 例如: ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro
      - 本地文件路径 : docker容器文件路径 ## 例如: ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro
    ports:
      - 443:443    ## 修改为 =>本地端口 : docker容器端口
    links:
      - web
      - api
```

按照以下方式修改config.yml文件

```config.yml
servers:
  http: https://your-domain         ## 例如 : https://protopie.com
  update: https://autoupdate.protopie.io

```

## 对于Windows

这些docker镜像基于linux。所以如果您使用Windows，建议使用`Docker for Windows`配合hyper-v在Windows上运行linux容器。详细信息请参见以下链接。

* https://docs.docker.com/docker-for-windows

## 注意事项

#### 降级版本

请注意，在`api`的情况下，ProtoPie Enterprise可能无法很好地支持版本降级。因为每次主要或次要版本更新可能包含数据库方案的变化，每次`api`在启动时都会检查它，并且如果版本更新包含数据库方案的变化，`api`将尝试迁移数据库。因此，在版本降级的情况下，由于迁移后的数据库方案，`api`可能会引发错误。

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### 版本不匹配

正如您可能从docker-compose服务名称中注意到的，`web`向`api`发送请求以获取数据并在页面中显示。这些服务虽然紧密耦合但作为服务是隔离的。因此，请确保`web`和`api`的版本具有匹配的次要版本（不是补丁版本）。如果版本不匹配，`web`的请求将返回带有错误消息的响应。

#### 磁盘空间不足和备份

上传的Pies和数据库数据将使用最多的磁盘空间。必须检查可用磁盘空间并创建备份，以防止任何意外问题。如果您想创建备份，请检查下面的docker卷，了解您需要复制的内容。

* `api_upload`：Pie上传到的位置。
```bash
 docker cp protopie_api_1:/app/upload [[备份路径]]
```
 
* `pg_data`：数据库数据存储的位置。
```bash
  docker exec protopie_db_1 pg_dump -c -U protopie_r protopie > [[备份路径]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pie文件和数据库恢复
* `api_upload`：上传的数据恢复。

```bash
 docker cp [[备份路径]] protopie_api_1:/app/

 例如: docker cp ./upload protopie_api_1:/app/ 
```
 
* `pg_data`：数据库数据恢复。

```bash
cat [[备份路径]]/protopie_db_xxx.sql |  docker exec -i app_db_1 psql -U protopie_w protopie
```

# 更新
更新前，为确保数据安全，建议创建服务器的快照镜像，并使用上述方法备份数据，将其存放在安全的位置。
## 如何更新ProtoPie本地部署（Windows）

1. 导航至包含`docker-compose.yml`文件的目录在Windows资源管理器中（例如=> c:\local\lib\protopie）

2. 打开docker-compose.yml文件

3. 查找、修改并保存以下部分

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. 输入"cmd"在窗口键+ r（快捷键）=> 运行窗口

5. 移动到cd protopie文件路径（例如=> cd c:\local\lib\protopie）

6. 停止正在运行的ProtoPie服务：
```bash
docker-compose -p protopie stop
```

7. 移除已停止的服务容器：
```bash
docker-compose -p protopie rm
```

8. 以分离模式启动更新后的ProtoPie服务：
```bash
docker-compose -p protopie up -d
```

9. 从浏览器访问"protopie URL"（IE，Chrome）

## 如何更新ProtoPie本地部署（Linux）

1. 导航至包含`docker-compose.yml`文件的目录：（例如=> cd /home/victor/enterprise-onpremises）

2. 使用文本编辑器打开`docker-compose.yml`文件：
```bash
sudo vi docker-compose.yml
```

3. 查找、修改并保存以下部分

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-11.0.5

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-11.0.5

```

4. 停止正在运行的ProtoPie服务：
```bash
docker-compose -p protopie stop
```

5. 移除已停止的服务容器：
```bash
docker-compose -p protopie rm
```

6. 以分离模式启动更新后的ProtoPie服务：
```bash
docker-compose -p protopie up -d
```

7. 从浏览器访问"protopie URL"（IE，Chrome）

## 故障排除指南

在应用此故障排除指南后，请始终确保浏览器缓存已清除（禁用）。

#### docker日志（postgres:10.5-alphine docker容器）出现"/bin/bash^M: bad interpreter: no such file or directory"错误时

如果您在Windows或Mac上使用Sublime Text编辑脚本：
点击视图 > 行结束符 > Unix并再次保存文件。

在notepad++中，您可以通过按下：
编辑 --> EOL转换 --> UNIX/OSX格式

删除多余的CR字符。您可以使用以下命令执行此操作：
```bash
sed -i -e 's/\r$//' setup.sh
```

如果您使用vi编辑脚本：
```bash
vi run.sh
:set fileformat=unix
```

#### ProtoPie服务器重启（移动ProtoPie服务器安装路径）
```bash
docker-compose -p protopie restart
```

#### ProtoPie服务器停止（移动ProtoPie服务器安装路径）
```bash
docker-compose -p protopie stop
```

#### ProtoPie服务器日志（移动ProtoPie服务器安装路径）
```bash
docker-compose -p protopie logs
```

#### 仅HTTP环境下的常见配置错误
请检查`config.yml`中的`tls` `ssl`是否为`false`

#### 如果服务器没有域名而是IP地址
更新`nginx.conf`第45行如下
```
        # 从
        listen 80;

        location / {
            proxy_pass http://web_server;
        }
```
```
        # 到
        listen 80;

        location / {
            sub_filter_once off;
            sub_filter_types text/html;
            sub_filter "<meta http-equiv=\"Content-Security-Policy\" content=\"upgrade-insecure-requests\"/>" "";
            proxy_pass http://web_server;
        }
```
