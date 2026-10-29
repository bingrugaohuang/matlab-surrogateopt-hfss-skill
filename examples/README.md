# 离线示例契约

`candidates.synthetic.json` 所有候选都是合成数字，不是实际 HFSS 测量或优化结果。

顶层 `sim_id`/`score_id` 定义本次可比组；每条记录必须一致。它们仅是调用者提供的标签，本工具不读取模型、原始曲线或哈希侧文件。严格身份认证应由真实适配器完成。

必需字段：

- `schema_version: 1`；`units` 必须精确为 S21/S11/S22=dB、GD=ns。
- `weights`/`scales`：四个通道的正有限数值；采用 `sum(w*(RMSE/scale)^2)/sum(w)` 重新计算 J。
- `candidates`：记录数组，包含非空 `id`、身份、`status`、`quality` 和四个非负有限 RMSE。
- 可选 `baseline_id` 必须对应最终纳入的点；基准为零的通道百分比输出 null。

`status` 必须是 `ok`。质量顺序为 exported < converged < precision_validated。`--minimum-quality` 控制筛选；这是标签过滤，不认证标签真实性。若过滤掉基准，应选择同质量组中的基准或去掉 baseline_id。

重复且相同的有效 id 只纳入一次；同 id 的不同有效结果直接报错。身份不匹配、失败、质量不足或指标非法的记录带原因排除。只支持完整 JSON，不接受正在追加的 JSONL；应先从权威账本导出一致快照。

折中点选择最小的 `max(RMSE/scale)`，相同则按 J、id 排序；它不是第二套用户偏好，也不替代工程门槛。Pareto 是四项 RMSE 同时最小化，保留相同误差的不同 id。

工具只读取输入并打印 JSON。数据适配/输出重定向由使用者明确指定，避免报告误写到活动目录。

`demo_surrogateopt_mock.m` 用 2 维解析函数示范基本 solver、options、callback、checkpoint。它没有故障重试、HFSS 服务或预算票据。每次运行建立新临时目录；恢复方式见参考文档，而不是复用某个现有工程的 checkpoint。
