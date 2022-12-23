# SQL注入

## 介绍

SQL是操作[数据库](https://baike.baidu.com/item/数据库/103728?fromModule=lemma_inlink)数据的结构化查询语言，网页的应用数据和后台数据库中的数据进行交互时会采用SQL。而SQL注入是将Web页面的原[URL](https://baike.baidu.com/item/URL/110640?fromModule=lemma_inlink)、表单域或数据包输入的参数，修改拼接成SQL语句，传递给Web服务器，进而传给[数据库服务器](https://baike.baidu.com/item/数据库服务器/613818?fromModule=lemma_inlink)以执行数据库命令。如Web应用程序的开发人员对用户所输入的数据或cookie等内容不进行过滤或验证(即存在注入点)就直接传输给数据库，就可能导致拼接的SQL被执行，获取对数据库的信息以及提权，发生[SQL注入攻击](https://baike.baidu.com/item/SQL注入攻击/4766224?fromModule=lemma_inlink)。

## 产生原因

SQL注入产生的原因是网站应用程序在编写时未对用户提交至服务器的数据进行合法性校验（类型、长度、业务参数合法性、敏感字符等），同时没有对用户输入数据进行有效地特殊字符过滤，使得用户的输入直接带入数据库执行，超出了SQL语句原来设计的预期结果，导致了SQL注入漏洞。

## 注入举例

> 通过万能密码的举例，来简单讲解SQL注入

```php
<?php
$conn = mysqli_connect($servername, $username, $password, $dbname);
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}
$username = @$_POST['username'];
$password = @$_POST['password'];
$sql = "select * from users where username = '$username' and password='$password';";
$rs = mysqli_query($conn,$sql);
if($rs->fetch_row()){
    echo "success";
}else{
    echo "fail";
}
```

用户名`username`和密码`password`均来自于用户的直接传入，无任何过滤，后直接拼接到SQL语句中。

正常用户登录是，正常sql语句为：

```sql
select * from users where username = 'admin' and password='password'
```

攻击者带恶意的SQL语句输入的用户名为`admin`，密码为`123' or 1 = 1 --+ `，因为 1=1 永真，所以也就会登录成功

## 应用场景

**SQL注入漏洞可能出现在一切与数据库交互的地方**，常见举例如下（主要还是存在于**增删改查**四个字上）：

> 简而言之：所有和数据库交互的点均可能存在SQL注入

| 关键字 | 功能举例                         |
| :----- | :------------------------------- |
| 增     | 注册新用户、创建订单、添加文章…… |
| 删     | 删除用户、删除订单……             |
| 改     | 修改订单、更新用户信息……         |
| 查     | 查询信息、筛选订单、搜索文章……   |

## 关系、非关系数据库

### 关系型数据库（SQL）

#### 什么是（SQL）关系型数据库

>  关系型数据库指的是使用关系模型（二维表格模型）来组织数据的数据库。 

#### 什么是关系模型

>  关系模型可以简单理解为二维表格模型，而一个关系型数据库就是由二维表及其之间的关系组成的一个数据组织。 

#### 常见关系型数据库管理系统([ORDBMS](https://baike.baidu.com/item/ORDBMS/870762))

1.  Oracle 
2.  MySql 
3.  Microsoft SQL Server 
4.  SQLite 
5.  PostgreSQL 
6.  IBM DB2 

#### 关系型数据库的优势

1.  采用二维表结构非常贴近正常开发逻辑（关系型数据模型相对层次型数据模型和网状型数据模型等其他模型来说更容易理解）； 
2.  支持通用的SQL（结构化查询语言）语句； 
3.  丰富的完整性大大减少了数据冗余和数据不一致的问题。并且全部由表结构组成，文件格式一致； 
4.  可以用SQL句子多个表之间做非常繁杂的查询； 
5.  关系型数据库提供对事务的支持，能保证系统中事务的正确执行，同时提供事务的恢复、回滚、并发控制和死锁问题的解决。 
6.  数据存储在磁盘中，安全可靠。 

#### 关系型数据库的劣势

>  **随着互联网企业的不断发展，数据日益增多，因此关系型数据库面对海量的数据会存在很多的不足。** 

1.  高并发读写能力差：网站类用户的并发性访问非常高，而一台数据库的最大连接数有限，且硬盘 I/O 有限，不能满足很多人同时连接。 
2.  海量数据情况下读写效率低：对[大数据](https://cloud.tencent.com/solution/bigdata?from=10680)量的表进行读写操作时，需要等待较长的时间等待响应。 
3.  可扩展性不足：不像web server和app server那样简单的添加硬件和服务节点来拓展性能和负荷工作能力。 
4.  数据模型灵活度低：关系型数据库的数据模型定义严格，无法快速容纳新的数据类型（需要提前知道需要存储什么样类型的数据）。 

### 非关系型数据库（NOSQL）

#### 什么是（NOSQL）非关系型数据库：

>  非关系型数据库又被称为 NoSQL（Not Only SQL )，意为不仅仅是 SQL。通常指数据以对象的形式存储在数据库中，而对象之间的关系通过每个对象自身的属性来决定，常用于存储非结构化的数据。 

#### 常见的NOSQL数据库

1.  键值数据库：Redis、Memcached、Riak 
2.  列族数据库：Bigtable、[HBase](https://cloud.tencent.com/product/hbase?from=10680)、Cassandra 
3.  文档数据库：MongoDB、CouchDB、MarkLogic 
4.  图形数据库：Neo4j、InfoGrid 

#### 非关系型数据库的优势

1.  非关系型数据库存储数据的格式可以是 key-value 形式、文档形式、图片形式等。使用灵活，应用场景广泛，而关系型数据库则只支持基础类型。 
2.  速度快，效率高。 NoSQL 可以使用硬盘或者随机存储器作为载体，而关系型数据库只能使用硬盘。 
3.  海量数据的维护和处理非常轻松，成本低。 
4.  非关系型数据库具有扩展简单、高并发、高稳定性、成本低廉的优势。 
5.  可以实现数据的分布式处理。 

#### 非关系型数据库的劣势

1.  非关系型数据库暂时不提供 SQL 支持，学习和使用成本较高。 
2.  非关系数据库没有事务处理，无法保证数据的完整性和安全性。适合处理海量数据，但是不一定安全。 
3.  功能没有关系型数据库完善。 
4.  复杂表关联查询不容易实现。

##  漏洞危害

1. 获取数据库访问权限，甚至获得DBA权限，从而获取数据库中的所有数据，造成信息泄漏；（**可获取数据**）
2. 对数据库的数据进行增加、删除、修改操作，例如删除数据库中重要数据的表（**可进行增删改操作**）
3. 通过构造特殊的数据库语句，可操作数据库进入后台或者插入木马，以获取整个网站和数据库的控制权限，篡改网页，发布不良信息等；（**可获取网站权限**）
4. 获取服务器最高权限，远程控制服务器，甚至导致局域网(内网)被入侵；（**可获取服务器权限**）

## 修复建议

### 代码层面

#### 输入过滤（正则过滤）

1. 严格控制输入数据的类型；如通过id获取用户信息时，仅允许传入的id为整型
2. 严格控制输入数据的长度；如限制用户名长度应小于20
3. 输入合法性判断；禁止出现一些特殊字符或关键词，如`'`，`"`，`\`，`<`，`>`，`&`，`*`，`;`，`#`，`select`，`from`，`where`，`sub`，`if`，`union`，`sleep`，`and`，`or`等
4. 对所有可能的输入点进行判断检测，如UA、IP、Cookie等

####  预编译SQL语句(参数化查询)

参数化查询是一种查询类型，其中占位符用于填充参数，参数值在执行时提供。原理是采用了预编译的方法，先将SQL语句中可被用户控制的参数集进行编译，生成对应的临时变量集，再使用对应的设置方法，为临时变量集里面的元素进行赋值，赋值过程中会对传入的参数进行强制类型检查和安全检查。

所有与数据库交互的业务接口均采用参数化查询，参数化的语句使用参数而不是将用户输入变量直接嵌入到SQL语句中，参数化查询是防御SQL注入的最佳方法，比如：Java中的`PreparedStatement`，PHP中的`PDO`等。

##### 预编译以及原理

预编译是指在创建数据库对象时就将指定的SQL语句编译完成，这时SQL语句已经被`解析、审查`，所以相对传统的执行方式(每处理一个SQL语句就要解析SQL语句、检查语法和语义)，预编译方式在执行数据插入、更新或者删除操作的时候，执行效率更高。

`为什么预编译能让传入的数据只能是数据，它的底层原理是怎样的？`

通常来说，一条SQL语句从传入到运行经历了生成`语法树、执行计划优化、执行`这几个阶段。在预编译过程中，数据库首先接收到带有预编译占位符`?`的SQL语句，解析`生成语法树(Lex)`，并缓存在`cache`中，然后接收对应的参数信息，从`cache`中取出语法树设置参数，然后再进行优化和执行。由于参数信息传入前语法树就已生成，执行的语法结构也就无法因参数而改变，自然也就杜绝了SQL注入的出现.

##### PDO

PDO针对预编译提供了两种模式：本地预编译和模拟预编译。

模拟预编译：本身不是一种真正的预编译，它是为了兼容不支持预编译的数据库，将用户输入的参数进行转义，拼接到数据库，由`数据库正常解析执行`。所以它的`预编译` 操作是由pdo 完成的 数据库本身没有参与预编译 **并且这是PDO的默认模式**

##### 演示

1、开启MySQL日志，查看日志

```php
<?php
$hostname ='127.0.0.1';
$dbname='ctf';
$conn = new PDO( "mysql:host=$hostname;dbname=$dbname",'root','root123456');

//$sql = 'select * from admin where id =\''.$id.'\'';
$sql ="select * from admin where id =?";

$pdos = $conn ->prepare($sql);

$pdos->bindParam(1,$_GET['id']);
$pdos->execute();

var_dump($pdos->fetchAll());
```

```
2021-11-28T05:29:59.198823Z	    9 Connect	root@localhost on ctf using TCP/IP
2021-11-28T05:29:59.199095Z	    9 Query	select * from admin where id ='\''
2021-11-28T05:29:59.199806Z	    9 Quit	
```

如日志所示，mysql本身没有预编译操作，只有`连接`，`查询`，`关闭` 三个操作。

2、开启本地预编译模式

```php
<?php
$hostname ='127.0.0.1';
$dbname='ctf';
$conn = new PDO( "mysql:host=$hostname;dbname=$dbname",'root','root123456');
$conn -> setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
//$sql = 'select * from admin where id =\''.$id.'\'';
$sql ="select * from admin where id =?";

$pdos = $conn ->prepare($sql);

$pdos->bindParam(1,$_GET['id']);
$pdos->execute();

var_dump($pdos->fetchAll());
```

```
2021-11-28T05:36:24.438190Z	   10 Connect	root@localhost on ctf using TCP/IP
2021-11-28T05:36:24.439940Z	   10 Prepare	select * from admin where id =?
2021-11-28T05:36:24.440013Z	   10 Execute	select * from admin where id ='\''
2021-11-28T05:36:24.440433Z	   10 Close stmt	
2021-11-28T05:36:24.440474Z	   10 Quit	
```

如日志所示，整个流程分为五部 `连接`，`预编译`，`传入参数执行`，`关闭预编译语句`，`关闭数据库`

##### 0x04 危害

如果使用模拟预编译模式 ，则可能会导致出现`宽字节注入漏洞`,`二次注入漏洞`(之前文章写到)

1、[sql二次注入 - wjlin0](https://wjlin0.com/archives/sql二次注入)

2、[sql宽字节注入 - wjlin0](https://wjlin0.com/archives/sql宽字节注入)

##### 0x05 总结

1、本次了解mysql的预编译处理能够使用户传入的数据只能是数据，而预编译是提前生成**语法树** 使其用户不能改变原有的语法结构，从而预防了SQL注入的产生。

2、了解了PHP的PDO两种预编译模式  `本地预编译`，`模拟预编译` 后者只是由pdo代执行‘预编译操作‘ ，不能算真正意义上的预编译，就会出现`宽字节注入`和`二次注入`的风险。而PDO默认模式就是模拟预编译，所以再执行时，最好设置

```php
$PDO -> setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
```

3、同样的JAVA也存在类似的问题，以后学习后再补充。

###  数据库层面

#### 最小权限原则

遵循最小化权限原则，严格限制网站用户的数据库的操作权限，禁止将任何高权限帐户（sa，dba、root等）用于应用程序数据库访问，从而最大限度的减少注入攻击对数据库的危害。

#### 禁用敏感函数

防止攻击者通过SQL注入获取到除数据库外的其他更高权限，如系统权限等；

比如MSSQL中，拒绝用户访问敏感的系统存储过程，如`xp_dirtree`、`xp_cmdshell`等。

#### 权限控制

限制用户仅能够访问必须使用的数据库表。

#### 统一编码

网站与数据层的编码统一，建议全部使用UTF-8编码，避免因上下层编码不一致导致一些过滤模型被绕过，比如宽字节注入等。

### 其他层面

1. 网站应避免抛出SQL语句执行过程中的错误信息，如类型错误、字段不匹配等，防止攻击者利用这些错误信息进行一些判断；
2. 使用通用防注入系统，或者部署WAF等。

## 靶场

- [DVWA](https://github.com/digininja/DVWA)

- [sqli-labs](https://github.com/Audi-1/sqli-labs)

## 参考

- [深入理解SQL注入与预编译（下）_牛客博客 (nowcoder.net)](https://blog.nowcoder.net/n/be73b8f592504ae8b1d00368433061be)

- [SQL注入 · d4m1ts 知识库](https://blog.gm7.org/%E4%B8%AA%E4%BA%BA%E7%9F%A5%E8%AF%86%E5%BA%93/01.%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95/02.WEB%E6%BC%8F%E6%B4%9E/01.SQL%E6%B3%A8%E5%85%A5/)