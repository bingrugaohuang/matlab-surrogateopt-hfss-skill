# MATLAB options、热启动与预算

## 安装版本优先

在允许使用的独立会话检查 `ver`、`help surrogateopt`、`optimoptions('surrogateopt')`。在线文档可能是更新版本；不要把其他 solver 的 `HybridFcn`、`MeshTolerance` 等选项照搬。无需为只读审查启动正在占用资源的第二个 MATLAB。

基础调用与可运行 mock 见 [demo_surrogateopt_mock.m](../examples/demo_surrogateopt_mock.m)。真实 objective 必须实现 workflow.md 的变量、预算与响应边界。

## 热启动有两种语义

- `InitialPoints=X`：给几何起点，仍需评价；这些调用不是免费样本。
- `InitialPoints=struct('X',X,'Fval',F)`：提供已知分数。只有点与分数的来源、完整仿真设置、评分定义和约束值可信且一致时才使用。

有非线性约束时还要处理对应 `Ineq`；不能只补 Fval 就假定约束已经认证。检查维度、有限性、边界、去重、量化后实际几何和样本覆盖。用缩放后的样本秩/分布辅助判断，不把满秩等同于好代理模型。

旧样本身份不足时仍可离线比较。若保留了可信原始曲线且仿真身份一致，可按新评分器重新评分；如果仿真设置不同，就不能仅重新计算 Fval 冒充同一实验。不要要求所有历史样本无条件重算。

## checkpoint 是状态续跑，不是新实验

保存原始 options 与冻结配置。检查当前目录、函数句柄实际文件、版本、bounds、mapping、target 与 scorer 是否仍对应原运行。

可靠的续跑形式是基于原 options 更新安装版本允许修改的字段：

```matlab
S = load(optionsFile, 'opts');
resumeOpts = optimoptions(S.opts, 'MaxFunctionEvaluations', newTotal);
[x,fval,exitflag,output,trials] = surrogateopt(checkpointFile,resumeOpts);
```

这是依赖既有文件的模板，不要在身份校验前直接执行。`newTotal` 是 solver 累计评价限额，不是“从现在开始新增这么多”。恢复前后核对 OutputFcn、CheckpointFile、UseParallel 和预算记录。不要新建只设置 PlotFcn 的 options 并依赖其余设置自动保留。若只需原样恢复，可采用安装版本文档给出的 checkpoint 调用。

换评分、换变量映射或换模型后，从已审核的点开启新实验；不要把旧 checkpoint 改名继续用。

## 昂贵求解使用独立预算

分别记录：solver 评价次数、唯一请求数、实际求解尝试数、完成数、缓存命中数、失败数。它们可能不同。

推荐事务：在锁内查询规范化设计键 → 已有票据复用 job → 检查剩余配额 → 持久化票据 → 解锁 → 发布请求。崩溃后不能删除未完成票据来“返还”预算，先确认其状态。OutputFcn 在评价之后才执行，不能替代投递前上限检查。

明确预算到底限制唯一设计还是实际求解次数。原工作流的一设计一票据机制限制新增设计；同一 job 若真正重算，仍会消耗计算资源。严格限制求解尝试时，应另外预留 attempt 票据并设置有界重试，不能把无限重试隐藏在同一 job 下。

## 采样参数

`MinSurrogatePoints` 影响构建代理的前期成本，不能一律调小；`MinSampleDistance` 应结合归一化空间与映射后的实际分辨率理解。代理重置不等于 HFSS 重启。14 维案例曾用 28 个最小代理点，这是案例配置，不是通用最优值。

扩大维度时先做预算明确、可信样本热启动、质量过滤的短实验；再根据敏感性、交互作用与可制造性降维。不要仅看一次小样本相关系数就冻结变量。

官方依据：[surrogateopt](https://www.mathworks.com/help/gads/surrogateopt.html)、[options](https://www.mathworks.com/help/gads/surrogate-optimization-options.html)、[checkpoint](https://www.mathworks.com/help/gads/work-with-checkpoint-files.html)。
