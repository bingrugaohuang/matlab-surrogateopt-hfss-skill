---
name: matlab-surrogateopt-hfss
description: Builds, reviews, and troubleshoots MATLAB surrogateopt workflows that evaluate expensive HFSS electromagnetic models. Use for MATLAB-HFSS coupling, checkpoint recovery, simulation budgets, verified warm starts, cache identity, and NGD filter tradeoffs. Preserves an existing working backend and isolates changes from active runs.
---

# MATLAB surrogateopt + HFSS

把 MATLAB 的昂贵黑盒优化与 HFSS 求解接起来，并让每次结果可追溯、可恢复、可比较。默认用用户语言解释。此 skill 提供操作知识与离线辅助工具；真实 HFSS 适配器需要针对工程实现和验证。

## 先确定任务与运行状态

- 区分新建闭环、检查运行、恢复中断、调整目标、离线选点。先读入口、有效配置和少量直接相关文件。
- 查明 MATLAB/AEDT 版本、已有后端、模型/设计/setup/sweep、变量映射、目标、预算和输出目录。不要假设软件装在 C 盘。
- 有活跃优化时，只读检查；把修改放到独立目录。不要改其搜索路径、模型、队列、STOP、配置或 checkpoint。用户已明确授权的独立实验可以继续，不重复索要许可。
- 进程不可见就报告 unknown；静态 doctor 正常不代表可安全启动第二个控制器。
- 沿用已验证的原生 AEDT 脚本、COM 或 PyAEDT 后端。安装本 skill 不构成迁移后端或启动求解的授权。

## 按任务读取

| 任务 | 参考文档 |
|---|---|
| 建立 MATLAB → HFSS → 曲线 → 评分闭环 | [workflow.md](references/workflow.md) |
| options、热启动、续跑、新增预算 | [matlab-and-budget.md](references/matlab-and-budget.md) |
| 缓存、身份、原子发布、故障恢复 | [identity-and-recovery.md](references/identity-and-recovery.md) |
| 报错、假收敛、路径遮蔽、重复求解 | [troubleshooting.md](references/troubleshooting.md) |
| 三谐振器 NGD、四曲线拟合、候选取舍 | [ngd-example.md](references/ngd-example.md) |
| 离线检查、单点验收、闭环验证 | [validation.md](references/validation.md) |
| 官方 API 与参考 skill | [sources.md](references/sources.md) |

## 实施时保留的约束

1. 先固定参数单位、变量名与派生关系。优化变量与 HFSS 实际变量可以不同；写入后读回完整变量集，验证实际求解的是请求点。
2. 把几何合法性检查放在昂贵求解之前。可表达为线性约束时直接传给 solver；非线性约束使用安装版本支持的接口。
3. 冻结仿真身份、评分身份和本轮配置。改变目标/权重意味着新的评分实验，不覆盖旧结果。
4. 默认串行共享工程；只有模型副本、目录、预算和许可证都独立时才考虑并行。
5. 在投递请求之前持久化预算票据；重试复用同一 job。停止回调不能单独保证 HFSS 调用上限。
6. 回应必须匹配 job、仿真身份、评分身份和完整实际变量；核对曲线哈希、频率网格、单位和质量状态，再评分。
7. 请求失败不能变成好分数。区分模型不可行、求解失败、数据缺失与协议错误；身份冲突立即停止提交。
8. 分别保留 exported、converged、precision_validated 证据。CSV 导出成功不证明网格收敛或群时延精度。
9. 报告总分最佳、关键指标最佳、明确选择规则的折中候选及非支配集合。不能仅凭 J 降低声称所有指标改善。

## 可直接运行的离线工具

从 skill 目录运行：

```text
python scripts/candidate_report.py examples/candidates.synthetic.json
```

只读取明确给定的 JSON，向标准输出打印排名；不遍历工程、不写文件、不启动 MATLAB/HFSS。它检查记录结构并按记录的 quality 标签筛选，**不会认证原始曲线或仿真身份**。字段约定见 [examples/README.md](examples/README.md)。

需要熟悉 MATLAB 调用时，可在单独 MATLAB 会话运行 [demo_surrogateopt_mock.m](examples/demo_surrogateopt_mock.m)；它仅优化解析函数并在临时目录保存自己的结果，不是 HFSS 驱动程序。

## 交付

说明实际读取/修改了什么、是否提交求解、预算如何计数、验证达到哪一级，以及剩余风险。给出可定位的文件与证据。不要把本仓库离线测试或历史项目测试写成当前模型的真实闭环验证。
