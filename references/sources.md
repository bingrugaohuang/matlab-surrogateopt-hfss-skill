# 来源与借鉴范围

API 页面于 2026-10-29 核对；在线页面可能展示比本机更高的 MATLAB 版本，实际以安装版本帮助与 options 为准。

## 官方文档

- [MathWorks surrogateopt](https://www.mathworks.com/help/gads/surrogateopt.html)：接口、有限边界、目标/约束与输出。
- [Surrogate Optimization Options](https://www.mathworks.com/help/gads/surrogate-optimization-options.html)：InitialPoints、采样选项、回调与停止条件。
- [Work with Checkpoint Files](https://www.mathworks.com/help/gads/work-with-checkpoint-files.html)：从原 options 修改允许字段并续跑。

HFSS 后端因工程而异；接入时读取已安装 AEDT 帮助或所用 PyAEDT 版本的官方接口文档，不假设另一个 Python 版本的方法签名相同。

## 参考开源 skill

- [matlab-solve-optimization](https://github.com/matlab/matlab-agentic-toolkit/blob/main/skills-catalog/math-and-optimization/matlab-solve-optimization/SKILL.md)：借鉴分类、配置、验证和按需参考的组织方式；不继承一般性的并行建议到共享 HFSS 工程。该文件采用其自身注明的 MathWorks 许可。
- [LZT001107/hfss-api-skill](https://github.com/LZT001107/hfss-api-skill/blob/master/SKILL.md)：借鉴先检查环境、再做单点任务的表达方式；不把 PyAEDT 迁移作为现有原生脚本工作流的先决条件。

本仓库独立编写文档和示例，没有复制上述 skill 的正文、脚本或许可证。本文件列出参考关系，不代表官方背书，也不声称发现了第三方即插即用的 surrogateopt–HFSS 优化服务。

## NGD 文献

- 陈道名、游彬，《基于特征多项式的负群时延滤波器设计方法》，2020。[DOI](https://doi.org/10.13954/j.cnki.hdu.2020.04.002)
- Ranjan Das, Qingfeng Zhang, Haiwen Liu, “Lossy Coupling Matrix Synthesis Approach for the Realization of Negative Group Delay Response,” IEEE Access, 6, 1916–1926, 2018。[DOI](https://doi.org/10.1109/ACCESS.2017.2780888)
- 相关早期预印本 “Synthesis of Negative Group Delay Using Lossy Coupling Matrix”： [arXiv:1708.02343v1](https://arxiv.org/abs/1708.02343v1)。标题/作者列表与正式出版版本有差别，引用时核对所读版本。这里不分发论文 PDF，也不将论文中的电磁验证描述为本 skill 的 HFSS 验证。
