# DigiKey API 申请与采集脚手架

本仓库已内置 **DigiKey → WEC 格式** 自动采集工具。申请 API 成功后即可按分类批量拉取产品。

**每周运营清单（恢复进度 + 必做项）→ [WEEKLY_OPS.md](./WEEKLY_OPS.md)**

> DigiKey 对个人/企业开发者通常**免费**提供 API（需注册、创建 App、遵守用量与条款）。

## 1. 申请步骤（尽量提高通过率）

1. 打开 [DigiKey Developer Portal](https://developer.digikey.com/) 并登录/注册。  
2. 创建 **Organization**，再建 **Production App**（真数据）与可选 Sandbox。  
3. 记下 `Client ID` / `Client Secret`。  
4. 本脚手架使用 **OAuth 2.0 Client Credentials（2-legged）**。  

用途建议：`Open-source non-commercial component catalog; keyword search by category → normalize → validate → GitHub PR`。

若 Secret 曾泄露：**立即在 Portal 重置**，旧密钥作废。

## 2. 本机配置密钥

**不要**把 Secret 提交进 Git。

```powershell
$env:DIGIKEY_CLIENT_ID = "你的ClientId"
$env:DIGIKEY_CLIENT_SECRET = "你的ClientSecret"
$env:DIGIKEY_ENV = "production"
```

或：`copy scripts\collectors\env.example scripts\collectors\.env`（已 gitignore）。

## 3. 命令用法

```bash
# 干跑
python scripts/collectors/run_collect.py --dry-run --sub resistors --limit 5

# 单分类生产采集
python scripts/collectors/run_collect.py --env production --sub resistors --limit 10

# 每周同款：全部分类
python scripts/collectors/run_weekly.py --env production --limit 10 --continue-on-error
```

| 参数 | 含义 |
|------|------|
| `--sub SLUG` | 二级分类，见 `query_map.json` |
| `--limit N` | 每类最多保留条数 |
| `--env` | `sandbox` / `production` |
| `--dry-run` | 不访问网络 |

## 4. GitHub Actions

| Workflow | 说明 |
|----------|------|
| **Weekly DigiKey collect + PR** | 每周一自动全量分类采集并 **开 PR** |
| **Collect DigiKey (manual)** | 手动单分类，可选开 PR |

### Secrets（Settings → Secrets → Actions）

| Name | 值 |
|------|-----|
| `DIGIKEY_CLIENT_ID` | Client ID |
| `DIGIKEY_CLIENT_SECRET` | Client Secret（用重置后的） |
| `DIGIKEY_ENV` | `production` 或 `sandbox` |

未配置 Secrets 时周任务会跳过，不破坏仓库。

### 审 PR

1. 打开自动 PR `chore: weekly DigiKey component collect`  
2. 看 diff + Checks  
3. 通过后 Merge  

## 5. 数据流

```text
query_map 分类 → DigiKey KeywordSearch
  → map_to_wec + attribute-profiles
  → manufacturers/ + data/
  → validate + build_catalog
  → Pull Request（不自动进 main）
```

## 6. 故障排查

| 现象 | 处理 |
|------|------|
| 401/403 | Secret 错误或已重置未更新 Secrets |
| 空结果 | 换关键词；检查 Production App |
| validate 失败 | 补 `param_synonyms.json` |
| 周任务 skip | 未配置 Secrets |

## 7. 合规

遵守 DigiKey 配额与条款；参数以官方手册为准；按分类分批，勿高频扫全站。
