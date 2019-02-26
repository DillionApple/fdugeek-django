# FDU GEEK 后端

## 如何运行

1. 安装Python3

2. 下载项目代码：`git clone https://github.com/DillionApple/fdugeek-django.git`

3. 解压，进入项目目录，执行`pip3 install -r requirements.txt`来安装依赖。建议使用 virtualenv 等隔离工具

4. 执行`./config.sh dev`来自动生成 Django 的`settings.py`文件

5. 执行`ssh-keygen -t rsa`，在项目目录下生成`rsa-keys`以及`rsa-keys.pub`文件，用于JWT认证

6. 执行`python3 manage.py migrate`来生成数据库表单

7. 执行`python3 manage.py runserver 0.0.0.0:8000`来运行测试服务器

8. 通过浏览器访问`127.0.0.1:8000`加对应url，来访问对应接口。推荐使用请求模拟工具 postman

## Github协作指南

代码仓库分为多个分支，每个分支功能如下：

1. master：稳定版本分支，保证该分支可直接部署
2. hotfix：热更新分支，用于线上紧急修复bug
3. dev：开发分支，用于多分支代码协作
4. feature_xxx、bug_fix、其它名称：用于开发新功能、改进已有功能和修复程序bug

### 分支合并策略

1. master: 不可直接push，必须通过 hotfix 或者 dev 分支发送 pull request 来修改
2. hotfix：可以直接push，且在push后，必须向 master 分支和 dev 分支发送  pull request
3. dev: 不可直接push，并只能接收来自 hotfix 和第4类分支的 pull request
4. feature_xxx、bug_fix、其它名称：分支自 dev 分支，可以直接push

pull request 会在 review 之后，合并到对应分支

分支、merge流程图如下：

![分支、merge流程图](https://pic1.zhimg.com/80/v2-e07177517a65128f4dc30c4cd2c03199_hd.png)

### 代码流程规范

后端所编写的新接口，必须要有对应的测试程序。在测试通过后，才能发布 pull request。测试程序利用 django 测试框架，具体编写方式参考`account/tests.py`

后端所编写的新接口，需要将接口 request、response 格式写在对应函数开头的注释中

项目将以Issue的形式进行管理，新的需求、bug会以Issue的形式提出来