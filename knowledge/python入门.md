# Python 入门笔记

## 什么是 Python？
Python 是一种简单易学的编程语言，特别适合新手入门。
- 用**缩进**表示代码块，而不是花括号 {}
- 变量不需要声明类型
- 有海量的第三方库（别人写好的功能）

## 基础语法

### 打印输出
```python
print("Hello, World!")
```

### 变量
```python
name = "小明"      # 字符串
age = 18           # 整数
height = 1.75      # 小数
is_student = True  # 布尔值
```

### 条件判断
```python
if age >= 18:
    print("成年人")
else:
    print("未成年人")
```

### 循环
```python
# for 循环
for i in range(5):
    print(i)           # 输出 0,1,2,3,4

# while 循环
count = 0
while count < 3:
    print(count)
    count += 1
```

### 函数
```python
def greet(name):
    """打招呼的函数"""
    return f"你好，{name}！"

print(greet("小明"))   # 输出：你好，小明！
```

## 常用数据结构

### 列表（List）
```python
fruits = ["苹果", "香蕉", "橘子"]
fruits.append("葡萄")     # 添加
print(fruits[0])          # 访问第一个：苹果
```

### 字典（Dict）
```python
student = {
    "name": "小明",
    "age": 18,
    "score": 95
}
print(student["name"])    # 输出：小明
```

## 文件操作
```python
# 读取文件
with open("文件.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 写入文件
with open("输出.txt", "w", encoding="utf-8") as f:
    f.write("Hello!")
```

## 第三方库安装
```bash
pip install 库名
```
