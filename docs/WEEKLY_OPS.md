# 每周必做 · 项目运营清单（World Electronic Components）

面向仓库维护者。目标：**稳定扩库、可恢复、少踩坑**。

---当前进度快照（2026-07-14）---

| 项 | 状态 |
|----|------|
| 仓库架构 / taxonomy / schema | 已完成 |
| GitHub Pages 检索站 | 已完成 |
| 种子数据 + DigiKey 批量导入 | 约 **156** 条产品已在 `main` |
| DigiKey API（TMT Org App） | Production 已调通 |
| 每周自动采集 + 开 PR | 本文件 + `collect-digikey-weekly.yml` |
| MOSFET / 保险丝映射 | 待补（`param_synonyms`） |

站点：https://zhanhuiinhk.github.io/world-electronic-components/docs/  
仓库：https://github.com/zhanhuiinhk/world-electronic-components  

---

## 一、如何恢复 / 继续当前进度

### 1. 拉最新代码

```powershell
cd <你的工作目录>
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
# 若已有仓库：
cd world-electronic-components
git checkout main
git pull origin main
```

### 2. 本地密钥（不要提交）

```powershell
# 建议先在 DigiKey 后台重置曾泄露的 Secret
$env:DIGIKEY_CLIENT_ID = "你的ClientId"
$env:DIGIKEY_CLIENT_SECRET = "你的新ClientSecret"
$env:DIGIKEY_ENV = "production"
```

或：`copy scripts\collectors\env.example scripts\collectors\.env` 后编辑。

### 3. 确认环境正常

```powershell
python scripts/validate.py
python scripts/collectors/run_collect.py --dry-run --sub resistors --limit 3
python scripts/search.py STM32
```

### 4. 从「上次停下的地方」继续

| 你想做的事 | 命令 / 动作 |
|------------|-------------|
| 再采一类 | `python scripts/collectors/run_collect.py --env production --sub capacitors --limit 15` |
| 本机跑完整周任务 | `python scripts/collectors/run_weekly.py --env production --limit 10` |
| 看未合并的自动 PR | GitHub → **Pull requests** 搜 `weekly DigiKey` |
| 改搜索词 | 编辑 `scripts/collectors/query_map.json` |
| 改参数映射 | 编辑 `scripts/collectors/param_synonyms.json` |
| 校验 / 重建站点索引 | `python scripts/validate.py` 然后 `python scripts/build_catalog.py` |

### 5. 配置 GitHub Secrets（每周 CI 必需）

仓库 **Settings → Secrets and variables → Actions** 添加：

| Name | 值 |
|------|-----|
| `DIGIKEY_CLIENT_ID` | Portal 中的 Client ID |
| `DIGIKEY_CLIENT_SECRET` | **新** Client Secret（勿用聊天里泄露过的） |
| `DIGIKEY_ENV` | `production`（推荐）或 `sandbox` |

未配置时：周任务会 **跳过** 并打 warning，不会弄坏仓库。

### 6. 首次手动试跑周任务

1. GitHub → **Actions** → **Weekly DigiKey collect + PR**  
2. **Run workflow**  
3. 可先 `dry_run=true` 验证流程  
4. 再 `dry_run=false` 真采并看是否出现 PR  

---

## 二、每周必做（建议固定周一）

预计 **15–30 分钟**（CI 自动采完后你只审 PR）。

### 清单 A — 自动化已配置时（推荐）

- [ ] **1. 打开自动 PR**  
  Actions 每周一 UTC 02:00 会开 PR：`chore: weekly DigiKey component collect`  
  分支名：`chore/digikey-weekly-collect`

- [ ] **2. 看 Files changed**  
  关注 `data/**`、`manufacturers/**`、`docs/assets/data-manifest.json`

- [ ] **3. 确认 Checks**  
  `Validate component data` 是否绿

- [ ] **4. 抽查 3～5 个型号**  
  打开 `datasheet_url`；参数是否离谱（阻值、封装）

- [ ] **5. Merge 或关闭**  
  通过则 **Squash and merge**；明显错误则 Comment 后关 PR，本机修映射再采

- [ ] **6. 刷站点**  
  https://zhanhuiinhk.github.io/world-electronic-components/docs/  
  搜刚合并的型号（可能需等 Pages 部署 1–3 分钟）

- [ ] **7. 记一笔**（可选）  
  在 Issue「Weekly log」写：本周新增约 N 条、问题 1 句

### 清单 B — 本机手动周（无 CI 或 Secrets 未配）

```powershell
git pull
python scripts/collectors/run_weekly.py --env production --limit 10 --continue-on-error
python scripts/validate.py
# 看 diff
git status
git checkout -b chore/manual-weekly-collect
git add data manufacturers docs/assets
git commit -m "Weekly DigiKey collect (manual)"
git push -u origin HEAD
# 在 GitHub 开 PR 后自审合并
```

### 清单 C — 每周加分项（有空再做）

- [ ] 补 1 个映射：晶体管 / 保险丝（上次 accept=0）  
- [ ] 改 1 个 `query_map` 关键词，避免每周总是同一批 Top 结果  
- [ ] 给自动生成的厂家补官网 `website`  
- [ ] 关过期 PR / 回看 Issues  

---

## 三、工作流说明

| Workflow | 触发 | 作用 |
|----------|------|------|
| `collect-digikey-weekly.yml` | 每周一 02:00 UTC + 手动 | 全部分类采集 → 校验 → **开 PR** |
| `collect-digikey.yml` | 仅手动 | 单分类采集 → 可选开 PR |
| `validate.yml` | push / PR | 数据校验 |
| `pages.yml` | push main | 部署检索站 |

**不会**自动 merge 到 `main`，必须你（或协作者）审 PR。

---

## 四、安全提醒

- Client Secret **只**放在本机环境变量 / `.env` / GitHub Secrets  
- 曾在聊天暴露过的 Secret：**请在 DigiKey 后台重置**  
- 不要 `git add` 含密钥的文件  

---

## 五、出问题时

| 现象 | 处理 |
|------|------|
| 周任务 Skipped | 检查 Secrets 是否配置 |
| 401/403 | 重置 Secret；确认 `DIGIKEY_ENV=production` 与 App 类型一致 |
| PR 无文件变更 | API 结果与库内重复；换 `query_map` 关键词或提高多样性 |
| validate 红 | 看日志缺哪个 `attributes`；改 `param_synonyms.json` |
| 站点搜不到 | 等 Pages；确认 `data-manifest.json` 含新路径 |

更细的 API 说明见 [DIGIKEY_SETUP.md](./DIGIKEY_SETUP.md)。
