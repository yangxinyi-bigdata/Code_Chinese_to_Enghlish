
主要由两部分构成, 
"cells": 里面是一个列表, 列表里面的每一个元素都是字典格式, 代表一个cell.

cell里面有 cell_type:
code, "cell_type": "markdown", "cell_type": "raw",
这三种格式.

source: 单元格的内容，是一个字符串列表。

execution_count: （仅适用于代码单元格）记录了代码单元格被执行的顺序。

outputs: （仅适用于代码单元格）记录了执行代码后的输出，包括标准输出、错误消息等。

metadata: 包含了一些 notebook 的元数据，比如使用的 kernel 规格、语言信息等。

翻译思路: 

所以基本上我只需要翻译 source 里面的内容就可以了.
