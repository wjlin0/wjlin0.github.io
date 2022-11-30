# JAVA反序列化漏洞

## 概述

Java 提供了一种对象序列化的机制，该机制中，一个对象可以被表示为一个字节序列，该字节序列包括该对象的数据、有关对象的类型的信息和存储在对象中数据的类型。将序列化对象写入文件之后，可以从文件中读取出来，并且对它进行反序列化，也就是说，对象的类型信息、对象的数据，还有对象中的数据类型可以用来在内存中新建对象。整个过程都是 Java 虚拟机（JVM）独立的，也就是说，在一个平台上序列化的对象可以在另一个完全不同的平台上反序列化该对象。

* 1.序列化是指把一个Java对象变成二进制内容，本质上就是一个`byte[]`数组。

* 2.为什么要把Java对象序列化呢？因为序列化后可以把`byte[]`保存到文件中，或者把`byte[]`通过网络传输到远程，这样，就相当于把Java对象存储到文件或者通过网络传输出去了。
* 将序列化对象写入文件之后，可以从文件中读取出来，并且对它进行反序列化，即把一个二进制内容（也就是`byte[]`数组）变回Java对象。有了反序列化，保存到文件中的`byte[]`数组又可以“变回”Java对象，或者从网络上读取`byte[]`并把它“变回”Java对象。也就是说，对象的类型信息、对象的数据，还有对象中的数据类型可以用来在内存中新建对象。
* 整个过程都是 Java 虚拟机（JVM）独立的，也就是说，在一个平台上序列化的对象可以在另一个完全不同的平台上反序列化该对象。
* Java的序列化机制仅适用于Java，如果需要与其它语言交换数据，必须使用通用的序列化方法，例如JSON。

## 	成因

暴露或间接暴露反序列化 API ，导致用户可以操作传入数据，攻击者可以精心构造反序列化对象并执行恶意代码

两个或多个看似安全的模块在同一运行环境下，共同产生的安全问题 

## 实现序列化与反序列化

FileOutputStream

> new FileOutputStream 的时候，如果目标文件不存在，那么会先创建目标文件，然后再写入。(如果目标文件所在的文件夹不存在，则抛出异常)
>
> new FileOutputStream(file) 如果目标文件已经存在，那么会先清空 目标文件的数据，然后再写入新的数据.
>
> 写入数据的时候如果需要以追加的形式写入，那么需要使用new FileOutputStream(file,true) 这个构造函数。

FileInputStream

> java.io包的FileOutputStream类可用于将数据（以字节为单位）写入文件。

ObjectOutputStream

> 基本上，ObjectOutputStream使用类名和对象值对Java对象进行编码。 并且，因此生成相应的流。 此过程称为序列化。
>
> 这些转换后的流可以存储在文件中，并且可以在网络之间传输。
>
> **注意**：ObjectOutputStream类仅写入那些实现Serializable接口的对象。 这是因为对象在写入流时需要序列化

ObjectInputStream

> ObjectInputStream主要用于读取ObjectOutputStream写入的数据。
>
> 基本上，ObjectOutputStream将Java对象转换为相应的流。 这称为序列化。 这些转换后的流可以存储在文件中，也可以通过网络传输。
>
> 现在，如果需要读取这些对象，则将使用ObjectInputStream，它将把流转换回相应的对象。这称为反序列化。

```java
public class Ser {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        String hello_ser = "hello ser";
        ser(hello_ser);
        unser();
    }

    public static void ser(Object o) throws IOException {
        System.out.println("序列化开始");
        FileOutputStream fileOutputStream = new FileOutputStream("ser.bin");
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
        objectOutputStream.writeObject(o);
        objectOutputStream.close();
        System.out.println("序列化结束");
    }

    public static void unser() throws IOException, ClassNotFoundException {
        System.out.println("反序列化开始");
        FileInputStream fileInputStream = new FileInputStream("ser.bin");
        ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
        String o = (String) objectInputStream.readObject();
        System.out.println(o);
        System.out.println("反序列化结束");
    }

}

--------------------------------------
序列化开始
序列化结束
反序列化开始
hello ser
反序列化结束
--------------------------------------
```



## 序列化特征

![image-20221130224748718](image/JAVA%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/202211302250742.png-1)

中间那一栏是文件的十六进制显示，最右边是字符显示。这里需要注意的特征值就是16进制显示时的前32位：

**AC ED**：`STREAM_MAGIC`，声明使用了序列化协议，**从这里可以判断保存的内容是否为序列化数据。** （这是在黑盒挖掘反序列化漏洞很重要的一个点）

**00 05**：`STREAM_VERSION`，序列化协议版本。

## 恶意攻击

```
public class Person implements Serializable {
    public String name;
    public int age;

    public Person() {
    }

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    @Override
    public String toString() {
        return "Person{" +
                "name='" + name + '\'' +
                ", age=" + age +
                '}';
    }
    private void readObject(ObjectInputStream ois) throws IOException,ClassNotFoundException {
        ois.defaultReadObject();

        Runtime.getRuntime().exec("calc");
    }
}

public class Ser {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        Person wjlin0 = new Person("wjlin0", 22);
        ser(wjlin0);
        unser();
    }

    public static void ser(Object o) throws IOException {
        System.out.println("序列化开始");
        FileOutputStream fileOutputStream = new FileOutputStream("ser.bin");
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(fileOutputStream);
        objectOutputStream.writeObject(o);
        objectOutputStream.close();
        System.out.println("序列化结束");
    }

    public static void unser() throws IOException, ClassNotFoundException {
        System.out.println("反序列化开始");
        FileInputStream fileInputStream = new FileInputStream("ser.bin");
        ObjectInputStream objectInputStream = new ObjectInputStream(fileInputStream);
        Person o = (Person) objectInputStream.readObject();
        System.out.println(o);
        System.out.println("反序列化结束");
    }

}

```

![image-20221130230043565](image/JAVA%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/202212010019366.png-1)

如果程序员在重写readObject的时候调用了恶意的方法时，我们就可以调用反序列化的结果让它成功执行。例如图中的弹出计算器

## 攻击流程

1.寻找反序列化入口readObject()，查看序列对象是否可控。

2.寻找危险方法存在位置。利用同名类方法等手段持续调用，最终到危险放上。

## 总结

反序列化出现漏洞的原因，是程序员对序列化的接口暴露 ，并存在一些危险的类，可被序列化，最终导致 代码执行的情况。
