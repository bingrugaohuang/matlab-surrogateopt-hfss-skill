# 发布验证记录

日期：2026-10-29（Asia/Singapore）。适用于本仓库初始版本，不表示所有未来版本或用户环境均已验证。

| 检查 | 结果与范围 |
|---|---|
| Python 3.14 离线测试 | 11 项通过；排名、权衡、非支配关系、身份标签过滤、重复冲突、质量过滤、单位、非法数值、零基准、只读 CLI、坏 JSON |
| Skill Creator quick_validate | UTF-8 模式通过；frontmatter、名称与基础结构检查 |
| MATLAB R2024b 独立 mlint | mock 示例无诊断；没有启动 MATLAB 主程序 |
| 合成 CLI | 纳入 4 点，排除失败点与重复点；总分、S21、折中候选按预期区分 |

CLI 测试使用仓库 `local/` 下的临时沙盒并自动清理；该目录不提交。早期测试使用系统临时目录时被当前沙盒权限拒绝，改为明确的仓库隔离目录后通过。候选工具本身不创建输出文件。

Windows 下验证中文 SKILL.md 时，旧默认编码可能产生解码错误；使用 `python -X utf8 .../quick_validate.py .`。这是校验工具的运行方式，不需要修改全局系统编码。

未执行：MATLAB mock 运行与 checkpoint 中断恢复、真实 HFSS 单点/闭环、AEDT 嵌入式 Python 文件替换、生产缓存/预算/队列验证。参考文档中的协议和预算机制是接入指导，本仓库未附带其完整服务端实现。

整理过程仅在新的 skill 仓库编写公开文件。没有启动、停止或向现有 MATLAB/HFSS 优化投递请求；没有复制原工程、活动账本、checkpoint、私人路径、账号凭据或论文 PDF。

复现：

```text
python -m unittest discover -s tests -v
python scripts/candidate_report.py examples/candidates.synthetic.json
```

Python 工具声明的最低版本为 3.10；本次实际测试版本为 3.14，未逐一运行所有中间版本。MATLAB 示例仅做 R2024b 静态检查，不标为运行已验证。
