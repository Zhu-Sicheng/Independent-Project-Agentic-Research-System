# factorlab — Agent 驱动的因子挖掘流水线（初版）

从「若干年的量价数据」出发，自动完成：

```
数据面板
   │
   ▼
Agent 2.1 经济学假设（自然语言，不写代码）
   │
   ▼
Agent 2.2 因子实现（表达式 DSL 或逐日 python 脚本）
   │
   ▼
回测 + 网格搜索（decay / rank|sign / 市值过滤 / 时间窗口）
   │
   ▼
Agent 3 评审：接受 / 优化 / 放弃（结合假设合理性）
   │
   ▼
因子池（表达式 + 矩阵 + 绩效 + 截面/时序相关性）
```

真实数据已经接入：S&P 500 成分股 2000-2026 的日频量价与市值面板，point-in-time 成分过滤，
样本切分为 2000-2020（选择）/ 2021-2024（样本外）/ 2025+（真正样本外）。
没有 LLM key 时会自动退回规则版 agent，流程与接 LLM 后完全一致。

---

## 1. 快速开始

```powershell
# 0) 真实数据：原始 CSV -> 清洗后的面板（约 20 秒，输出 data/processed/）
python -m factorlab build-data --raw data/raw --out data/processed

# 1) 在真实数据上挖掘（自动使用 2000-2020 样本内 / 2021-2024 样本外 / 2025+ holdout）
python -m factorlab run --data data/processed/panel --hypotheses 3 --rounds 2 --max-evals 120 --offline

# 2) 查看因子池与相关性
python -m factorlab pool
```

合成数据（没有真实数据时用来跑通流程）：

```powershell
python -m factorlab gen-data
python -m factorlab demo --hypotheses 8 --rounds 2 --max-evals 100 --offline
```

产物：

```
runs/<run_id>/report.md      # 假设、每次尝试、网格最优配置、分年绩效、因子池
runs/<run_id>/attempts.jsonl # 每次尝试的完整 JSON 记录
runs/<run_id>/equity.png     # 入池因子的累计净值
pool/                        # 因子池（见第 7 节）
```

单表达式快速回测：

```powershell
python -m factorlab expr --expression="-rank(ts_mean(returns,5))" --transform none
python -m factorlab expr --expression="ts_std(returns,20)" --grid     # 走完整网格
```

> PowerShell 里以 `-` 开头的表达式要用 `--expression="..."` 的等号写法，否则会被当成参数名。
> 测试：`python -m unittest discover -s tests`（45 个用例）。

---

## 2. 目录结构

```
factorlab/
  config.py            # 全部可调参数：回测设置、网格空间、LLM、挖掘循环
  data/
    panel.py           # PanelStore：date x ticker 矩阵容器 + 派生字段
    loader.py          # 长表 / 宽表 / 按年分文件 的读取，统一成 PanelStore
    sample.py          # 合成数据生成器（带真实因子结构，无未来函数）
    us_equity.py       # 真实数据：逐票 CSV + 成分股区间 -> 面板 + 元数据
  expr/
    ops.py             # 算子注册表（同时是给 agent 的算子说明书）
    parser.py          # 表达式 tokenizer + 递归下降解析器 + AST 改写
    evaluator.py       # AST 在面板上求值
    validate.py        # 静态校验：字段、算子、窗口、复杂度
    script.py          # 逐日 python 脚本的校验与受限执行
    spec.py            # FactorSpec：表达式/脚本的统一载体（可哈希、可序列化）
  backtest/
    engine.py          # 因子矩阵 -> 权重 -> 日频 pnl，含分年绩效
    metrics.py         # sharpe / turnover / maxdd / IC / 截面 spearman / 时序 pearson
    grid.py            # 网格搜索 + 窗口替换 + 结果排名
    split.py           # 样本内 / 样本外 / holdout 切分与分段绩效
  agents/
    llm.py             # OpenAI 兼容 / Anthropic / 离线 三种客户端
    prompts.py         # 三个 agent 的 system / user prompt 模板
    hypothesis.py      # Agent 2.1 经济学家：数据 -> 假设
    implementer.py     # Agent 2.2 实现者：假设 -> 表达式/脚本
    critic.py          # Agent 3 研究总监：接受 / 优化 / 放弃
    fallback.py        # 无 LLM 时的规则版研究库
  pool/
    pool.py            # 因子池存储 + 相关性计算
  orchestrator.py      # 挖掘主循环、日志、报告、净值图
  cli.py               # 命令行入口
docs/
  agent_contracts.md   # 2.1 / 2.2 / 3 的 JSON 接口契约
```

---

## 3. 数据模块

### 3.1 真实数据（CRSP 风格美股）

原始数据在 `data/raw/`：1200 个 CSV，逐票 `s<permno>.csv`（`Adj_Open/High/Low/Close/Volume/MktCap`），
外加 `MASTER_UNIVERSE_sp500_membership_extended_asOf20260930_v2.csv`（成分股进出区间）、
`permno_to_ticker_mapping.csv`（permno → ticker）、`security_master...csv`（GICS 行业）和 SPY 行情。

一条命令把原始文件清洗成研究面板：

```powershell
python -m factorlab build-data --raw data/raw --out data/processed
```

输出：

```
data/processed/
  panel/
    open.parquet high.parquet low.parquet close.parquet volume.parquet cap.parquet
  meta/
    security_master.csv          # permno / ticker / gvkey / GICS
    universe_intervals.csv       # permno, start_date, end_date（point-in-time）
    manifest.json                # 规模、覆盖率、收益分布、默认切分
```

每个 parquet 就是一张 **index=日期、columns=permno** 的矩阵，float32 + zstd。
当前规模：**6726 个交易日（2000-01-03 → 2026-09-30）× 1195 只股票**，每日约 502 只在成分内，
字段覆盖率 42%（分母是"全历史出现过的股票"，分子是"当天确实是成分股"）。

**清洗规则**（`factorlab/data/us_equity.py`）：

| 步骤 | 处理 |
|---|---|
| 价格口径 | 直接用数据商的 `Adj_*`（已做拆股与分红调整），不再二次复权 |
| 成分股 | 只在 `start_date <= t <= end_date` 的区间内保留该股票，退市后自然消失，**无幸存者偏差** |
| 非法值 | `close/high/low/open <= 0`、`volume <= 0`、`cap <= 0` 置 NaN；表内已无零成交量 |
| 重复 | 同一 `(permno, date)` 去重保留最后一条 |
| 缺失 | **不做前向填充**；停牌/未上市就是 NaN，由因子和回测按缺失处理 |
| 代码变更 | 列用 permno（稳定），ticker 会复用（43 个重名），映射表放 `meta/security_master.csv` |
| 派生字段 | `returns`、`log_returns`、`amount = close*volume`、`adv20`、`cap_rank` 在 `PanelStore` 中按需生成 |

数据体检（`manifest.json` 里有完整结果）：每日 498–508 只成分股；日收益均值 0.048%、标准差 2.4%；
`|ret| > 50%` 的样本 90 个（占 3.4M 的 0.003%），集中在 2008 年金融危机与个别并购/逼空日，
保留了未删除——是否要截尾应该在回测口径里决定，而不是在数据层偷偷改。

### 3.2 读取

```python
from factorlab.data import load_processed

panel = load_processed("data/processed/panel")   # PanelStore
panel.field("close")                             # DataFrame(date x permno)
panel.field("returns")                           # 派生
panel.summary()
panel.meta["default_split"]                      # 数据自带的切分约定
```

通用格式（长表 / 宽表 / 按年分文件）仍然走 `load_panel()`：

```python
from factorlab.data import load_panel
panel = load_panel("data/other")     # date+ticker 长表，或一个字段一个文件
```

`y`（预测目标）默认 `close_to_close`，即 `close_t / close_{t-1} - 1`；
在 `BacktestSettings(y=...)` 里可以换成任意价格字段（会取 pct_change）。

### 3.3 样本切分（已按约定设好）

数据自带 `default_split`，`MiningLoop` 会自动使用：

| 段 | 区间 | 用途 |
|---|---|---|
| 样本内 `is` | 2000-01-03 → 2020-12-31（5284 天） | **唯一**用于网格搜索选参数 |
| 样本外 `oos` | 2021-01-04 → 2024-12-31（1005 天） | 验证，不参与选择 |
| 真正样本外 `holdout` | 2025-01-02 → 2026-09-30（437 天） | 最后一关，平时不看 |

想显式覆盖：`--train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01`。

---

## 4. 因子表达式语言

### 4.1 语法

- 算术：`+ - * / ^`，一元 `-`，比较 `> < >= <= == !=`，逻辑 `& | !`（也可写 `&& ||`）
- 常量：`nan`、`inf`、`true`、`false`
- 函数调用：`rank(x)`、`ts_mean(x, 20)`、`if_else(cond, a, b)`

示例：

```text
-ts_mean(returns, 5)
-rank(ts_std(returns, 20))
ts_returns(close, 20) / ts_std(returns, 60)
if_else(rank(cap) > 0.3, -ts_mean(returns, 20), nan)
-ts_corr(close, volume, 20) * ts_rank(volume, 60)
```

### 4.2 算子

| 类别 | 算子 |
|---|---|
| element-wise | `abs sign log log1p sqrt exp signed_power clip nan_to_num max min` |
| cross-sectional（逐日截面） | `rank`（pct 排名 0~1）`zscore demean scale winsorize` |
| time-series（逐股票时序） | `delay delta ts_returns ts_sum ts_mean ts_std ts_min ts_max ts_median ts_skew ts_kurt ts_rank ts_zscore ts_ir ts_argmax ts_argmin ts_corr ts_cov ts_decay_linear` |
| conditional | `if_else(cond,a,b) mask(x,cond)` |

`rank` 是按日截面排名，`ts_*` 是逐股票滚动。滚动窗口的 `min_periods = max(3, d//2)`。

### 4.3 时间窗口规则

只允许 `5 / 20 / 60 / 120 / 240` 天（`config.ALLOWED_WINDOWS`）。
表达式中出现其他窗口会在校验阶段直接报错，网格搜索也只会在这几个值里替换。
脚本因子的 `param_grid` 若不是这几个值，会给 warning（允许非窗口参数）。

### 4.4 逐日 python 脚本因子

当因子需要表达式表达不了的截面迭代逻辑时，Agent 2.2 可以交脚本：

```python
def generate(panel, params):
    window = int(params.get("window", 5))
    r = panel.field("returns")
    rel = panel.field("volume") / panel.field("volume").rolling(20).mean()
    num = (r * rel).rolling(window, min_periods=max(2, window // 2)).sum()
    den = rel.rolling(window, min_periods=max(2, window // 2)).sum()
    return -(num / den)
```

约定：

- 必须定义 `generate(panel, params)`（或 `generate(panel)`），返回 `date x ticker` 的 DataFrame；
- 命名空间里只有 `pd`、`np`、`math`、`PARAMS` 和少量安全 builtin；**禁止 import、文件、网络、dunder 访问**；
- 可调窗口写在 `param_grid`，例如 `{"window": [5, 20, 60]}`，网格会遍历；
- 输出会按面板的日期/股票对齐，非数值列和非 DataFrame 返回值直接报错。

> 这是「护栏」不是「沙箱」：能防住 LLM 的常见越界，但挡不住蓄意攻击。真要跑不可信代码，请把整个进程放进容器。

---

## 5. 回测与网格搜索

### 5.1 口径

```
原始因子
  → 市值过滤    if_else(rank(cap) > 0.3, f, nan)     # 丢掉最小 30%
  → 截面变换    none / rank / sign / zscore
  → 时间衰减    linear decay，最近一天权重最大
  → 截面去均值  w = f - mean(f)                     # 美元中性
  → 归一化      w = w / sum(|w|)                    # 1 倍总敞口
  → pnl         pnl_t = Σ w_{t-1,i} · r_{t,i}       # delay=1，无未来函数
```

- turnover（单边）= `0.5 * Σ|w_t - w_{t-1}|`，指标里乘 252 年化；
- 成本 = `cost_bps/1e4 * Σ|Δw|`（默认 0，可设）；
- 指标：`sharpe ann_return ann_vol total_return max_drawdown turnover hit_rate ic ic_ir fitness n_names`，另加**分年**的 return / sharpe / turnover / maxdd / IC；
- `fitness = sharpe * sqrt(|ann_return| / max(turnover, 0.125))`（BRAIN 口径，便于横向比较）。

### 5.2 网格空间

| 维度 | 取值 |
|---|---|
| decay | `0, 5, 20, 60`（0 = 不衰减） |
| 截面变换 | `none, rank, sign`（`zscore` 可选） |
| 市值过滤 | `none`，或丢掉最小 30%（`cap_filter=0.3`） |
| 表达式窗口 | 每个窗口槽位在 `5, 20, 60, 120, 240` 中重取 |
| 脚本参数 | 由 `param_grid` 声明 |

默认 `max_evals=200`：窗口组合过多时先做「基准 + 单窗口坐标扫描」，再随机补足；
每个配置都完整回测，按 `sharpe` 排序（同分看 turnover）。IC 只在排名靠前的配置上重算，用于提速。

### 5.3 样本内 / 样本外 / 真正样本外

三段切分，全部是**日期闭区间**：

| 段 | 字段 | 区间 | 用途 |
|---|---|---|---|
| 样本内 | `is` | 2000-01-03 → 2020-12-31 | **唯一**参与网格搜索选参数 |
| 样本外 | `oos` | 2021-01-04 → 2024-12-31 | 验证，不参与选择 |
| 真正样本外 | `holdout` | 2025-01-02 → 2026-09-30 | 最后一关 |

这组日期写在 `data/processed/meta/manifest.json::default_split` 里，`MiningLoop` 自动读取；
也可以显式覆盖：

```python
from factorlab.config import SampleSplit

SampleSplit(
    train_end="2020-12-31",
    test_start="2021-01-01", test_end="2024-12-31",
    holdout_start="2025-01-01",
)
# 或按比例：SampleSplit(train_frac=0.8, holdout_start="2025-01-01")
```

```powershell
python -m factorlab run --data data/processed/panel --hypotheses 5 `
  --train-end 2020-12-31 --oos-start 2021-01-01 --oos-end 2024-12-31 --holdout-start 2025-01-01
```

协议（`factorlab/backtest/split.py`）：

1. 因子矩阵始终在**全样本**上计算。因子是因果的（第 t 行只用 ≤t 的数据），
   所以样本外/真正样本外不会因为「因子在这段上算」而偷看未来；
2. 网格搜索的窗口/decay/rank/sign/市值过滤**只在样本内**打分排序；
3. 选出的配置原封不动地在另外两段重跑，三段指标都存、都报；
4. 切的是 **pnl 序列**而不是重算子面板，因此没有 rolling 预热损耗，
   样本外第一天的换手也按真实持仓变化计算；
5. 不切分时退回全样本选择，额外两段为空——不会编造。

落库位置：

- 网格表：`sharpe_is` / `sharpe_oos` / `sharpe_holdout`（以及 `ann_return_*`、`turnover_*`、`max_drawdown_*`、`ic_*`）
- 因子池：`meta.json` 的 `segments.is` / `segments.oos` / `segments.holdout`，`pool summary` 多出对应两列
- 报告：决策表多 `sharpe IS` / `sharpe OOS` / `sharpe Holdout` 三列，每个因子下面三段指标 + 分段分年表

Agent 3 以**样本内**做判断，用另外两段做过拟合检查：两段中任意一段为负、或平均回吐超过样本内优势的 60%，
直接判过拟合并放弃。LLM 的 prompt 同样写明「holdout 是最后一关，样本内好看但样本外塌掉的必须放弃」。


---

## 6. 三个 Agent（2.1 / 2.2 / 3）

| Agent | 类 | 输入 | 输出 |
|---|---|---|---|
| **2.1 经济学家** | `HypothesisAgent` | 数据画像（字段覆盖率/分布/自相关）、因子池已有因子、已试过并失败的假设 | 若干条假设：机制、方向、horizon、可证伪预测、自然语言因子配方 |
| **2.2 实现者** | `ImplementationAgent` | 2.1 的假设 + 字段表 + 算子说明书 + 窗口规则 | `FactorSpec`：表达式或脚本 + 解释；校验失败会带着错误信息重试 |
| **3 研究总监** | `CriticAgent` | 2.1 的假设 + 2.2 的实现 + 网格汇总 + 分年绩效 + 历史尝试 | `accept / optimize / abandon` + 诊断 + 最多一个结构性修改（改符号、换窗口、平滑） |

**2.1 与 2.2 的边界**：2.1 只产出经济学故事和自然语言配方，**不写任何代码**；
2.2 承担全部实现问题（表达式还是脚本、选哪些字段/算子/窗口）。
这样拆的收益是两者可以独立替换与独立重试：换经济学家不动执行层，
换执行层（比如以后接 WorldQuant BRAIN 的表达式方言）不动研究逻辑。
接口契约（JSON schema）见 `docs/agent_contracts.md`。

Agent 3 的修改只作用于**表达式结构**——decay / rank / sign / 市值过滤已经由网格搜索过了，不重复建议。
`optimize` 会带着新 spec 回到 Agent 2.2 → 重新回测，最多 `max_rounds` 轮。

### 6.1 接 LLM

```powershell
$env:DEEPSEEK_API_KEY="sk-..."                 # 或 OPENAI_API_KEY / ANTHROPIC_API_KEY
$env:FACTORLAB_LLM_PROVIDER="openai"           # openai | anthropic | offline | auto
$env:FACTORLAB_LLM_BASE_URL="https://api.deepseek.com/v1"
$env:FACTORLAB_LLM_MODEL="deepseek-chat"
python -m factorlab run --hypotheses 5 --rounds 2
```

`provider=auto` 时会按 key 自动选择；没有任何 key 时自动退回离线规则库，
三个 agent 的接口、校验、日志完全一致，所以离线跑出来的流程和接 LLM 后是同一条。

### 6.2 离线规则库

`agents/fallback.py` 里是 8 条手写的经济学假设（短期反转、低波动、Amihud 非流动性、成交量冲击、
成交量加权反转（脚本）、隔夜跳空、区间压缩、量价背离），配套实现模板和评审阈值。
它的作用是让整条流水线在没有 key 时可测试、可演示——不是给 LLM 擦屁股的假实现。

---

## 7. 因子池

```
pool/
  index.json                     # 所有因子记录（spec / 假设 / 绩效 / 分年 / 配置 / 相关性）
  correlations.csv               # 两两相关性长表
  factors/<name>-<fingerprint>/
      meta.json                  # 单因子完整记录
      factor.parquet             # 最优配置下的原始因子矩阵（float32）
      pnl.parquet                # 日 pnl + turnover
      grid.parquet               # 网格搜索明细（前 100 行）
```

因子 id = `名字-slug + spec 内容 sha1 前 8 位`，同一份 spec 重复入库是幂等的。

**两种相关性都会算、都会存，但不设阈值**：

- 截面：两个因子矩阵逐日截面 Spearman 的均值（`xs_spearman_mean`，另有 std / 天数）；
- 时序：两条日 pnl 的 Pearson（`pnl_pearson`，按共同交易日）。

新增因子时会和池内每个因子算一遍并**双向**写回（两侧 meta 都更新 `max_abs_xs_corr` / `max_abs_pnl_corr`），
同时 `pool.recompute_correlations()` 可全量重算。是否因为相关性高而拒绝，留给后续策略/人来定。

```python
from factorlab.pool import FactorPool
pool = FactorPool("pool")
pool.summary()                     # DataFrame：id/name/sharpe/turnover/IC/max_corr...
pool.load_factor(fid)              # 因子矩阵
pool.load_pnl(fid)                 # 日 pnl
pool.correlations()                # 两两相关性
pool.report()                      # markdown
```

示例（合成数据，离线 8 个假设、入池 5 个）：

| 相关性 | factor A | factor B | xs spearman | pnl pearson |
|---|---|---|---|---|
| 同一信号 | short_term_reversal | volume_weighted_reversal | 0.913 | 0.921 |
| 同一信号 | low_volatility_anomaly | range_compression_breakout | 0.756 | 0.754 |
| 独立 | short_term_reversal | range_compression_breakout | -0.020 | 0.010 |

最后一行正是因子池的价值：`range_compression` 名字听起来是「区间压缩」，实际和低波动因子高度重合；
而「成交量加权反转」虽然实现方式（脚本）完全不同，和普通反转其实是同一个信号。

---

## 8. 已知限制 / 下一步

1. **真实数据**：`loader` 已支持长表/宽表/按年分文件，但字段映射和 `y` 还需要按真实数据确认；
   拿到数据后建议先跑 `panel.summary()` 看覆盖率和极值。
2. **只有量价**：没有行业、市值中性化、财务因子；`group_*` 类算子和行业中性化是明确的扩展点。
3. **成本**：默认 0，`cost_bps` 可开；网格目前不对成本做敏感性分析。
4. **统计**：单次样本外切分已支持（见 5.3），但还没有 walk-forward 滚动验证，
   也没有多重检验校正（Deflated Sharpe / White's Reality Check）；
   网格 200 次搜索本身就会抬高最优 Sharpe，后续应加入选择偏差惩罚。
5. **脚本沙箱**：静态检查 + 受限 builtins，非强隔离，生产环境请用容器。
6. **并发**：网格是串行的；单因子 200 次回测在 300x1800 面板上约 20 秒，因子多了可以并行/缓存。
7. **Agent 记忆**：目前只把「已入库因子 + 本次已试假设」喂给 Agent 2.1，跨 run 的失败经验还没有持久化。
