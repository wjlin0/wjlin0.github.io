> 注意：用的命令行尽量用powershell 有些命令cmd 用不了
>
> 比如：mv等
1
## 安装Gitbook所需工具

### 安装gitbook-cli

用于gitbook 命令行的安装

```powershell
npm install gitbook-cli -g
gitbook --version
```

![image-20221129215233580](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129215233580.png)

### 安装gitbook summary

用于自动生成Summary.md，该文件为目录文件

```bash
npm install -g gitbook-summary
book --version
```

![image-20221129220021247](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129220021247.png)

## 创建项目

### 编写book.json

> 用来导入插件 或指定全局配置，至于每个插件的用法可百度查询或在这个[文章](https://www.cnblogs.com/mingyue5826/p/10307051.html#217-donate--%E6%89%93%E8%B5%8F%E6%8F%92%E4%BB%B6)中查看。

```json
{
    "title": "Wjlin0 Gitbook",
    "author":"Wjlin0",
    "description":"记录学习笔记",
    "language":"zh-hans",
    "root":"./docs",
    "links" : {
      "sidebar" : {
          "博客地址" : "https://wjlin0.com"
      }
   },

    "plugins" : [
      "back-to-top-button",
      "expandable-chapters",
      "github-buttons",
      "copy-code-button",
      "page-footer-ex",
      "anchor-navigation-ex",
      "-lunr", 
      "-search", 
      "hide-element",
      "search-pro",
      "donate",
      "splitter",
      "github",
      "-sharing",
      "sharing-plus",
      "custom-favicon",
      "page-treeview"
    ],
    "pluginsConfig": {
      "github": {
        "url": "https://github.com/wjlin0"
    },
    "page-treeview": {
      "copyright": "Copyright &#169; wjlin0",
      "minHeaderCount": "2",
      "minHeaderDeep": "2"
  },
    "favicon": "./favicon.ico",
    "hide-element": {
      "elements": [".gitbook-link",".treeview__copyright",".treeview__main-title"
    ]
  },
      "github-buttons": {
          "buttons": [{
          "user": "wangzhebufangqi",
          "repo": "ActionTest",
          "type": "star",
          "size": "small"
        }]
      },  
      "page-footer-ex": {
              "copyright": "By [Wjlin0](https://wjlin0.com/)，使用[知识共享 署名-相同方式共享 4.0协议](https://creativecommons.org/licenses/by-sa/4.0/)发布",
              "markdown": true,
              "update_label": "更新时间：",
              "update_format": "YYYY-MM-DD HH:mm:ss"
      },   
      "donate": {
        "wechat": "",
        "alipay": "",
        "title": "",
        "button": "赏",
        "alipayText": "支付宝捐赠",
        "wechatText": "微信捐赠"
      },
      "sharing": {
        "douban": false,
        "facebook": false,
        "google": true,
        "hatenaBookmark": false,
        "instapaper": false,
        "line": true,
        "linkedin": true,
        "messenger": false,
        "pocket": false,
        "qq": false,
        "qzone": true,
        "stumbleupon": false,
        "twitter": false,
        "viber": false,
        "vk": false,
        "weibo": true,
        "whatsapp": false,
        "all": [
            "douban", "facebook", "google", "hatenaBookmark", 
            "instapaper", "linkedin","twitter", "weibo", 
            "messenger","qq", "qzone","viber","vk","weibo",
            "pocket", "stumbleupon","whatsapp"
        ]
    }
      
    }
  }
```

### 创建根目录，导入笔记

> 导入自己的笔记

```
mkdir docs
notepad.exe .\docs\README.md //图片中打错了
```

![image-20221129220950545](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129220950545.png)



### 生成SUMMARY.MD文件

```powershell
cd docs
book sm
```

![image-20221129221123486](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129221123486.png)

### 构建项目静态文件

```
cd ../
gitbook install
gitbook build
```

构建完成之后，会生成几个目录，_book 为生成的静态资源 node_modules 为 node js的 模块文件

![image-20221129221603529](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129221603529.png)

### 测试本地环境

```
gitbook serve
```

![image-20221129223221641](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129223221641.png)

![image-20221129223249357](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129223249357.png)

## 构建github Page

> 免费的存放静态资源文件的。

### 构建github项目

构建如图所示仓库，仓库命名格式为`xxx.github.io` 这个xxx为你的账户名称就是途中左边那个wjlin0(要依据你的名字来哈)，我这里构建过了所以 爆红了。

![image-20221129224035267](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129224035267.png)

### 上传静态文件

```
cd .\_book\
git init
git add *
git commit -m "New commit"
git branch -M main
git remote add origin https://github.com/wjlin0/wjlin0.github.io.git
git branch --set-upstream-to=origin/main main
git push origin main
```

### github page 构建

![image-20221129233842493](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129233842493.png)

![image-20221129233855821](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129233855821.png)

等待完成即可

### 配置自定义域

> 没有域名 或者无需配置自定义域名可忽略这一步

选择右上角 settings

![image-20221129234000275](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129234000275.png)

选择Pages -> Add a domain

![image-20221129234013450](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129234013450.png)

选择 Add domain

![image-20221129234122642](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129234122642.png)

![image-20221129234152977](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129234152977.png)

在自己的DNS服务商做DNS TXT 解析 ，做完之后点击 Verify。回到仓库位置，选择 Custom domain，输入你刚刚自定义的域名，再点击保存。

![image-20221129234338700](image/gitbook%E6%90%AD%E5%BB%BA%E8%BF%87%E7%A8%8B/image-20221129234338700.png)

### 访问

保存完之后  DNS check successful 通过之后 ，访问域名即可

> https://wjlin0.github.io 或者 https://book.wjlin0.com

## 更新文件

### 导出 git

更新之前将之前 .git 导入出来

```
mv ./_book/.git ./
```

### 更新目录

```
cd docs && book sm && cd ../
```

### 构建静态文件



```
gitbook install # 若修改了book.json，则需要重新下载
gitbook build
mv  .git ./_book/
```

### 提交更新后的代码

```powershell
### powershell的用法
cd ./_book
git pull
git add .
$A = Get-Date;git commit -m "$A";
git push
```

或者 你可以这样

```cmd
### cmd的用法
cd ./_book
git pull
git add .
git commit -m "%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%: %time:~3,2%"
git push
```

### 更新脚本

`update.bat`

```bat
@echo on
C:\Users\TZ\.gitbook\versions\3.2.3\node_modules\.bin\npm.cmd config set registry=http://registry.npmjs.org && cd /d %~dp0 && attrib -h ./_book/.git && move ./_book/.git ./ && cd docs  && book sm && cd ../ && gitbook install && gitbook build && move .git ./_book/ && attrib +h ./_book/.git && cd ./_book && git pull && git add . && git commit -m "%date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,2%: %time:~3,2%" && git push
pause
```



