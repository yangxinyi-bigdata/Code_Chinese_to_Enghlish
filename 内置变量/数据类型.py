
class 列表(list):
    def __init__(self, f):
        super().__init__(f)

    def 追加(self, *args, **kwargs): # real signature unknown
        """ Append object to the end of the list. """
        return super().append(*args, **kwargs)

    def 清空(self, *args, **kwargs): # real signature unknown
        """ Remove all items from list. """
        return super().clear(*args, **kwargs)

    def 复制(self, *args, **kwargs):  # real signature unknown
        """ Return a shallow copy of the list. """
        return super().clear(*args, **kwargs)

    def 计数(self, *args, **kwargs):  # real signature unknown
        """ Return number of occurrences of value. """
        return super().count(*args, **kwargs)

    def 扩展(self, *args, **kwargs):  # real signature unknown
        """ Extend list by appending elements from the iterable. """
        return super().extend(*args, **kwargs)

    def 索引(self, *args, **kwargs):  # real signature unknown
        """
        Return first index of value.

        Raises ValueError if the value is not present.
        """
        return super().extend(*args, **kwargs)

    def 插入(self, *args, **kwargs):  # real signature unknown
        """ Insert object before index. """
        return super().extend(*args, **kwargs)

    def 弹出(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        return super().pop(*args, **kwargs)

    def 移除(self, *args, **kwargs):  # real signature unknown
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        return super().remove(*args, **kwargs)

    def 翻转(self, *args, **kwargs):  # real signature unknown
        """ Reverse *IN PLACE*. """
        return super().remove(*args, **kwargs)

    def 排序(self, *args, **kwargs):  # real signature unknown
        """
        Sort the list in ascending order and return None.

        The sort is in-place (i.e. the list itself is modified) and stable (i.e. the
        order of two equal elements is maintained).

        If a key function is given, apply it once to each list item and sort them,
        ascending or descending, according to their function values.

        The reverse flag can be set to sort in descending order.
        """
        return super().sort(*args, **kwargs)


class 字典(dict):
    """
    字典() -> new empty dictionary
    字典(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    字典(iterable) -> new dictionary initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    字典(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)
    """

    def 清空(self):  # real signature unknown; restored from __doc__
        """ D.clear() -> None.  Remove all items from D. """
        super().clear()

    def 复制(self):  # real signature unknown; restored from __doc__
        """ D.copy() -> a shallow copy of D """
        super().copy()

    @staticmethod  # known case
    def 从键值创建(*args, **kwargs):  # real signature unknown
        """ Create a new dictionary with keys from iterable and values set to value. """
        super().copy(*args, **kwargs)

    def 获取(self, *args, **kwargs):  # real signature unknown
        """ Return the value for key if key is in the dictionary, else default. """
        return super().get(*args, **kwargs)

    def 元素对(self):  # real signature unknown; restored from __doc__
        """ D.items() -> a set-like object providing a view on D's items """
        return super().items()

    def 键序列(self):  # real signature unknown; restored from __doc__
        """ D.keys() -> a set-like object providing a view on D's keys """
        return super().keys()

    def 弹出(self, 键, 默认值=None):  # real signature unknown; restored from __doc__
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If the key is not found, return the default if given; otherwise,
        raise a KeyError.
        """
        return super().pop(键, 默认值)

    def 弹出元素对(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.
        Raises KeyError if the dict is empty.
        """
        return super().popitem()

    def 设置带默认值(self, *args, **kwargs):  # real signature unknown
        """
        如果 key 不在字典中，则插入 key 并以默认值作为value。
        如果键在字典中, 则返回对应的值, 否则返回默认值

        Insert key with a value of default if key is not in the dictionary.

        Return the value for key if key is in the dictionary, else default.
        """
        return super().setdefault(*args, **kwargs)

    def 更新(self, E=None, **F):  # known special case of dict.update
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        """
        return super().update(E, **F)

    def 值序列(self):  # real signature unknown; restored from __doc__
        """ D.values() -> an object providing a view on D's values """
        return super().values()


class 字符串(str):
    """
    str(object='') -> str
    str(bytes_or_buffer[, encoding[, errors]]) -> str

    Create a new string object from the given object. If encoding or
    errors is specified, then the object must expose a data buffer
    that will be decoded using the given encoding and error handler.
    Otherwise, returns the result of object.__str__() (if defined)
    or repr(object).
    encoding defaults to sys.getdefaultencoding().
    errors defaults to 'strict'.
    """

    def 大写化(self, *args, **kwargs):  # real signature unknown
        """
        返回字符串的大写版本。

        更具体地说，使第一个字符大写，其余字符小写。
        """
        return super().capitalize(*args, **kwargs)

    def 小写_专业(self, *args, **kwargs):  # real signature unknown
        """ 用于返回一个适合无视大小写比较的字符串版本。它类似于 lower 方法，但更加强大，因为它不仅转换所有大写字母为小写字母，还处理了一些特殊的大小写转换规则，使其在多语言环境下更加有效。

•	目的：返回一个字符串的版本，使其适合无视大小写的比较。

•	用法：casefold() 方法对字符串执行更广泛的大小写折叠转换，确保在进行无视大小写的比较时更准确。

示例

s = "Groß"

print(s.casefold())

# 输出: 'gross'

在这个例子中，德语字符 ß 被转换为 ss，这是大小写折叠的结果，而不仅仅是简单的小写转换。"""

        return super().casefold(*args, **kwargs)

    def center(self, *args, **kwargs):  # real signature unknown
        """
        Return a centered string of length width.

        Padding is done using the specified fill character (default is a space).
        """
        pass

    def count(self, sub, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.count(sub[, start[, end]]) -> int

        Return the number of non-overlapping occurrences of substring sub in
        string S[start:end].  Optional arguments start and end are
        interpreted as in slice notation.
        """
        return 0

    def encode(self, *args, **kwargs):  # real signature unknown
        """
        Encode the string using the codec registered for encoding.

          encoding
            The encoding in which to encode the string.
          errors
            The error handling scheme to use for encoding errors.
            The default is 'strict' meaning that encoding errors raise a
            UnicodeEncodeError.  Other possible values are 'ignore', 'replace' and
            'xmlcharrefreplace' as well as any other name registered with
            codecs.register_error that can handle UnicodeEncodeErrors.
        """
        pass

    def endswith(self, suffix, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.endswith(suffix[, start[, end]]) -> bool

        Return True if S ends with the specified suffix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        suffix can also be a tuple of strings to try.
        """
        return False

    def expandtabs(self, *args, **kwargs):  # real signature unknown
        """
        Return a copy where all tab characters are expanded using spaces.

        If tabsize is not given, a tab size of 8 characters is assumed.
        """
        pass

    def find(self, sub, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.find(sub[, start[, end]]) -> int

        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Return -1 on failure.
        """
        return 0

    def format(self, *args, **kwargs):  # known special case of str.format
        """
        S.format(*args, **kwargs) -> str

        Return a formatted version of S, using substitutions from args and kwargs.
        The substitutions are identified by braces ('{' and '}').
        """
        pass

    def format_map(self, mapping):  # real signature unknown; restored from __doc__
        """
        S.format_map(mapping) -> str

        Return a formatted version of S, using substitutions from mapping.
        The substitutions are identified by braces ('{' and '}').
        """
        return ""

    def index(self, sub, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.index(sub[, start[, end]]) -> int

        Return the lowest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Raises ValueError when the substring is not found.
        """
        return 0

    def isalnum(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is an alpha-numeric string, False otherwise.

        A string is alpha-numeric if all characters in the string are alpha-numeric and
        there is at least one character in the string.
        """
        pass

    def isalpha(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is an alphabetic string, False otherwise.

        A string is alphabetic if all characters in the string are alphabetic and there
        is at least one character in the string.
        """
        pass

    def isascii(self, *args, **kwargs):  # real signature unknown
        """
        Return True if all characters in the string are ASCII, False otherwise.

        ASCII characters have code points in the range U+0000-U+007F.
        Empty string is ASCII too.
        """
        pass

    def isdecimal(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a decimal string, False otherwise.

        A string is a decimal string if all characters in the string are decimal and
        there is at least one character in the string.
        """
        pass

    def isdigit(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a digit string, False otherwise.

        A string is a digit string if all characters in the string are digits and there
        is at least one character in the string.
        """
        pass

    def isidentifier(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a valid Python identifier, False otherwise.

        Call keyword.iskeyword(s) to test whether string s is a reserved identifier,
        such as "def" or "class".
        """
        pass

    def islower(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a lowercase string, False otherwise.

        A string is lowercase if all cased characters in the string are lowercase and
        there is at least one cased character in the string.
        """
        pass

    def isnumeric(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a numeric string, False otherwise.

        A string is numeric if all characters in the string are numeric and there is at
        least one character in the string.
        """
        pass

    def isprintable(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is printable, False otherwise.

        A string is printable if all of its characters are considered printable in
        repr() or if it is empty.
        """
        pass

    def isspace(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a whitespace string, False otherwise.

        A string is whitespace if all characters in the string are whitespace and there
        is at least one character in the string.
        """
        pass

    def istitle(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is a title-cased string, False otherwise.

        In a title-cased string, upper- and title-case characters may only
        follow uncased characters and lowercase characters only cased ones.
        """
        pass

    def isupper(self, *args, **kwargs):  # real signature unknown
        """
        Return True if the string is an uppercase string, False otherwise.

        A string is uppercase if all cased characters in the string are uppercase and
        there is at least one cased character in the string.
        """
        pass

    def join(self, ab=None, pq=None, rs=None):  # real signature unknown; restored from __doc__
        """
        Concatenate any number of strings.

        The string whose method is called is inserted in between each given string.
        The result is returned as a new string.

        Example: '.'.join(['ab', 'pq', 'rs']) -> 'ab.pq.rs'
        """
        pass

    def ljust(self, *args, **kwargs):  # real signature unknown
        """
        Return a left-justified string of length width.

        Padding is done using the specified fill character (default is a space).
        """
        pass

    def lower(self, *args, **kwargs):  # real signature unknown
        """ Return a copy of the string converted to lowercase. """
        pass

    def lstrip(self, *args, **kwargs):  # real signature unknown
        """
        Return a copy of the string with leading whitespace removed.

        If chars is given and not None, remove characters in chars instead.
        """
        pass

    def maketrans(self, *args, **kwargs):  # real signature unknown
        """
        Return a translation table usable for str.translate().

        If there is only one argument, it must be a dictionary mapping Unicode
        ordinals (integers) or characters to Unicode ordinals, strings or None.
        Character keys will be then converted to ordinals.
        If there are two arguments, they must be strings of equal length, and
        in the resulting dictionary, each character in x will be mapped to the
        character at the same position in y. If there is a third argument, it
        must be a string, whose characters will be mapped to None in the result.
        """
        pass

    def partition(self, *args, **kwargs):  # real signature unknown
        """
        Partition the string into three parts using the given separator.

        This will search for the separator in the string.  If the separator is found,
        returns a 3-tuple containing the part before the separator, the separator
        itself, and the part after it.

        If the separator is not found, returns a 3-tuple containing the original string
        and two empty strings.
        """
        pass

    def removeprefix(self, *args, **kwargs):  # real signature unknown
        """
        Return a str with the given prefix string removed if present.

        If the string starts with the prefix string, return string[len(prefix):].
        Otherwise, return a copy of the original string.
        """
        pass

    def removesuffix(self, *args, **kwargs):  # real signature unknown
        """
        Return a str with the given suffix string removed if present.

        If the string ends with the suffix string and that suffix is not empty,
        return string[:-len(suffix)]. Otherwise, return a copy of the original
        string.
        """
        pass

    def replace(self, *args, **kwargs):  # real signature unknown
        """
        Return a copy with all occurrences of substring old replaced by new.

          count
            Maximum number of occurrences to replace.
            -1 (the default value) means replace all occurrences.

        If the optional argument count is given, only the first count occurrences are
        replaced.
        """
        pass

    def rfind(self, sub, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.rfind(sub[, start[, end]]) -> int

        Return the highest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Return -1 on failure.
        """
        return 0

    def rindex(self, sub, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.rindex(sub[, start[, end]]) -> int

        Return the highest index in S where substring sub is found,
        such that sub is contained within S[start:end].  Optional
        arguments start and end are interpreted as in slice notation.

        Raises ValueError when the substring is not found.
        """
        return 0

    def rjust(self, *args, **kwargs):  # real signature unknown
        """
        Return a right-justified string of length width.

        Padding is done using the specified fill character (default is a space).
        """
        pass

    def rpartition(self, *args, **kwargs):  # real signature unknown
        """
        Partition the string into three parts using the given separator.

        This will search for the separator in the string, starting at the end. If
        the separator is found, returns a 3-tuple containing the part before the
        separator, the separator itself, and the part after it.

        If the separator is not found, returns a 3-tuple containing two empty strings
        and the original string.
        """
        pass

    def rsplit(self, *args, **kwargs):  # real signature unknown
        """
        Return a list of the substrings in the string, using sep as the separator string.

          sep
            The separator used to split the string.

            When set to None (the default value), will split on any whitespace
            character (including \n \r \t \f and spaces) and will discard
            empty strings from the result.
          maxsplit
            Maximum number of splits.
            -1 (the default value) means no limit.

        Splitting starts at the end of the string and works to the front.
        """
        pass

    def rstrip(self, *args, **kwargs):  # real signature unknown
        """
        Return a copy of the string with trailing whitespace removed.

        If chars is given and not None, remove characters in chars instead.
        """
        pass

    def split(self):  # real signature unknown; restored from __doc__
        """
        Return a list of the substrings in the string, using sep as the separator string.

          sep
            The separator used to split the string.

            When set to None (the default value), will split on any whitespace
            character (including \n \r \t \f and spaces) and will discard
            empty strings from the result.
          maxsplit
            Maximum number of splits.
            -1 (the default value) means no limit.

        Splitting starts at the front of the string and works to the end.

        Note, str.split() is mainly useful for data that has been intentionally
        delimited.  With natural text that includes punctuation, consider using
        the regular expression module.
        """
        pass

    def splitlines(self, *args, **kwargs):  # real signature unknown
        """
        Return a list of the lines in the string, breaking at line boundaries.

        Line breaks are not included in the resulting list unless keepends is given and
        true.
        """
        pass

    def startswith(self, prefix, start=None, end=None):  # real signature unknown; restored from __doc__
        """
        S.startswith(prefix[, start[, end]]) -> bool

        Return True if S starts with the specified prefix, False otherwise.
        With optional start, test S beginning at that position.
        With optional end, stop comparing S at that position.
        prefix can also be a tuple of strings to try.
        """
        return False

    def strip(self, *args, **kwargs):  # real signature unknown
        """
        Return a copy of the string with leading and trailing whitespace removed.

        If chars is given and not None, remove characters in chars instead.
        """
        pass

    def swapcase(self, *args, **kwargs):  # real signature unknown
        """ Convert uppercase characters to lowercase and lowercase characters to uppercase. """
        pass

    def title(self, *args, **kwargs):  # real signature unknown
        """
        Return a version of the string where each word is titlecased.

        More specifically, words start with uppercased characters and all remaining
        cased characters have lower case.
        """
        pass

    def translate(self, *args, **kwargs):  # real signature unknown
        """
        Replace each character in the string using the given translation table.

          table
            Translation table, which must be a mapping of Unicode ordinals to
            Unicode ordinals, strings, or None.

        The table must implement lookup/indexing via __getitem__, for instance a
        dictionary or list.  If this operation raises LookupError, the character is
        left untouched.  Characters mapped to None are deleted.
        """
        pass

    def upper(self, *args, **kwargs):  # real signature unknown
        """ Return a copy of the string converted to uppercase. """
        pass

    def zfill(self, *args, **kwargs):  # real signature unknown
        """
        Pad a numeric string with zeros on the left, to fill a field of the given width.

        The string is never truncated.
        """
        pass