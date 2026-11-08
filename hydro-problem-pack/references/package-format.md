# 包结构、配置与计分

## 共同结构

整题导入 ZIP 的顶层直接放一个数字目录，不能额外包一层 hydro 或项目目录：

```text
1/
  problem.yaml
  problem_zh.md
  additional_file/  # 题面有图片时使用；是公开附件，不放标程或测试答案
    figure.png
  testdata/
    config.yaml
    01.in
    01.out
    ...
    checker.cc       # 仅 SPJ 需要
    interactor.cpp   # 仅交互题需要
    manager.cpp      # 仅通信题需要
```

`.out` 与 `.ans` 均可，关键是 config 中引用的文件确实存在；允许多个输入共享同一个答案文件。不要为了配对数量强行复制答案。

题面图片与 testdata 同级存入 additional_file，正文使用 Hydro 的 `file://文件名` 引用，不能用当前电脑的绝对路径。尺寸语法、命名与验证见 [statement-images.md](statement-images.md)。图片不需要注册到 problem.yaml 的 statements 列表。

最小 problem.yaml 示例：

```yaml
title: 题目中文名称
tag:
  - 图论
statements:
  - name: zh.md
    lang: zh
    source: problem_zh.md
```

题号、owner 和历史统计不属于可复用模板的必填信息。示例来自导出包，不能照抄旧账户字段。

## 评测配置

普通题默认采用 50 点、单个 100 分 min 子任务。以下只展示前两点，实际应继续列到 50.in/50.out，共 50 个 case：

```yaml
type: default
time: 1000ms
memory: 256m
subtasks:
  - id: 1
    type: min
    score: 100
    if: []
    cases:
      - input: 01.in
        output: 01.out
        score: 100
      - input: 02.in
        output: 02.out
        score: 100
```

SPJ 追加：

```yaml
checker_type: testlib
checker: checker.cc
```

交互改为 `type: interactive`，配置 `interactor: interactor.cpp`；不要配置 communication 的 num_processes。

标准 Hydro 会为 interactor 编译提供 testlib.h，源代码直接 `#include "testlib.h"`。不要仅为这个头文件添加 judge_extra_files，不要复制进 testdata，也不要改成 cf_testlib.h 等私有名称。本地编译通过 `-I 本地testlib目录` 提供依赖；本地工具依赖不属于导入包内容。

通信改为：

```yaml
type: communication
num_processes: 2
manager:
  file: manager.cpp
  lang: auto
```

保留适用的 time、memory、subtasks。进程数按题意设定，2 是本用户提供的双人样例，不是所有通信题的定律。

## 计分语义和用户约定

- 当前用户明确规定固定 50 点、`type: min`。默认一个 100 分 min 子任务，各 case 的满分同为 100；全通过得 100，任一点失败该子任务得 0。不是把 50 个 100 分 case 相加。
- 可省略 case 的 score 让平台按 min 归一化；显式写时每点写 100，不写 2。配置和平台行为应实际核对。
- min 的目的是提前跳过后续未开始的点。当前 flow 会检查子任务得分是否已归零再启动待运行点；已并发运行的 case 不保证被即时取消。不在 skill 中调整服务器并发设置，也不声称严格串行评测。
- 只有用户明确更改规则时才采用 sum 等其他方案；sum 按点分累加，整数点分相加应为 100。不得把原通信样例的 score:2 或过去作品的 sum 当作新默认。
- 有依赖的子任务用 `if` 表达依赖，只在题目本来有依赖时使用。
- 比例乘分常有向下取整；若用户另行指定部分得分机制，应明确其与 min 的合并方式。

题面、配置、报告必须描述同一种评分方式。时间和内存只写在配置文件，不写进题干；用户未提供的对应项分别默认 1000ms、256m，已有原题限制则沿用，用户本次要求优先。

## 完整资料包

参考组织（可调整命名）：

```text
Hydro导入包.zip
hydro/1/...
author/
  reference.cpp
  题解.md
  generate.py
  cases.csv
  validation_report.json
  本地联测工具（若需要）
导入说明.md
```

不含编译器、缓存、编译产物和未使用的依赖。交互题按上文使用 Hydro 自带的 testlib.h；其他实际需要的依赖另行确认，并写清本地复测方法。若目标服务器明确不是标准 Hydro 环境，先核实编译设置，不自行绕过平台头文件。genlib.hpp 样例仅用于出题生成，不应无理由成为选手或评测端的依赖。

整题导入与已有题目的测试数据上传是不同入口：后者只上传 testdata 内容，并单独设置题面与元信息。交付说明避免混淆。

## 当前接口的核对来源

2026-11-08 核对官方实现；未来版本变化时重新检查相应实现，不为已有可验证配置无意义地重复联网：

- [default.ts](https://github.com/hydro-dev/Hydro/blob/master/packages/hydrojudge/src/judge/default.ts)
- [interactive.ts](https://github.com/hydro-dev/Hydro/blob/master/packages/hydrojudge/src/judge/interactive.ts)
- [communication.ts](https://github.com/hydro-dev/Hydro/blob/master/packages/hydrojudge/src/judge/communication.ts)
- [flow.ts](https://github.com/hydro-dev/Hydro/blob/master/packages/hydrojudge/src/flow.ts)
