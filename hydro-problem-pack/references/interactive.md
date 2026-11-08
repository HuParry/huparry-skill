# 交互题

## 接口

### 本项目必须遵守的实现约定

- interactor 直接 `#include "testlib.h"`，入口先调用 `registerInteraction(argc, argv)`。标准 Hydro 编译时会提供头文件；不改名为 cf_testlib.h，不额外打包副本，不为它配置 judge_extra_files。
- **用户明确要求：交互裁判和交互参考解均保留默认 C++ 流同步和默认绑定。** 不调用 `ios::sync_with_stdio(false)`、`ios_base::sync_with_stdio(false)` 或等价的 0 参数，也不使用 `cin.tie(nullptr)`/`cin.tie(0)`。这是本项目约定，不表述为所有交互程序在语言原理上都不能关闭同步。
- interactor 用 ouf 读选手命令，不再用 cin、scanf 或 getline 读取同一 stdin。保持同步也不能修复两个读取器争抢同一通道的问题。
- 回复统一使用 `cout << ... << endl`，仍须显式刷新，不能依赖默认绑定碰巧触发刷新。私有输入用 inf，标准答案按需用 ans；tout 是记录文件，不是给选手的回复通道。

一个选手程序与 interactor 通过标准输入输出持续交换消息。裁判私有 `.in` 不等于选手初始输入，先列明哪些量可以公开。

Hydro 当前实现将 interactor 以以下参数运行：

```text
interactor /w/in /w/tout /w/out
```

testlib 使用 `registerInteraction(argc, argv)`：`inf` 读私有输入，`ouf` 从选手 stdout 读命令，`ans` 读参考答案文件；interactor stdout 发回复给选手。判定使用 `quitf(_ok/ _wa/ _fail, ...)` 等 testlib 协议，不能把通信 manager 的 stdout 0/1 得分协议照搬过来。

## 裁判结构与可编译示例

按“初始化 testlib → 读取私有数据并计算必要信息 → 发送公开初始输入 → 查询/答案分支 → 结束判定”组织程序。常规参数解析使用 testlib 的 readInt/readLong/readToken，避免无必要的自定义整数解析器、文件描述符接管、线程和退出系统。私有数据损坏为 `_fail`，选手答案或查询错误为 `_wa`/格式错误。

可以直接编译联测的具体示例：[interactor.cpp](../assets/interactive-minmax/interactor.cpp) 与 [solution.cpp](../assets/interactive-minmax/solution.cpp)。示例为单组最小/最大值下标查询：1≤n≤10000，互异整数绝对值≤10^9；查询要求 i<j，预算 ceil(3n/2)-1，最终答案不计次数。仅学习结构，不能把该题协议套给其他题。

容易直接从私有数据计算的真值可不依赖 ans；答案非唯一时校验语义。不要擅自发送成功确认、错误码或下一组标记。若题目规定发送 -1，须明确相应错误路径；testlib 解析失败可能直接判格式错误，不能声称所有异常都已发出 -1。

## 协议清单

题面、标程、interactor 对齐以下规则：初始公开输入；查询语法；参数顺序和范围；每类命令的返回；何时刷新；次数预算与是否跨多组重置；答案语法；结束是否有回复；错误回复（如有）。

未由题目规定的公平性策略不要擅自更改。例如 i<j 的查询限制必须遵守，等号允许与否必须明确，最终答案不计入询问时不能扣次数。

正确的计数框架：

```text
持续读命令：
  若是查询：验证参数；若 used == limit 则拒绝；++used；输出并刷新回复
  若是最终答案：验证答案；按题面结束协议收尾并判定
  否则：拒绝
```

不要使用“只循环 limit 次，每读一条命令就扣一次”的写法；这会把最终答案误算成查询，并拒绝恰好用满额度的合法解。

## 活性和结束

- 每次需要选手读取的回复都刷新；不能等待双方都没有义务发送的消息。
- 最终答案之后如题面要求立即结束，应测试选手等待额外回复、继续发命令或不退出的情况。对 EOF 的检查需配合关闭该关闭的输入端和外层超时，不能无条件无限等。
- 多组题每次作答只结束本组，不能提前 quitf(_ok) 或关闭 stdout。最后一组才结束；不无理由手动 fclose(stdout) 或接管标准流。
- 需要检查额外输出时，在最后一组、选手按协议应当退出的阶段检查 ouf；不能在还需发送下一组 n 或查询回复时先等 EOF。testlib 的 interactor 模式不能假定 quitf(_ok) 自动执行普通 checker 的尾随内容检查。
- 明确静态/自适应裁判，按本题要求实现；不能借“增强数据”改变策略空间。

## 联测

**编译是交付硬门槛。** 先对实际要打包的 interactor.cpp 使用标准名称 testlib.h 编译，并编译实际参考解。默认以 C++17 构建；例如 `g++ -std=c++17 -O2 interactor.cpp -I 本地testlib目录 -o interactor`。优先取得目标 Hydro 配套版本；Hydro 仓库使用 testlib 子模块，应按锁定的提交取文件，而非误把子模块当普通 raw 文件路径。记录编译器、标准及头文件版本。不能只编译改写版或私有改名头文件版本。

交付前检查缺失 include、非标准扩展、参数类型、testlib API 兼容性和额外依赖。源码或依赖改动后重新编译联测；任何编译失败先修复，不把失败结果写成通过。如果目标版本无法取得，明确实际验证版本及未验证项，不伪称目标平台通过。

常见约定可先自动检查：

```text
python scripts/check_interactive.py --interactor testdata/interactor.cpp --solution author/reference.cpp
```

不带编译选项时，工具只检查标准 include、testlib 入口、同步/绑定及混用 stdin 的常见写法，不解析 C++ 完整语义，检查通过不能代替编译。

为防止只做文本检查，也可让工具调用真实编译器，对刚才指定的原文件直接构建；任何编译错误都会使命令失败：

```text
python scripts/check_interactive.py --interactor testdata/interactor.cpp --solution author/reference.cpp --testlib-dir 本地testlib目录 --compiler g++ --build-dir work/interactive-build
```

未传 --testlib-dir 时输出会明确标记“未请求编译”；不能把这次静态检查记为编译通过。编译产物与本地 testlib 保留在导入目录之外。

用真实 interactor 和两个方向的管道，记录请求/响应；不要把所有预设回复一次喂给普通程序当作完整交互测试。覆盖 n 最小值、0 次询问直接回答（若合法）、恰好 limit 次查询后回答、limit+1、坏参数、未知命令、错误答案、提前 EOF、未刷新/死锁。

判题环境缺失时可先做本地真实管道联测，报告尚未在目标 Hydro 实测。独立静态回放可用于解析器分支，但不能替代会读回复的活跃参考解。

打包前确认没有把本地 testlib 副本或改名版本塞入导入包。平台依据：[Hydro compileLocalFile 自动提供头文件](https://github.com/hydro-dev/Hydro/blob/master/packages/hydrojudge/src/task.ts)。
