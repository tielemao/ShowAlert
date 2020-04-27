# ShowAlert

## Explain

- 利用Python Flask Web框架搭建web站点
- 主要用于读取报警的日志并在网页上展示出来


## ENV

| Project | version | Description |
|---|---|---|
| python | 3.7 | None |
| Flask | 1.0.2 | web框架 |
| Flask-wtf | 0.14.2 | form表单插件 |
| Flask-Bootstrap | 3.3.7.1 | 优化html |
| Flask-Login | 0.4.1 | 登录插件 |
| Flask-SQLAIchemy | 2.3.2 | 数据库插件 |
| SQLAIchemy | 1.3.2 | 采取SQLite数据库 |
| supervisor | 4.0.2 | 监听相关进程，挂掉则重启 |
| Jinja2 | 2.10 | 模板引擎 |
| chinesecalendar | 1.2.2 | 用于判断法定节假日 |
| Flask-APScheduler | 1.11.0 | 定时执行任务 |

## Route

| Route | Function | Methods | Description |
| --- | --- | --- | --- |
| '/' and '/index' | index | GET | 首页 |
| /login | login | GET,POST | 登录 |
| /logout | logout | GET | 注销 |
| /alertlog | alertlog | GET | 查看日志 |
| /alertlog/info |  | GET | info级别日志 |
| /alertlog/warn |  | GET | warn级别日志 |
| /alertlog/critical |  | GET | critical级别日志 |
| /alertlog/urgency |  | GET | urgency级别日志 |
| /flush | flush | GET | 刷新N条最新critical日志 |
| /json_flush | json_flush | GET | 展示table格式的critical日志 |
| /ignore | ignore | GET,POST | 添加忽略报警 |

## Run
进入showlog项目下，输入以下命令
`flask run -h 主机ip -P 端口`
* 例：
```bash
(venv) D:\Code\ShowAlertLog\showlog>flask run -h 127.0.0.1 -p 5000
 * Serving Flask app "showlog.py"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
127.0.0.1 - - [12/Apr/2019 16:30:11] "GET / HTTP/1.1" 302 -
127.0.0.1 - - [12/Apr/2019 16:30:11] "GET /login?next=%2F HTTP/1.1" 200 -
127.0.0.1 - - [12/Apr/2019 16:30:12] "GET /favicon.ico HTTP/1.1" 404 -
```

## Update Daily

### 2019-04-3
* [x] Flask初步框架搭建

### 2019-04-4
- [x] flask-wtf处理web表单
- [x] flask-sqlalchemy ORM（使用SQLite数据库）
- [x] flask-migrate数据迁移插件
- [x] flask-login插件
- [x] 完成用户数据库与登录

### 2019-04-8
- [x] 初步完成日志导入与解析
- [x] 初步完成html页面

### 2019-04-9
- [x] Flask-Bootstrap插件
- [x] 使用Bootsrap美化
- [x] 对log日志中的“#n#"做换行处理
- [x] 对log日志中的”DROP“做过滤去掉
- [x] 对报警级别做了划分标签查看

### 2019-04-16

- [x] 服务器部署，安装python3虚拟环境venv

- [x] 生成requirements.txt文件

  ```bash
  (venv) $ pip freeze > requirements.txt
  ```

- [x] 进入虚拟环境完成安装依赖`(venv) $ pip install -r requirements.txt`

- [x] 安装gunicorn作为生产环境web服务器（wsgi/支持高并发）

- [x] 安装Supervisor工具监视Flask服务器进程，并在其崩溃时自动重启。

- [x] 启动命令变为如：

  ```bash
  (venv) $ gunicorn -b localhost:8000 -w 4 showlog:app
  ```

### 2019-04-28

* [x] Fix 服务器log 文件编码Windows-1252引起的问题。

  ```bash
  /opt/skype/logs/2019-04-28.log
  {'confidence': 0.7299818356320205, 'language': '', 'encoding': 'Windows-1252'}
  ```


* [x] Fix TypeError: 'str' does not support the buffer interface

  ```bash
  File  "/home/wuweizeng/ShowAlertLog/showlog/parse.py", line 24, in log_parse
      new_content = content2.replace("#n#", '\n')
  ```

### 2019-06-13

* [x] parse.py中对log的分析从def优化成class.
* [x] router.py中优化匹配动态URL
* [x] 建立一个一次性只刷新50行报警信息的页面
  * [x] 利用yield和`__next__`方法来获取
* [x] 优化按钮
* [x] 有序列表

### 2019-06-19

- [x] 读取报警信息存储结构从文件读写改为使用list和json
- [x] 倒序读取CRITICAL 级别的N条报警信息
- [x] json展示测试中
- [x] 优化只展示CRITICAL 和 WARN级别

### 2019-06-21

* [x] 读取文件时使用`errors='ignore'`来解决编码问题
* [x] 修复json过滤CRITICAL

### 2019-06-24

* [x] nginx代理访问，侦听服务器公网ip 80 端口，实际是proxy_pass localhost的8000端口。

  ```nginx
     location / {
          # forward application requests to the gunicorn server
          proxy_pass http://localhost:8000;
          proxy_redirect off;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
     }
   
     location /static {
          # handle static files directly, without forwarding to the application
          alias /home/wuweizeng/ShowAlertLog/showlog/static;
          expires 30d;
      }   
  ```

  gunicorn启动多进程：

  ```bash
  gunicorn -b localhost:8000 -w 4 showlog:app
  ```

### 2019-06-25

- [x] 配置supervisor，至此`flask => gunicorn 8000 => nginx 80 / supervisor`一套web应用稳定保障运行。

### 2019-06-26

* [x] 修复单例模式存在的bug

* [x] 修复获取log文件名+15hours(之前存在时差bug）

* [x] 读取json对象并以table方式展示警报

* [x] 解决报警信息宽度过长，使用自动换行


### 2019-08-15

* [x] 修复原报警critical不会显示Urgency级别的bug
* [x] flush页面刷新20条且改为倒序
* [x] json未修复暂隐藏该页面（基本也不会用来看）

### 2019-09-25

* [x] 法定节假日，开发服务器忽略展示CRITICAL级别的日志。
  * [x] 增添判断法定节假日的方法
  * [x] 增添开发服务器的过滤

### 2019-10-30

* [x] 己添加过滤用功能，但未接入前端展示去控制人为增添条件
* [x] 程序自检功能，后端己实现，待实现前端展示

###  2019-11-07

* [x] 添加冬夏令时功能

### 2019-11-19

* [x] 定时执行自检任务（每隔半小时在flush页面输出一条 自检信息）
* [x] 增加忽略展示的功能

### 2019-11-26

* [x] 增强忽略展示，以配置文件的方式存在和进行改动

## ToDo

- [ ] 滚动条拖上到极限自动刷新（Ajax）

- [ ] 预留提供api接口

- [ ] 认证访问己做，为方便测试暂未开启强制登录认证

- [ ] 查看全部的报警页方式改为倒序（考虑使用MQ消息队列）；

  

  

