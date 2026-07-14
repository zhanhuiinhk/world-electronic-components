# DigiKey API 申请与采集脚手架

本仓库已内置 **DigiKey → WEC 格式** 自动采集工具。申请 API 成功后即可按分类批量拉取产品。

> DigiKey 对个人/企业开发者通常**免费**提供 API（需注册、创建 App、遵守用量与条款）。是否审核通过以官方为准；下文给出申请技巧与失败时的退路。

## 1. 申请步骤（尽量提高通过率）

1. 打开 [DigiKey Developer Portal](https://developer.digikey.com/) 并登录/注册 DigiKey 账号。  
2. 创建 **Organization**（组织）——生产接口通常挂在 Organization 的 Production App 下。  
3. 创建应用（App）：
   - **Sandbox App**：用于联调（数据可能是假数据/不完整，但协议与字段结构可用）  
   - **Production App**：真实产品数据（推荐最终使用）  
4. 记下：
   - `Client ID`
   - `Client Secret`
5. 本脚手架使用 **OAuth 2.0 Client Credentials（2-legged）**，机器对机器，无需用户浏览器登录。  
6. 阅读并接受 [API Terms](https://developer.digikey.com/) 中的使用限制（禁止滥用、注意 rate limit）。

### 申请填写建议（提高成功率）

| 项 | 建议写法 |
|----|----------|
| 用途 | Open-source electronic component database for engineers; non-commercial catalog aggregation |
| 应用名 | World Electronic Components / your-github-username |
| 网站 | `https://github.com/zhanhuiinhk/world-electronic-components` 或你的 Pages 站点 |
| 回调 URL | 2-legged 可不强依赖；若要求可填 `https://localhost` 或 `https://localhost:8139/digikey_callback` |
| 使用场景 | Keyword search by category → normalize → validate → PR into open data repo |

### 若申请失败 / 很久未批

- 先用 **Sandbox App** 把流水线跑通（`--env sandbox`）  
- 用仓库已有 **CSV 导入** / 手工 JSON 继续扩库  
- 稍后补充公司信息或改用企业邮箱再申请 Production  
- 备选：Mouser API、Nexar（Octopart）等同类源（脚手架可后续扩展）

## 2. 本机配置密钥

**不要**把 Secret 提交进 Git。

### Windows PowerShell（当前会话）

```powershell
$env:DIGIKEY_CLIENT_ID = "你的ClientId"
$env:DIGIKEY_CLIENT_SECRET = "你的ClientSecret"
# 可选：production（默认）或 sandbox
$env:DIGIKEY_ENV = "sandbox"
```

### 或使用本地文件（已被 .gitignore）

复制示例：

```bash
copy scripts\collectors\env.example scripts\collectors\.env
# 编辑 .env 填入 ID/SECRET
```

## 3. 命令用法

依赖：Python 3.10+，仅标准库（无需 pip 安装额外包）。

```bash
# 干跑：不调 API，用内置样例 JSON，验证映射与写入逻辑
python scripts/collectors/run_collect.py --dry-run --sub resistors --limit 5

# Sandbox 真调 API（需 Key）
python scripts/collectors/run_collect.py --env sandbox --sub resistors --limit 10

# 生产环境，按二级分类拉取并合并到 data/
python scripts/collectors/run_collect.py --env production --sub microcontrollers --limit 20

# 只写到临时目录，不碰 data/
python scripts/collectors/run_collect.py --dry-run --sub capacitors --out-dir _collect_out

# 拉取后自动校验
python scripts/collectors/run_collect.py --dry-run --sub resistors --validate
```

参数摘要：

| 参数 | 含义 |
|------|------|
| `--sub SLUG` | taxonomy 二级 slug，如 `resistors`、`microcontrollers` |
| `--limit N` | 最多保留 N 条（映射成功且过规则） |
| `--env` | `sandbox` / `production` |
| `--dry-run` | 使用 `fixtures/sample_keyword_search.json`，不访问网络 |
| `--out-dir` | 输出根目录，默认仓库根（写入 `data/` 与 `manufacturers/`） |
| `--validate` | 结束后调用 `scripts/validate.py` |
| `--no-merge` | 不与已有 JSON 合并，整文件覆盖同 mfr 文件（慎用） |

## 4. 数据流

```text
taxonomy 二级类 → 搜索关键词
       ↓
DigiKey KeywordSearch (V4)
       ↓
map_to_wec（字段 + 参数同义词 → attribute-profiles）
       ↓
manufacturers/{id}.json  +  data/{category}/{id}.json
       ↓
validate.py  +  build_catalog / 站点 manifest
```

映射规则见：`scripts/collectors/query_map.json`、`param_synonyms.json`。

## 5. GitHub Actions（可选）

工作流：`.github/workflows/collect-digikey.yml`

仓库 **Settings → Secrets and variables → Actions** 添加：

- `DIGIKEY_CLIENT_ID`
- `DIGIKEY_CLIENT_SECRET`
- `DIGIKEY_ENV` = `production` 或 `sandbox`

可 `workflow_dispatch` 手动触发；默认 **不会** 在未配置 Secret 时硬失败（会跳过）。

> 建议：Action 只提交到分支或开 PR，不要无审直接推 `main`。当前工作流写入 `collect/branch` 产物目录供下载，你本地合并更安全。

## 6. 合规与质量

- 遵守 DigiKey API 配额与缓存策略（关键词结果可能有延迟）  
- 参数以官方手册为准；API 字段缺失时会跳过「必填 attributes」不满足的条目  
- 不要高频扫全站；按分类、limit 分批  
- 商标与型号归原厂；本库 MIT 仅覆盖仓库内整理结构  

## 7. 故障排查

| 现象 | 处理 |
|------|------|
| `401/403` | Client ID/Secret 错误，或 Sandbox Key 调了 Production 域名 |
| 空结果 | 换关键词；Sandbox 数据不全；改 `--env production` |
| validate 失败 | 看缺的 `attributes.*`；补充 `param_synonyms.json` |
| 厂家文件冲突 | 脚本按 `manufacturer_id` 合并数组，以 part_number 去重 |

## 8. 下一步

1. 完成 Portal 注册，拿到 Sandbox Key  
2. 本地：`run_collect.py --env sandbox --sub resistors --limit 5`  
3. 通过后改 Production，按分类扩大 `limit`  
4. 需要时再加 Mouser collector（同一 `map_to_wec` 接口）  
