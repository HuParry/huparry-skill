# 用户样例学习记录

以下记录来自用户于本次任务提供的 ZIP，作为格式线索，不把未验证的历史程序当作通用模板。

## 来找直角三角形.zip

- 顶层 `648/`，`problem_zh.md`、`problem.yaml`、`testdata/config.yaml`。
- `type: default` + `checker_type: testlib` + `checker: checker.cc`：这是常规题中的 SPJ 分支。
- 50 对 `.in/.out`；YES 数据的 `.out` 可以只有结论，由 checker 检验选手构造。
- `template.cpp` 是基于 genlib.hpp 的生成工具，不是判题程序；包中未附 genlib.hpp，不能当作自包含构建环境。
- 静态审查发现：YES 分支没有验证选手首词确实为 YES，也没有验证直角。反例输入 a=5,b=10，点 (0,0)、(3,4)、(6,-8)：三条边均不与坐标轴平行，最短两边长 5 和 10，但第三边平方为 153，不是 125。该程序的现有检查不足以拒绝它。
- `type: min` 表达全组判定，不表示每点独立计分。

## 猜最大数最小数.zip

- 顶层 `510/`，`type: interactive`，`interactor: interactor.cpp`，15 对 `.in/.ans`。
- 原始输入含 n 与隐藏数组；选手只先读 n，通过 `? i j` 查询，最终 `! 最小下标 最大下标`。
- 使用 testlib registerInteraction。私有答案文件存最终两下标。
- 静态审查发现：Left 在读操作类型前递减，最终 `!` 被计入预算；用满题面允许的查询次数后无法提交答案。未知命令也未立即拒绝。这些不是应继承的约定。

## 通信题：寻找不同的位置 (1).zip

- 顶层 `819/`，`type: communication`，`num_processes: 2`，`manager.cpp`。
- Run-Twice：first 获得 S，second 获得 T 和 first 发送的一个受限整数。
- 部分输入共享 `equal.out`，不是文件遗漏；须按 config 引用验证。
- manager 通过 fdopen 接管继承描述符、关闭写端，并规范化转发整数。这些是值得保留的实际接口处理。
- 配置的 min 与每点 score:2 并存，不应凭表面字段推断“每点独立2分”；重新根据用户意图设置 sum/min，并验证归一化和总分。

## 魔术表演.zip（带图片的题面）

- 顶层 `716/`。图片实际路径为 `716/additional_file/FaWel_fY2cF_jI2JPCM2C.png`，与 problem_zh.md、testdata 同属一道题。
- 原文引用为 `![](file://FaWel_fY2cF_jI2JPCM2C.png =300x)`。`file://` 后跟公开附件名，不加 additional_file/ 前缀，也不是本机文件路径；`=300x` 为样例使用的宽度标记。
- 图片已实际查看，为杯子魔术场景的背景插画。图片引用尺寸不是原文件尺寸，不应为匹配展示宽度擅自裁掉内容。
- 样例仅含一对 d01.in/d01.out，且没有 testdata/config.yaml。这能证明附件目录与引用格式，不能作为当前用户“固定50点、min、显式资源配置”的完整模板。不得因为新样例更简短就覆盖这些已确认规则。
- 只学习图片打包方式，不沿用其 pid、owner、统计和与当前新题无关的背景内容。

## 已完成作品带来的补充

本会话制作 CF2179F 时验证过：多组批量通信需要并发 I/O；判错时常规 exit 可能等待阻塞写线程持有的 FILE 锁；本地联测器同时 communicate 和代理转发可产生管道竞态。相关处理已归入 communication.md，不要求将该图题的具体数据规模当作其他通信题的默认。

用户反馈 CF2258C 的交互裁判存在目标环境编译问题。此前改名并随包提供 cf_testlib.h 的做法不应成为模板：标准 Hydro 直接提供 testlib.h。新规范改为标准 include、保留默认流同步与绑定，并要求实际上传源文件用 Hydro 配套头文件编译、再做真实交互联测；不把私有头文件下的本地编译或源码扫描当作目标环境验证。
