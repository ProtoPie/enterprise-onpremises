*[English](../README.md) ∙ [简体中文](README.zh-Hans.md) ∙ [日本語](README.ja.md) ∙ [한국인](README.ko.md)*

# 在本地服务器上部署ProtoPie Enterprise

这是使用Docker Compose在您的本地服务器上部署ProtoPie Enterprise的官方指南。

ProtoPie Enterprise属于ProtoPie生态系统的一部分，是一种为了方便团队协作的云环境。ProtoPie生态系统中的云环境包括：

1. **ProtoPie Cloud（公共云环境）**：适用于Free、Basic和Pro计划用户，访问URL为 https://cloud.protopie.io 
2. **ProtoPie Enterprise云环境**：分为以下两种部署方式：
   - **Private Cloud（私有云环境）**：在AWS上为指定客户独立划分的空间，访问URL为 https://your-organization.protopie.cloud 
   - **On-Premises（本地服务器）**：在您的组织本地的服务器上部署，访问URL为服务器的IP（例如 http://192.168.xxx.xxx ）或服务器的域名（例如 https://protopie.your.domain ）。这篇文档将讨论这种部署方式

了解更多ProtoPie生态系统，请访问：
- [ProtoPie Ecosystem](https://www.protopie.io/learn/docs/introducing-protopie/protopie-ecosystem)
- [ProtoPie Cloud](https://www.protopie.io/learn/docs/cloud/getting-started)
- [ProtoPie Enterprise](https://www.protopie.io/learn/docs/enterprise/getting-started)

## 部署准备
在您的服务器上部署ProtoPie Enterprise之前，请确保满足以下硬件、操作系统和软件要求。接着，请将您计划用于访问服务器的URL提供给我们。这个URL将用于浏览器访问云环境，也用于在ProtoPie Studio、ProtoPie Connect或ProtoPie Player中通过“Log in with Secure Enterprise”功能输入。

我们将根据您提供的URL生成证书pem文件。部署过程中，服务器需要访问互联网以拉取Docker镜像。部署完成后，若有需要，您可以根据组织的安全策略断开互联网连接。

注意：我们通常推荐将ProtoPie Enterprise On-Premise部署在专门的Linux服务器上，并在另外多台PC上安装ProtoPie Studio和ProtoPie Connect，然后连接到服务器上使用。特殊情况下，例如测试或仅您一人使用时，您也可以在同一台PC上（Windows或MacOS）同时部署ProtoPie Enterprise On-Premise并安装ProtoPie Studio和ProtoPie Connect。

## 硬件要求
|             	| 数量 	| CPU(核心) 	| 内存 	|
|-------------	|-----	|-----------	|--------	|
| 最低要求     	| 1   	| 1核 64位	| 4GB    	|
| 推荐配置 	| 1   	| 2核 64位	| 8GB    	|
* 存储：取决于将保存多少原型。

## 操作系统要求
如果您可以全新安装服务器操作系统的话，推荐用Linux的Debian LTS最新版12
### Linux
* Debian 9+
* Fedora 28+
* Ubuntu 18.04+
### Windows
* Windows 10 64位：专业版、企业版或教育版（1607周年更新，构建14393或更高版本）
### macOS
* 10.12+

## 软件要求
 * Docker 1.13.0+
 * Docker Compose 1.10.0+


## 准备工作

### 克隆仓库

```bash
git clone https://github.com/ProtoPie/enterprise-onpremises.git
```

### 修改文件

在运行ProtoPie Enterprise之前，请检查并修改以下文件。

#### license.pem

将我们生成的pem证书文件重命名为`license.pem`，并将其移动到`docker-compose.yml`文件所在的同一目录。

#### config.yml

`config.yml`文件包含了ProtoPie Enterprise的基本配置，例如：

- `servers.http`：ProtoPie Enterprise运行的URL（例如 `http://192.168.xxx.xxx` 或 `https://protopie.your.domain`）。
- `mail.smtp`：用于发送电子邮件的SMTP配置（例如邀请成员或更改密码）。如果不配置此选项，邀请成员时需要手动复制邀请链接发送给被邀请人。

#### db.env

`db.env`文件包含用于初始化数据库的配置，包括`root user`和`protopie db`。这个文件可以不修改。

### 配置HTTPS加密或不加密

我们强烈建议您出于安全原因使用HTTPS，但您也可以选择不使用HTTPS。

#### 如果不使用HTTPS加密

如果不使用HTTPS，比如没有域名而使用IP地址，可以通过以下步骤修改nginx.conf文件，使其支持不使用HTTPS的情况下运行。

将第45行从：

```nginx
listen 80;

location / {
    proxy_pass http://web_server;
}
```

修改为：

```nginx
listen 80;

location / {
    sub_filter_once off;
    sub_filter_types text/html;
    sub_filter "<meta http-equiv=\"Content-Security-Policy\" content=\"upgrade-insecure-requests\"/>" "";
    proxy_pass http://web_server;
}
```

#### 如果使用HTTPS加密

##### 使用OpenSSL生成SSL证书（.crt）

使用以下命令创建SSL证书（.crt），确保同时拥有私钥（.key）和证书签名请求（.csr）文件：

```bash
openssl x509 -req -days 365 -in <filename>.csr -signkey <filename>.key -out <filename>.crt
```

例如：

```bash
openssl x509 -req -days 365 -in protopie.csr -signkey protopie.key -out protopie.crt
```

##### 修改相关文件

如果您有SSL/TLS证书，请将以下配置正确插入到`nginx.conf`文件中：

```nginx
server {
    listen 443;
    server_name localhost;
    ssl on;
    ssl_certificate /etc/nginx/ssl/protopie.crt; #docker容器文件路径
    ssl_certificate_key /etc/nginx/ssl/protopie.key; #docker容器文件路径

    ssl_session_timeout 5m;
    ssl_protocols SSLv2 SSLv3 TLSv1;

    location / {
        proxy_pass http://web_server;
    }
}
```

修改`docker-compose.yml`文件如下：

```yaml
services:
  nginx:
    image: nginx:1.21.1-alpine
    hostname: ppeop_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx-html:/usr/share/nginx/html:ro
      - ./ssl/protopie.key:/etc/nginx/ssl/protopie.key:ro  # 本地文件路径 : docker容器文件路径
      - ./ssl/protopie.crt:/etc/nginx/ssl/protopie.crt:ro  # 本地文件路径 : docker容器文件路径
    ports:
      - 443:443  # 本地端口 : docker容器端口
    links:
      - web
      - api
```

修改`config.yml`文件，确保使用https：

```yaml
servers:
  http: https://protopie.your.domain  
  update: https://autoupdate.protopie.io
```

## 启动和运行

编辑上述文件后，可以启动`docker-compose.yml`中的Docker容器并运行ProtoPie Enterprise。执行以下命令通过Docker Compose在后台运行容器：

```bash
docker-compose -p protopie up -d
```

请注意，您可能需要通过`docker login`登录您的Docker ID才能从docker hub拉取这些docker镜像。

然后，您可以在 `http://192.168.xxx.xxx` 或 `https://protopie.your.domain` 访问它。

### 对于Windows

这些docker镜像基于linux。所以如果您使用Windows，建议使用`Docker for Windows`配合hyper-v在Windows上运行linux容器。详细信息请参见以下链接。

* https://docs.docker.com/docker-for-windows

### 对于MacOS

如果您使用MacOS，推荐使用HomeBrew，然后用下面的命令安装docker和docker-compose:

```bash
brew install docker docker-compose colima
```

## 常用的管理命令
部署成功后您可能需要用到这些命令帮助你管理和查看Docker容器，注意docker-compose命令需要在docker-compose.yml所在的文件夹中运行

```bash
docker ps
```
列出当前正在运行的Docker容器。ProtoPie Enterprise由Docker Compose中的四个服务组成，这些服务都是docker镜像。

* `nginx` - 网络服务器
* `web` - 网络应用程序接口
* `api` - 后端API
* `db` - 数据库服务器

```bash
docker-compose -p protopie restart
```
重启所有在compose项目protopie中定义的服务容器。

```bash
docker-compose -p protopie stop
```
停止所有在compose项目protopie中定义的服务容器。

```bash
docker-compose -p protopie down
```
停止并移除所有在compose项目protopie中定义的服务、网络和缓存卷。
请注意，即使容器停止或被移除，`db`数据也会持续存在，因为`db`绑定挂载到了主机文件系统。

```bash
docker-compose -p protopie logs
```
显示在compose项目protopie中定义的所有服务的日志。

```bash
docker network ls
```
列出所有Docker网络。

```bash
docker volume ls
```
列出所有Docker卷。

```bash
docker volume rm protopie_api_logs protopie_api_upload protopie_api_download protopie_pg_data
```
删除所有的Docker卷。！！！危险注意：最后这个命令会删除所有数据，只有当你备份了数据并确认需要的时候才这样做！！！

## 注意事项

#### 磁盘空间不足和备份

上传的Pies和数据库数据将使用最多的磁盘空间。必须检查可用磁盘空间并创建备份，以防止任何意外问题。如果您想创建备份，请检查下面的docker卷，了解您需要复制的内容。

* `api_upload`：Pie上传到的位置。
```bash
 docker cp protopie_api_1:/app/upload [[备份路径]]
```
 
* `pg_data`：数据库数据存储的位置。
```bash
docker exec protopie_db_1 pg_dump -c -U postgres protopie > [[备份路径]]/protopie_db_`date +%y%m%d%H%M%S`.sql
```

#### Pie文件和数据库恢复
* `api_upload`：上传的数据恢复。

```bash
 docker cp [[备份路径]] protopie_api_1:/app/

 例如: docker cp ./upload protopie_api_1:/app/ 
```
 
* `pg_data`：数据库数据恢复。

```bash
cat [[备份路径]]/protopie_db_xxx.sql |  docker exec -i protopie_db_1 psql -U postgres protopie
```
## 升级和降级
更新和降级前，为确保数据安全，建议创建服务器的快照镜像，并使用上述方法备份数据，将其存放在安全的位置。

#### 更新版本

1. 导航至包含`docker-compose.yml`文件的目录：（例如=> cd /home/victor/enterprise-onpremises）
（对于Windows，导航至包含`docker-compose.yml`文件的目录在Windows资源管理器中（例如=> c:\local\lib\protopie））

2. 使用文本编辑器打开`docker-compose.yml`文件：
```bash
sudo vi docker-compose.yml
```

3. 查找、修改并保存以下部分

```
web:
image: protopie/enterprise-onpremises:web-9.20.0 => image: protopie/enterprise-onpremises:web-13.1.3

api:
image: protopie/enterprise-onpremises:api-9.20.0 => image: protopie/enterprise-onpremises:api-13.1.3

```

4. 停止正在运行的ProtoPie服务：
```bash
docker-compose -p protopie stop
```
（对于Windows：用Win + r快捷键 => 运行窗口输入"cmd"并打开，移动到cd protopie文件路径（例如=> cd c:\local\lib\protopie））

5. 移除已停止的服务容器：
```bash
docker-compose -p protopie rm
```

6. 以分离模式启动更新后的ProtoPie服务：
```bash
docker-compose -p protopie up -d
```

7. 从浏览器访问"protopie URL"（IE，Chrome）

#### 降级版本

请注意，在`api`的情况下，ProtoPie Enterprise可能无法很好地支持版本降级。因为每次主要或次要版本更新可能包含数据库方案的变化，每次`api`在启动时都会检查它，并且如果版本更新包含数据库方案的变化，`api`将尝试迁移数据库。因此，在版本降级的情况下，由于迁移后的数据库方案，`api`可能会引发错误。

* enterprise-web-1.0.2 / enterprise-api-1.0.8 (O)
* enterprise-web-1.0.2 / enterprise-api-1.1.2 (X)

#### 版本不匹配

正如您可能从docker-compose服务名称中注意到的，`web`向`api`发送请求以获取数据并在页面中显示。这些服务虽然紧密耦合但作为服务是隔离的。因此，请确保`web`和`api`的版本具有匹配的次要版本（不是补丁版本）。如果版本不匹配，`web`的请求将返回带有错误消息的响应。

## 故障排除指南

在应用此故障排除指南后，请始终确保浏览器缓存已清除（禁用）。

#### docker日志（postgres:10.5-alphine docker容器）出现"/bin/bash^M: bad interpreter: no such file or directory"错误时

这个问题通常是由LF与CRLF编码冲突导致的。如果你在Windows上使用git克隆仓库，然后使用Windows版Docker进行部署，你可能会遇到这个问题。要解决这个问题，你需要确保至少以下三个文件是LF编码格式：`db-init\01-init.sh`、`db-init\02-init-db.sh`以及`db.env`。

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

#### 仅HTTP环境下的常见配置错误
请检查`config.yml`中的`tls` `ssl`是否为`false`

#### 服务器上的80端口正被其他应用程序使用
我们发现一些客户服务器上的80端口已被其他应用占用。因此，建议更改ProtoPie本地服务使用的端口。您可以通过修改`docker-compose.yml`文件，将`services.nginx.ports`项从`80:80`调整为`8080:80`，并且更新`config.yml`文件中的`servers.http`项，从`http://192.168.xxx.xxx`更改为`http://192.168.xxx.xxx:8080`。完成这些步骤后，请向我们提供更新后的URL和端口信息，以便我们为您的服务提供新证书。之后，您需要替换现有证书。

请注意，由于80端口是HTTP的默认端口，Web浏览器通常不显示。但如果服务端口更改为8080，您则需要在URL中指明新端口。例如，原先通过`http://192.168.xxx.xxx`访问服务的，现在应改为`http://192.168.xxx.xxx:8080`。