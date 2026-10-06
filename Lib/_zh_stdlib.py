# -*- coding: utf-8 -*-
"""常用标准库中文别名(懒加载): import 时自动打补丁, 英文原名照常可用."""
import sys as _sys
import importlib.abc as _abc

_PATCHES = {
 "io": {},
 "_pyio": {},
 "csv": {"读取器": "reader", "写入器": "writer", "字典读取器": "DictReader",
         "字典写入器": "DictWriter", "注册方言": "register_dialect",
         "注销方言": "unregister_dialect", "获取方言": "get_dialect",
         "列出方言": "list_dialects", "字段大小限制": "field_size_limit",
         "嗅探器": "Sniffer"},
 "datetime": {"日期": "date", "时间": "time", "日期时间": "datetime",
              "时间差": "timedelta", "时区": "timezone", "时区信息": "tzinfo"},
 "json": {"加载": "load", "加载字符串": "loads", "转储": "dump",
          "转储字符串": "dumps", "编码器": "JSONEncoder", "解码器": "JSONDecoder"},
 "math": {"平方根": "sqrt", "幂": "pow", "正弦": "sin", "余弦": "cos",
          "正切": "tan", "对数": "log", "指数": "exp", "向下取整": "floor",
          "向上取整": "ceil", "阶乘": "factorial", "最大公约数": "gcd",
          "圆周率": "pi", "自然常数": "e", "无穷大": "inf", "非数字": "nan",
          "截断": "trunc", "浮点求和": "fsum", "绝对值": "fabs", "反正弦": "asin",
          "反余弦": "acos", "反正切": "atan"},
 "os": {"取当前目录": "getcwd", "列目录": "listdir", "建目录": "mkdir",
        "建多级目录": "makedirs", "删除文件": "remove", "重命名": "rename",
        "删除目录": "rmdir", "取环境变量": "getenv", "设置环境变量": "putenv",
        "执行系统命令": "system", "遍历目录树": "walk", "环境变量": "environ",
        "分隔符": "sep", "换行符": "linesep"},
 "os.path": {"连接": "join", "分割": "split", "存在": "exists",
             "绝对路径": "abspath", "基本名": "basename", "目录名": "dirname",
             "是否文件": "isfile", "是否目录": "isdir", "文件大小": "getsize"},
 "pathlib": {"路径": "Path", "纯路径": "PurePath"},
 "random": {"随机数": "random", "随机整数": "randint", "选择": "choice",
            "打乱": "shuffle", "均匀分布": "uniform", "高斯": "gauss",
            "种子": "seed", "范围随机": "randrange", "采样": "sample",
            "随机字节": "randbytes"},
 "statistics": {"平均值": "mean", "中位数": "median", "众数": "mode",
                "标准差": "stdev", "总体标准差": "pstdev",
                "方差": "variance", "总体方差": "pvariance",
                "调和平均": "harmonic_mean"},
 "string": {"模板": "Template", "标点": "punctuation", "数字": "digits",
            "字母": "ascii_letters", "大写字母": "ascii_uppercase",
            "小写字母": "ascii_lowercase", "空白": "whitespace",
            "格式化器": "Formatter"},
 "sys": {"版本": "version", "平台": "platform", "路径": "path",
         "参数": "argv", "标准输出": "stdout", "标准输入": "stdin",
         "标准错误": "stderr", "模块": "modules", "最大递归": "getrecursionlimit",
         "默认编码": "getdefaultencoding"},
 "time": {"时间戳": "time", "睡眠": "sleep", "本地时间": "localtime",
          "格林威治时间": "gmtime", "格式化": "strftime", "解析": "strptime",
          "高精度计时": "perf_counter", "单调计时": "monotonic"},
 "turtle": {"前进": "forward", "后退": "backward", "右转": "right",
            "左转": "left", "画笔抬起": "penup", "画笔落下": "pendown",
            "画圆": "circle", "写字": "write", "颜色": "color",
            "画笔大小": "pensize", "速度": "speed", "主循环": "mainloop",
            "清空": "clear", "重置": "reset"},
}

def _apply(name, mod):
    top = name.split(".")[0]
    table = _PATCHES.get(name) or _PATCHES.get(top) if "." in name else _PATCHES.get(name)
    if table is None:
        return
    added = []
    for zh, en in table.items():
        try:
            if hasattr(mod, en) and not hasattr(mod, zh):
                setattr(mod, zh, getattr(mod, en))
                added.append(zh)
        except Exception:
            pass
    if added:
        try:
            all_ = getattr(mod, "__all__", None)
            if isinstance(all_, list) and all_:
                for zh in added:
                    if zh not in all_:
                        all_.append(zh)
        except Exception:
            pass
    if name in ("io", "_pyio"):
        _wrap_io_open(mod)
        return
    if name == "pathlib" or top == "pathlib" and name == "pathlib":
        _patch_pathlib(mod)
    if name == "datetime":
        try:
            if not hasattr(mod, "现在") and hasattr(mod, "datetime"):
                setattr(mod, "现在", mod.datetime.now)
            if not hasattr(mod, "今天") and hasattr(mod, "date"):
                setattr(mod, "今天", mod.date.today)
        except Exception:
            pass

def _patch_pathlib(mod):
    try:
        Path = getattr(mod, "Path", None)
        if Path is None:
            return
        if getattr(Path.read_text, "_zh_utf8", False):
            return
        _orig_read = Path.read_text
        _orig_write = Path.write_text
        _orig_open = Path.open
        def read_text(self, encoding="utf-8", errors=None, newline=None):
            kw = {"encoding": encoding}
            if errors is not None:
                kw["errors"] = errors
            if newline is not None:
                kw["newline"] = newline
            return _orig_read(self, **kw)
        def write_text(self, data, encoding="utf-8", errors=None, newline=None):
            kw = {"encoding": encoding}
            if errors is not None:
                kw["errors"] = errors
            if newline is not None:
                kw["newline"] = newline
            return _orig_write(self, data, **kw)
        def open(self, mode="r", buffering=-1, encoding="utf-8", errors=None, newline=None):
            kw = {}
            if errors is not None:
                kw["errors"] = errors
            if newline is not None:
                kw["newline"] = newline
            # 二进制模式不传 encoding(与 open 语义一致)
            if "b" in mode:
                return _orig_open(self, mode, buffering)
            return _orig_open(self, mode, buffering, encoding, **kw)
        for f, o in ((read_text, _orig_read), (write_text, _orig_write), (open, _orig_open)):
            f._zh_utf8 = True
            try:
                f.__doc__ = o.__doc__
                f.__name__ = o.__name__
                f.__module__ = "pathlib"
            except Exception:
                pass
        Path.read_text = read_text
        Path.write_text = write_text
        Path.open = open
    except Exception:
        pass

class _ZhLoader(_abc.Loader):
    def __init__(self, orig):
        object.__setattr__(self, "_orig", orig)
    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_orig"), name)
    def create_module(self, spec):
        cm = getattr(object.__getattribute__(self, "_orig"), "create_module", None)
        if cm is None:
            return None
        try:
            return cm(spec)
        except Exception:
            return None
    def exec_module(self, mod):
        object.__getattribute__(self, "_orig").exec_module(mod)
        try:
            _apply(mod.__name__, mod)
        except Exception:
            pass

class _ZhFinder(_abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        top = name.split(".")[0]
        if name not in _PATCHES and top not in _PATCHES:
            return None
        for finder in _sys.meta_path:
            if finder is self:
                continue
            try:
                try:
                    spec = finder.find_spec(name, path, target)
                except TypeError:
                    spec = finder.find_spec(name, path)
            except Exception:
                continue
            if spec is not None and spec.loader is not None:
                try:
                    spec.loader = _ZhLoader(spec.loader)
                except Exception:
                    return None
                return spec
        return None

class _OpenWrapper:
    # 可调用对象(而非函数): 作为类属性访问时不会绑定 self,
    # 否则测试类中 self.open(path) 会把 self 当 file 传入
    def __init__(self, orig):
        self._orig = orig
        self._zh_utf8 = True
        try:
            self.__doc__ = orig.__doc__
        except Exception:
            pass
        try:
            self.__name__ = getattr(orig, "__name__", "open")
        except Exception:
            pass
        try:
            self.__module__ = "io"
        except Exception:
            pass
    def __call__(self, file, mode="r", buffering=-1, encoding=None,
                 errors=None, newline=None, closefd=True, opener=None):
        if encoding is None and isinstance(mode, str) and "b" not in mode:
            encoding = "utf-8"
        return self._orig(file, mode, buffering, encoding, errors,
                          newline, closefd, opener)

def _wrap_io_open(mod):
    try:
        orig = getattr(mod, "open", None)
        if orig is None or getattr(orig, "_zh_utf8", False):
            return
        mod.open = _OpenWrapper(orig)
    except Exception:
        pass

def install():
    for f in _sys.meta_path:
        if isinstance(f, _ZhFinder):
            return
    _sys.meta_path.insert(0, _ZhFinder())
    _wrap_io_open(_sys.modules.get("io"))
    # 已导入的模块直接补丁
    for name in list(_PATCHES):
        mod = _sys.modules.get(name)
        if mod is not None:
            try:
                _apply(name, mod)
            except Exception:
                pass
