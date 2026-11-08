# HuParry Skills

用于规范化 Hydro OJ 出题流程的 Codex skill。当前提供 **hydro-problem-pack**，可根据题面、题目链接、截图、参考代码或样例压缩包，制作中文题面的 Hydro 题目数据包。

## 支持范围

| 类型 | 评测配置 | 处理内容 |
| --- | --- | --- |
| 常规题 | `type: default` | 标准答案、普通判题；构造题等非唯一答案使用 SPJ |
| 交互题 | `type: interactive` | 交互协议、询问预算、interactor 与管道联测 |
| 通信题 | `type: communication` | 多进程信息隔离、通信预算、manager 与完整联测 |
| 含图片的题面 | 适用于以上所有类型 | 图片附件打包、Hydro 引用语法与缺图检查 |

这是供 Codex 使用的工作规范和辅助工具；它不会自行登录 OJ、提交代码或发布线上题目。

## 安装

在目标设备的 Codex 对话中发送：

```text
请安装这个仓库中的 hydro-problem-pack skill：
https://github.com/HuParry/huparry-skill/tree/main/hydro-problem-pack
```

也可以按照 [Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills)，将整个 `hydro-problem-pack/` 文件夹复制到本机技能目录。必须保留 `references/`、`scripts/` 和 `agents/`，不能只复制 `SKILL.md`。

本地安装的文件需要在其他设备分别安装。仓库更新后，已有安装也应重新同步或更新；仅登录同一个账号或更新聊天记录，不代表本地文件已经更新。

## 使用

安装后，在 Codex 聊天中用 `$hydro-problem-pack` 调用。

### 已有题目链接

```text
使用 $hydro-problem-pack，制作下面这道题的 Hydro 数据包：
【题目链接】

按默认规范完成中文题面、参考代码、Markdown 题解、测试数据和本地验证，
交付 Hydro 导入包和完整资料包。
```

### 自创题目

先附上题面文档、截图或文字，再发送：

```text
使用 $hydro-problem-pack，根据附件中的题目制作 Hydro 数据包。

数据范围：【填写】
通信预算或询问上限：【如适用则填写】
其他特殊要求：【没有则删除】

影响题意或评测结果的歧义先向我确认，其余按默认规范完成。
```

### 本次有特殊要求

直接在请求中补充，例如：

```text
这次时间限制改为 3 秒、空间限制改为 512 MB。
先给出参考代码，等我确认通过后再继续打包。
```

当次明确要求优先于 skill 的默认规范。已有图片或样例 ZIP 可以一起提供，不必重复描述附件格式。

## 默认出题规范

| 项目 | 默认约定 |
| --- | --- |
| 题面 | 中文；保留原数学含义与输入输出协议 |
| 题解 | 中文 Markdown，便于复制与发布 |
| 参考代码 | 通常使用 C++17 |
| 测试点 | 固定 50 个 |
| 评分 | 单个 100 分 `min` 子任务，全部通过才得 100 分 |
| 时间与内存 | 当次指定优先，其次沿用原题；未提供的对应项默认 1 秒、256 MB |
| 资源限制的位置 | 只写入 YAML 配置，不在题干中重复写出 |
| 验证与交付 | 自行完成本地验证后交付；不默认等待人工确认 AC |
| 题号与历史字段 | 不沿用样例的 owner、提交统计或旧题号；明确指定时才设置 pid |

`min` 可以让失败后尚未开始的测试点跳过，以节省评测资源；已经并行运行的测试点是否继续，由评测机调度决定，不保证严格逐点串行停止。

## 交付内容

一次出题通常提供两个文件：

1. **Hydro 导入包 ZIP**：直接上传到 Hydro 的“导入题目”入口。
2. **完整资料包 ZIP**：包含导入包、可编辑题目原文件、参考解、题解、生成器、数据清单与验证报告。

完整资料包中的 `author/` 是出题人资料，不应作为选手公开附件。导入已有题目的测试数据与整题导入是不同入口，具体操作以该次交付说明为准。

本仓库保存的是 skill 源文件，生成题目时仍会正常产出题目 ZIP。

## 题面图片

图片放在题目目录下的 `additional_file/`，例如：

```text
1/
  problem.yaml
  problem_zh.md
  additional_file/
    figure-01.png
  testdata/
    config.yaml
    ...
```

在 Hydro 题面中引用：

```markdown
![示意图](file://figure-01.png)
```

需要指定显示宽度时：

```markdown
![示意图](file://figure-01.png =300x)
```

`file://` 后面是附件名，不加 `additional_file/` 前缀，也不填写本机绝对路径。`=300x` 是 Hydro 的扩展语法，普通 Markdown 预览未必支持。完整规则见 [题面图片说明](hydro-problem-pack/references/statement-images.md)。

## 打包辅助工具

### 交互程序编写与编译

交互裁判直接使用 `#include "testlib.h"`，由 Hydro 提供该头文件，不改名、不随题目重复打包，也不为它添加 `judge_extra_files`。本地通过编译器的 `-I` 指定标准 testlib.h 所在目录。

本项目要求交互裁判和参考解保留默认 C++ 流同步和绑定，不关闭 `sync_with_stdio`，不调用 `cin.tie(nullptr)`。裁判用 testlib 的 `ouf` 读取命令、`cout << ... << endl` 回复，不能再用 `cin` 或 `scanf` 抢读同一输入通道。

提供一份可编译的 [最小/最大值交互裁判示例](hydro-problem-pack/assets/interactive-minmax/interactor.cpp) 和 [配套参考解](hydro-problem-pack/assets/interactive-minmax/solution.cpp)，展示正确的计数、刷新、语义检查和结束流程。它们是具体题目的示例，不应直接套用到其他交互协议。

交付前必须编译实际上传的源文件，再进行真实管道联测；编译失败不能交付为已完成。下面的命令既检查源码约定，也调用真实 C++17 编译器：

```sh
python hydro-problem-pack/scripts/check_interactive.py --interactor hydro/1/testdata/interactor.cpp --solution author/reference.cpp --testlib-dir 本地testlib目录 --compiler g++ --build-dir work/interactive-build
```

不指定 `--testlib-dir` 时仅做源码约定检查，不能据此宣称编译通过。详细要求见 [交互题规范](hydro-problem-pack/references/interactive.md)。

交互示例已使用 Hydro 锁定的 testlib 提交 `2d20123984e9479b8a56ebe0d6a51e23ad7c35b3`、GCC 16.2.0、C++17 在本地编译通过，并验证 11 组正常交互（n 从 1 到 10000）、10 项协议探测、源码约定检查及真实编译失败时的阻断。该结果为 Windows 本地管道验证，不代表已在所有 Hydro 服务器或 Linux 沙箱中实测。

### 题目导入包

通常由 Codex 在执行 skill 时调用，无需手动操作。手动使用时，需要 Python 3.10 或更新版本；脚本只使用标准库。

在仓库根目录运行：

```sh
python hydro-problem-pack/scripts/build_import.py --root hydro/1 --output Hydro导入包.zip
```

如评测需要额外程序，显式加入对应源文件：

```sh
python hydro-problem-pack/scripts/build_import.py --root hydro/1 --judge-source checker.cc --output Hydro导入包.zip
```

交互题改为 `--judge-source interactor.cpp`，通信题改为 `--judge-source manager.cpp`；多个必需源文件或头文件可重复该参数。路径相对于 `testdata/`。题面图片会从 `additional_file/` 自动纳入，不需要使用此参数。

该工具检查文件白名单、默认 50 个输入文件、路径、图片引用、空文件及 ZIP 完整性。它不解析 YAML 配置语义，也不能代替标准答案验证、裁判程序联测和 Hydro 实际显示检查。

## 仓库结构

```text
README.md
hydro-problem-pack/
  SKILL.md
  agents/openai.yaml
  references/
    package-format.md
    normal.md
    interactive.md
    communication.md
    statement-images.md
    sample-findings.md
  scripts/
    build_import.py
    check_interactive.py
  assets/interactive-minmax/
    interactor.cpp
    solution.cpp
```

- [SKILL.md](hydro-problem-pack/SKILL.md)：完整入口与执行流程。
- [目录、配置与计分](hydro-problem-pack/references/package-format.md)：三类题型共同的导入格式。
- [常规题与 SPJ](hydro-problem-pack/references/normal.md)、[交互题](hydro-problem-pack/references/interactive.md)、[通信题](hydro-problem-pack/references/communication.md)：各题型的裁判接口与验证重点。
- [样例学习记录](hydro-problem-pack/references/sample-findings.md)：样例格式和已发现的判题缺陷，避免照搬。

本地验证通过不等于已在目标 Hydro 实例验收。生成题目包后，应按交付说明在目标实例提交参考解，核对实际评测结果。
