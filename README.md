# Code_Chinese_to_Enghlish
我有一个梦想, 能够使用中文顺畅的开发Python, 却不会影响到正常工作. 写于 2024年3月1日 17:34分, 这个梦想有可能实现吗?

所以我现在的想法是, 开发这样一个工具, 自动从中文代码中提取出中文变量, 自动翻译成英文变量, 同时保存一个变量库, 保证每次翻译结果是稳定的.
再生成一个同功能的英文代码, 这样就可以实现, 写的时候是中文变量, 需要和其他人合作的时候, 提交给其他人看的时候, 就是一个标准的英文开发代码!

我觉得这是一个很好的梦想.

### 20240730 项目描述: 

使用中文编程, 本项目旨在将中文编程的代码自动翻译成英文.

且通过建立翻译词组映射关系的库, 来保证每次翻译的一致性和稳定性.

从而能够让我们在日常编程中使用中文进行变量命名, 并且在需要的时候可以将代码转换成英文版本, 方便工作需要.

现有一个历史变量库, 变量替换的时候, 先从本地历史变量库中进行匹配, 如果匹配不到再联网进行翻译, 并保存到变量库当中.

### 20240731 笔记:
思路, 现在应该做的是一个功能规划, 拆分.
1. 首先分析在里面都有哪些元素, 如何提取出中文变量(函数名, 类名), 提取出注释, 提取出符号等等.
    1.1 成功识别出各种元素之后, 其他的就非常简单了. 只需要用翻译接口, 或者是大模型接口, 对变量进行翻译. 然后进行替换就OK了.
2. 首先变量识别和提取. 对于替换的话, 如果直接采用 replace是否可以呢? 应该是不行, 如果一个变量名称中的一部分是另外一个变量很容易搞出问题.
3. 所以对于每个变量, 采用一个坐标的方式, 就是行数, 再加上位置. 基本上就可以定位到任何一个位置.

gpt提取变量的思路, 就是如果存在某一个变量, 那么这个变量一定是被定义过的.
但是如果是从外部引入的变量, 这种方法就不行了.
a = 5

code = re.sub(r'\b' + re.escape(var) + r'\b', translation_dict[var], code)

好的, 这行代码看起来非常有价值, \b 代表匹配单词边界, re.escape(var) 代表 var里面的特殊字符都能够被当做普通字符处理.
这样就不怕一个变量包含另外一个变量了.

引入中文变量, 有这么几种可能性: 
1. 使用语法 张三 = 22
    1.1 这种已经匹配成功了, 看来进行替换也不是什么难事
2. 使用语法 import 张三, 使用语法 import pandas as 张三, from datetime import time as 时间
   2.1 这种看起来也不是非常困难, 只需要写正则表达式, 实在不行写python代码按照规则匹配, 肯定也能搞得定.
3. 还有函数名称替换, def 某个函数()  函数中的变量 def 某个函数(变量1, 变量2) class 类名称: 
4. 貌似上面的这几种都是有固定的语法的, 也就是说替换起来应该是非常简单的. 把这几种都实现了, 变量应该就都提取好了吧.
4. 还有别的变量的可能性吗? 貌似没有了啊, 就这么简单就提取出来了.

下一步骤就是批量替换
在import from import def class 这几种定义中, 都是非常简单的, 不需要正则表达式, 直接按行处理就可以了.

20240731 18:14 现在基本上变量提取没什么问题了.
下一步就是变量替换.
首先找一个库保存一下, 需要用到数据库吗? 好像有个本地配置文件就可以了啊.

连接哪个大模型呢? 如果用Chatgpt的话, 在本地没办法直接运行啊, 得在服务器中转一下.
这个好像不用大模型也可以, 还是用吧.
有没有别的大模型啊, 国内其他大模型, 应该难度都不是特别大, 甚至本地大模型.

我部署一个http服务, 然后请求http服务, 将变量名称传入进去, 然后在服务器中获取翻译结果.
最好还是用国内的服务吧.

prompt
下面是我在编程中使用的中文变量, 请帮助我翻译成对应的英文变量名称
对于英文请直接忽略, 对于中文变量, 请将中文和英文对接的结果使用JSON格式进行返回:
['init', 'self', '小说名称', '输入文件_路径', '输出文件_路径', '读取小说内容', 'self', '小说处理器_类']


{
  "小说名称": "novel_name",
  "输入文件_路径": "input_file_path",
  "输出文件_路径": "output_file_path",
  "读取小说内容": "read_novel_content",
  "小说处理器_类": "NovelProcessor_class"
}

所以说其实就是一个 key: value的格式对吧, 那我就用json格式保存吧.

# 写入数据
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# 读取数据
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


### 20240801:
现在就是三个函数分别提取三种变量.
然后调用大模型进行替换.

开发一个历史变量保存文件, 可以先检查文件是否存在, 如果不存在则创建文件, 然后读取该文件, 读入字典.
如果历史上已经存在过的变量, 则直接保存.


# 替换变量名
for var in variables:
    if var in translation_dict:
        code = re.sub(r'\b' + re.escape(var) + r'\b', translation_dict[var], code)

print(code)

### 20240801: 
"发送邮件": "send_email",
"发送邮箱": "send_email",
发现了一个小bug, 发送邮箱和发送邮件, 被翻译成了相同的英文, 导致出现了冲突.
这里虽然存在 发送邮箱 翻译不准确, 但是不得不防备以后还可能出现这种状况, 那么应该如何翻译呢? 

首先, 如果在一个代码变量中存在两个变量, 但是被翻译成一种英文.
其次, 如果在历史变量中存在A, 翻译成B. 然后又出现变量C, 也被翻译成了B.
这两种都有可能产生冲突.

对于第一种, 我没办法控制大模型的翻译结果, 只能在大模型翻译后, 自行检查是否存在重复的, 如果存在重复的, 
则将重复的收集起来发送给大模型进行修改.

然后再对修改后的结果替换原来的.

对于第二种, 首先历史变量检查时不会触发, 因为是新变量, 但是翻译后, 进行合并之后, 也是要进行检查.
所以两者是相同的, 都是要进行检查, 如果存在重复则重新修改.

20240801: 
发现了新的问题, 当import引用的是一个中文名称的py文件时, 这时候如果直接翻译成英文.
但是这个英文文件不存在, 就会出现错误.

应该将这个中文文件也关联性的进行处理, 调用该代码进行替换, 并且这个文件名称也应该保存到变量库当中去, 
保证两次替换的文件和代码中的变量可以替换成相同的值.

而且这个py文件当中的函数也会进行替换, 那么两者必须保证替换的是一致的才可以.
OK对了, 这个需要考虑啊.

也就是替换实际上不是一个文件的替换, 而是一系列关联性文件的整体替换, 才能保证替换成英文之后的代码可以正常运行.
有意思.


with open(merged_file_name, "w") as 文件:
这个和for
import
from 应该放在一起.
这个也需要处理


### 20240802: 
暂时能翻译的都翻译了, 
后面还有的就是关联文件翻译.
在翻译文件名称的时候, 将文件名称也保存到变量当中去, 保证翻译结果的统一.
import 通义千问大模型
提取出通义千问大模型, 找到通义千问大模型.py文件, 然后对这个文件进行翻译.
在这个文件当中, 也寻找import 中的其他中文文件, 如果是中文的, 则进行翻译, 如果是英文名称则不进行翻译.

如果在当前文件夹找不到, 或者当前项目当中找不到, 则说明不需要翻译.

### 20240804
今天终于来干点正事了, 我应该修改我的时间方面的思考啊, 如何让自己能够集中注意力干点有用的事情.
不能只通过工作这一件事来赚钱, 一定要在搞点别的事情啊!

梳理一下, 当前这个功能已经进展到什么程度了? 
对了

-[x] 引入logru记录日志, 别再用print打印了, 并不好用
-[x] 发现大模型会偷懒, 有的单词就跳过了, 没有进行翻译, 翻译之后再检查一遍是否所有的都返回了.

函数名称, function_argument_name = one

发现对于这种没有匹配上, 也就是说可以用多个变量, 解包一个多元素变量.

下面开发新的重量级功能, 关联翻译.
简单的地方是, 变量反正都统一存在一个文件里面.
直接从里面搜索就可以.
然后找到的文件名称, 

import 通义千问模型
这时候应该会对, 通义千问模型进行翻译.
那么就说明很可能在当前文件夹中存在一个 通义千问模型.py 的文件.
这时候就将 通义千问模型.py 添加到队列中.
当前文件翻译完成之后, 再对队列中的另外一个文件进行翻译.

import 通义千问模型
print(通义千问模型.__file__)

首先判断标题是否中文, 如果是中文, 则通过代码通义千问模型.__file__判断路径是否当前工作路径.

如果是当前工作路径, 则将该文件完整路径添加到队列当中去.
然后再次调用这个代码, 对该文件进行处理.
处理该文件过程中, 还会再出现import中的中文内容.

那么再次重复进行递归一直到队列中的所有元素被处理完成.

import 通义千问模型
from 测试大模型 import 翻译中文变量
import 豆包大模型 as 豆包, 月之暗面大模型 as 月之

总之只要import 后面的, from 后面的(如果有from就不看import了)都要单独提取出来成为文件.
然后判断是否中文, 如果中文再判断是否当前项目当中的.
如果是项目当中的, 就添加到队列当中, 进行后续处理.
当前代码处理完成之后, 则继续调用队列, 继续处理后面的代码.

这两种要对 通义千问模型, 豆包大模型 进行进一步处理.

新发现一个问题, 这里from A import B
A也可能是一个目录包含__init__.py
B是一个py代码.
这样的话, 其实a和b都是需要翻译的.
要判断是文件还是目录, 如果是目录, 则要进一步翻译B.


print(通义千问模型.__file__)
包还是代码文件可以用这个判断, 包的文件是__init__.py, 代码是 通义千问模型.py
/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/示例代码/__init__.py


/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/通义千问模型.py

如果是一个目录, 是否需要对目录下面的所有文件都进行翻译? 
是否需要创建一个新的目录? 
对, 肯定是需要创建一个新的目录.

判断如果是一个目录, 则递归对目录下面所有文件进行处理.
首先要在同一层级创建一个新的英文目录, 然后里面的所有文件应该都得处理吧? 还是只处理用到的文件呢? 
如果一个包太大了, 有几十个文件? 好像也没关系.

 './示例代码/novel_send/小说_发送_脚本.py',

/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Code_Chinese_to_Enghlish/示例代码/novel_send/小说_发送_脚本.py

这两个是相同的文件, 所以当获取到后面的这个, 就知道了是哪个文件, 然后添加到列表当中等待处理就可以了.

bug修复: 
def 遍历目录和文件列表(开始目录='.', 忽略目录=None)
之前在匹配的时候只考虑到了这种语法, 没考虑到函数还可以有默认值.
def 遍历目录和文件列表(开始目录, 忽略目录)

### 20240807:
-[x] 对文件名称进行翻译之后, 也保存到整个变量列表当中去.

发现还是直接一步到位吧, 直接遍历整个项目进行翻译.
使用文件翻译的时候, 将文件翻译结果也添加到变量json里面去, 保证翻译的一致性.

我到时候翻译的应该是另外一个中文的项目, 而不是翻译自己. 那么 "已保存变量.json" 这个文件到底是保存到自己这里, 还是项目那边?
为了保证一致性, 应该是保存到自己这里, 不能污染原来的项目, 对.

既然指定了要翻译的项目, 那么就应该直接指定项目的根路径, 然后从根路径开始进行遍历.

/Users/yangxinyi/Library/CloudStorage/OneDrive-个人/100_code/Test_Translate_Project

### 20240809: 

翻译内置变量的进程, 发现存在问题, 当使用隐式方法定义变量类型的时候, 例如 b = "666", 这种b的类型默认是str, 是没办法
变成我设置的 "字符串" 类型的, 也就是说除非我手动再添加一层设置, 否则使用不了.

暂时停止这个工作, 还是专心把项目翻译先搞完再说别的.

项目翻译, 看一下项目翻译到底怎么搞吧.
获取了目录列表之后, 依次判断, 目录是否包含中文
如果包含中文, 则在同一层级创建一个翻译英文目录
如果是多层级文件夹, 应该先从上级文件夹开始遍历, 创建上级文件夹, 然后对于下级文件夹, 找到对应的上级英文文件夹, 再去创建子文件夹.

OK, 思路很明确, 开始写代码吧.

### 20240811

首先从父层级一层一个往下面改, 这样可以保证, 每一层级, 当前层级处理完成之后, 当前层级就全是英文了, 
然后所有文件已经复制了一份到英文文件夹当中.
后面就处理这个子文件夹就可以了, 

子文件夹再判断其中的目录名是否存在中文, 如果存在中文的, 则在同一层级, 创建一个英文目录, 然后将中文目录中的所有内容复制过去.

然后如果这个上一层级已经有过复制了, 那么就将中文目录直接删除掉.
如果这个上层目录没有过复制记录, 那么就保留中文的目录.

遍历的逻辑是先遍历当前层级A, 获取一个下一层级B, 再获取一个B中的子目录C, 遍历C中的所有子目录D
一直到B中的所有遍历完成.
在提取下一个一级子目录K

### 20240813
今天干啥呢?
赶紧走核心流程吧, 文件夹翻译已经完成了, 接下来是文件的翻译.

- [x] 下面这种变量没提取成功.
def 传入大模型返回JSON(messages: List[Dict[str, str]]) -> Dict[str, str]:
for 目录路径, 目录列表, 文件列表 in os.walk(start_directory):

- [x] 未替换成功内容: directory_mapping_dict = tongyi_qianwen_model.翻译文件名(chinese_variable)
文件名前缀_翻译字典 = 通义千问模型.翻译文件名(文件名前缀)
分析: 通义千问模型 是 import 进来的, 文件名前缀_翻译字典 是提取的变量.
所以 翻译文件名, 这个实际上没有被提取出来.
但是如果提取所有的 xxx.xxx 会把 pd.DataFrame 中的DataFrame也给提取出来.
xxx.xxx 如果是中文则需要翻译, 如果是英文, 则不需要翻译. 应该是这样的逻辑.
不可能按照代码特征统一匹配, 然后全部替换, 也不是不可以.
能不能按照import后面的变量进行提取呢? 也不能
from 翻译工具 import 通义千问模型
from 内置变量 import *
对于星号匹配的号码, 并没有显示的导入, 所以我也不知道到底导入了哪个变量.
那么只能通过代码的特征去进行匹配.

正常来讲, 在代码都匹配完成之后, 代码部分中, 除了字符串, 是不应该存在中文的, 如果说一个代码替换完成了, 
发现还是存在中文, 那么就是说没有替换完成, 应该对剩余的进行替换.
直接按照变量格式提取一个中文变量, 也可能是中英文混合的变量, 

发现了一个似乎是更好的替换方案, 代码会从前往后进行替换, 如果匹配上注释的就不会再匹配其他的.
如果匹配上单行字符串或者多行字符串, 就不会再往后匹配.
然后最后匹配包含有中文的变量: 
```# 匹配注释部分
注释匹配模式 = r'(#.*?)\n'
字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\".*?\"|\'.*?\')'
# 修改为跨行匹配模式
多行字符串匹配模式 = r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\')'
变量匹配模式 = r'\b(\w*[\u4e00-\u9fff]+\w*)\b'

# 合并所有模式
综合匹配模式 = 注释匹配模式 + r'|' + 多行字符串匹配模式 + r'|' + 字符串匹配模式 + r'|' + 变量匹配模式

re.findall(综合匹配模式, 代码文本, flags=re.DOTALL)
```

- [x] 问题: 字符串中的内容被替换问题

首先思考清楚, 到底是提取变量的时候也避过去字符串当中的内容, 还是说替换的时候才避过去.
反正不管怎么样, 替换的时候肯定是要避过去的. 先把这个完整吧.

已保存变量_路径 = "已保存变量.json" 
在这行代码中, 已保存变量 是一个变量名称, 替换的时候, 会导致这个字符串中的一部分也被替换掉了.

代码
f = ["数据", "数据2", "这种"]
如果数据也是一个变量, 那么数据也会被替换掉
f2 = "数据4"

如果数据4是一个变量, 那么数据4会被替换掉, 所以"数据4" '数据4' with open("数据4") 
所以字符串可能出现在任何地方, 只能在替换的时候, 判断, 如果内容出现在 双引号, 单引号, 三个双引号, 三个单引号
当中的内容, 都不能进行替换. 因为可能会改变原来代码的功能.



""""""  '''''' 对于这两种字符串中的内容, 应该是不进行替换的, 当前会对其中的内容也进行替换.
"" 这里面的内容, 也会进行替换.
提取变量的时候, 提取出来也无所谓, 只能在替换的时候, 判断如果是处于字符串当中的数据, 那么不进行替换.



对于py文件, 三种情况应该都有, 有在根目录的, 有在中文目录的, 有在英文目录的, 有在中文套中文套中文目录.
有在中文套英文套英文, 或者中文套中文套英文, 中文套


文件翻译思路: 
1. 首先根文件夹的文件, 处理方式是直接在原目录中翻译成英文文件, 源文件保留.
2. 中文文件夹里面的py文件, 应该已经随文件夹复制到英文文件夹里面了. 翻译方式是英文目录直接翻译成英文文件, 而且应该把复制的中文py文件删除掉.
3. 英文文件夹里面的py文件, 这种应该还没动, 处理方式是直接在原目录中翻译成英文文件, 源文件保留.

直接翻译文件的功能, 我应该已经有了

#Todo
思路2: 
在当前项目中创建一个空文件夹, 把整个翻译的项目结果都放到里面去.
优点: 可以创建一个纯净的英文项目, 不必再和原来的中文项目混合到一起, 但是对比起来没有那么方便.
也可以在同一层级创建一个文件夹, 翻译结果放进去.
还是两种都试一下吧.


### 20240815

- [x] 测试代码.py, 同样的一个文件, 在两个文件夹中都存在, 那么这两个翻译是否会产生冲突呢? 

- [x] 同样的, 如果是出现相同的目录, 后面的也会将前面的覆盖掉

如果是用其他的值作为key, 
会更好一些, 如果是用完整路径作为key, 好像有点累赘
还是用列表保存吧, 只需要依次保存就可以了, 或者是用数字作为唯一标识符, 这样后面还能对的上.
列表的话, 就很难和原来的未过滤之前的全部列表对应上了.

对, 用数字编码, 也就相当于是ID, 这样更好一些, 所以我从一开始就使用pd的话, 是不是就没这么多事了.
- [x] 现在的问题是, 在新建的英文文件夹当中, 原来的中文文件并没有被删除.
一个问题一个问题解决吧.


- [x] 内置变量文件夹中原来的中文代码没有删除掉.
- 搞一下这个吧, 
小说_发送_脚本.py, 这个代码在 '/示例代码/novel_send'
但是因为我上面目录只处理了中文目录, 导致这个里面没有英文目录


- [x] 内置变量对应的built_in_variable 的 __init__ 翻译之后, 因为其中引入的变量, 在实际代码中翻译成英文了, 但是字符串的变量没有变化, 导致出错.
__init__ 因为是python中的固定规定, 不能改成中文.
当这个文件存在的时候, 有两种可能, 一种是中文文件夹. 那么中文文件夹会被复制成英文文件夹, 这个文件被复制过去.
如果是复制过去的话, 那么应该将其中的中文翻译成英文.

如果是本来就在英文文件夹呢? 也应该翻译.
就是说如果是在中文文件夹当中, 应该不进行任何处理.
如果是在英文文件夹中, 有两种可能, 一种是本来就在这.
一种是从中文文件夹复制过来的.
可以直接进行翻译.

根据上层路径, 判断是否存在于中文文件夹当中, 如果在中文文件夹当中, 则不进行处理.
如果是在英文文件夹当中, 则进行翻译.

- [x] 这个文件翻译之后没有进行删除, 应该也是因为英文文件夹的原因, 应该记录一下, 只有上层某一层文件夹曾经复制过, 那么所有翻译之后原文件, 都不应该保留了.
/Users/yangxinyi/Downloads/200_临时文件夹/Test_Project_V3/example/novel_send/小说_发送_脚本_测试1.py

只需要判断一个目录是否有对应的中文目录就可以了, 如果有对应的中文目录, 那么一定是复制品, 里面的文件不需要保留.
如果没有对应的中文目录, 那么应该保留.

通过映射关系来判断似乎效果非常不错, 每个中文文件夹都必定有一个对应的英文文件夹, 如果说一个英文文件夹存在映射中文文件夹, 那么说明它是衍生的, 则里面的中文代码直接替换.
如果说是原生的, 那么翻译并保留原来的.
即使是多层的, 只要是中文文件夹, 一定有对应的英文文件夹.
如果是英文文件夹, 那么只要父目录中存在中文, 一定有对应的衍生文件夹.

- [x] 现在好像还没考虑到这种情况: 对于曾经翻译过的代码, 应该如何处理呢? 当我第二次运行的时候, 应该是用新翻译过来的英文代码替代原来的英文代码.
那么首先, 如果说当翻译一个中文文件的时候, 显示对应的英文文件已经存在了, 应该继续翻译, 将原来的覆盖掉.
通过处理上面的问题, 顺便将这个问题也处理完成了.

- [x] 翻译整个项目到新的位置, 可能这个才是正道, 反正两个功能都保留吧, 用这个翻译功能,
逻辑顺序: 首先翻译对应项目名称, 任何将整个项目内容复制到新位置.
然后在新位置中对所有文件夹进行翻译, 如果是中文文件夹, 就复制一个英文的, 将原来中文的删除掉.
和当前的复制有什么区别吗? 当前的是翻译了英文的之后, 原来的中文还要保留.
而新项目是翻译了之后, 原来的中文应该删除掉.

- [x] 一个测试的项目文件夹, 应该包含各种各样的条件,
目录中应该有 中文目录, 包含英文py文件, 包含中文py文件, 包含中文子文件夹, 包含英文子文件夹.
目录的中文子目录中又包含, 以上几种不同的.
目录的英文子目录中又包含, 以上几种不同的.

### 20240817
今天的目标是? 

- [x] 翻译 jupyter文件
完成了, 没想到这么简单.

- [x] 项目翻译-但是创建创建一个新的项目, 而不是将两个前后翻译的混合在一起.
今天的目标就是这个吧, 但是目标不是完成, 因为这个任务的难度现在还没有什么真正的预估, 预估两三天应该差不多能完成.
思路: 
首先, 如果原来的项目就是英文的话, 再来一个, 如果不传递名称, 有点没法搞, 不知道应该传递到哪里.
所以这个项目名称还是手动给一个名称, 或者说绝对路径, 对给一个绝对路径吧.
复制_绝对路径 = ""
步骤: 
1. 将当前项目中的所有文件, 复制一份到新的文件夹里面去
2. 文件夹修改, 将所有中文文件夹, 修改成英文文件夹.
   这个当前的函数功能.
3. py文件修改, 将所有py文件, 翻译成英文文件, 然后删除原来的中文文件.
唯一要思考的就是, 对于其他数据文件, 配置文件, 这些要不要翻译.
如果也进行翻译的话, 就需要在py代码里面进行替换, 一般来说都是路径, 也就是字符串里面进行替换, 有没有其他可能性呢? 
保存在数据库里面? 或者其他的可能性, 暂定不进行替换.

- [x] 将英文项目翻译成中文项目, 逆反天罡.
这个可以的, 我就用这个开发吧, 如果是打包的话, 需要保证对方电脑中有对应的环境吗? 应该不需要吧, 但是需要打包整个python的解释器, 可能.
是不是直接给大家提供翻译的API会更好一些?

- [x] 操作页面开发

- [x] 项目打包
项目如何运行呢? 最好是web的形式吧, 如果开发成一个网站, 当然可以. 或者一个非常简单的页面.
在本地运行一个flask服务器, 然后web端访问flask服务器工作? 


后端直接在本地启动一个http, 然后和python中的代码进行交互就可以了是吧.
python翻译结果直接把数据对接会web前端就可以了.



- [x] 我觉得现在搞的这个日志匹配的项目好像可以用作这个










