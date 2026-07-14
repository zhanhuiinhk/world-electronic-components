# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 DigiKey、Mouser、Arrow 同类项。

## 对外网站

https://zhanhuiinhk.github.io/world-electronic-components/docs/

| 访客可见 | 协作者（本仓库） |
|----------|------------------|
| 产品检索 | DigiKey 采集、校验、周任务 |
| 公开说明 | `docs/WEEKLY_OPS.md` 运营清单 |

## 维护者：恢复进度 + 每周必做

请直接阅读：

- **[docs/WEEKLY_OPS.md](docs/WEEKLY_OPS.md)** — 如何恢复、Secrets、每周清单  
- **[docs/DIGIKEY_SETUP.md](docs/DIGIKEY_SETUP.md)** — API 申请与命令  

### 一分钟本地确认

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components
python scripts/validate.py
python scripts/collectors/run_collect.py --dry-run --sub resistors --limit 3
```

### 每周自动采集

配置 Actions Secrets（`DIGIKEY_CLIENT_ID` / `DIGIKEY_CLIENT_SECRET` / `DIGIKEY_ENV`）后：

- 工作流 **Weekly DigiKey collect + PR** 每周一自动跑  
- 结果以 **Pull Request** 形式提交，**需人工合并**  

## DigiKey 采集命令

```bash
# 单分类
python scripts/collectors/run_collect.py --env production --sub resistors --limit 10

# 全部分类（与周任务相同）
python scripts/collectors/run_weekly.py --env production --limit 10 --continue-on-error
```

## 其它命令

```bash
python scripts/search.py STM32
python scripts/build_catalog.py
python scripts/csv_to_json.py examples/import-template.csv -o data/passive-components/demo.json
```

## 许可证

[MIT](LICENSE)
