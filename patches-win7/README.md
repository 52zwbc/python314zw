# Win7/Vista 兼容补丁（取自 PythonVista v3.14.8）

来源：https://github.com/adang1345/PythonVista （tag `v3.14.8`，`patches/` 目录）。
该仓库发布的是补丁包而非改完的完整源码：从 python.org 官方 sdist 出发，
按 `Notes.md` 中 Python 3.14 一节打补丁，再跑 `Tools/msi/buildrelease.bat`。

## 补丁清单（3.14.8 用这 5 个）

| 补丁 | 作用 |
|---|---|
| `add-dll-8.patch` | 随包安装 `api-ms-win-core-path-l1-1-0.dll`（Vista/Win7 运行必需） |
| `restore-vista-handling-12.patch` | 恢复 Vista/SP2 兼容：运行时检测 API 是否存在并降级；安装程序 OS 版本检查改写 |
| `build-full-installer-8.patch` | 切到 `full.wixproj` 打完整离线包（含调试符号/二进制、UCRT、自由线程版、JIT）；`Download→Install` 文案 |
| `fix-launcher-2.patch` | py 启动器 Win7 兼容（CompareStringEx/注册表/ini  workaround）+ 随包带 dll |
| `fix-tcltk-2.patch` | 用支持 Vista 的 Tcl/Tk 依赖版（3.14.8 专用） |
| `zh-bundle-win7.patch` | 自制：将上面两个补丁对 `Default.wxl` 的改动汉化后合入本仓库版本 |

`support-vs-2026-14.patch` 未采用：其适用范围只到 3.14.7，且现有构建在 runner
VS 下已可通过。

## 应用顺序（workflow 中执行，勿调换）

```
add-dll-8 → fix-launcher-2 → build-full-installer-8 → restore-vista-12 → fix-tcltk-2 → zh-bundle-win7
```

`add-dll-8` 必须在 `fix-tcltk-2` 之前（两者都改 `PCbuild/get_externals.bat` 同一位置）。

## 与中文汉化的合并说明

- `restore-vista-12` / `build-full-installer-8` 对 `Tools/msi/bundle/Default.wxl`
  的 hunks 被 `--exclude` 跳过，改由 `zh-bundle-win7.patch` 以汉化形式加入：
  `FailureOldOS` 拆为 6 条 Win7/Vista/Server 中文提示（bootstrapper cpp 引用了这些新 ID，
  缺失会导致构建失败）；3 条 `Include_*` 由“下载”改为“安装”、VS 2017→VS 2026（full 离线包语义）。
- `restore-vista-12` 对 `Default.thm` 的 hunks 整段跳过：它动的是 Install 页
  （删退役提示、按钮上移），我们保留自己的 Success 页二维码版；两者正交。
- `DeprecationMessage`（郭老师修改版文案）保留未删。
- 其余补丁文件与中文改动（`Parser/pegen.c`、`Python/bltinmodule.c`、`Objects/*`、
  `Modules/main.c`/`_io/*`、`Lib/_zh_*`）无重叠，直接应用。
