# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 DigiKey、Mouser、Arrow 同类项。

## 对外网站（访客）

https://zhanhuiinhk.github.io/world-electronic-components/  
（推荐：https://zhanhuiinhk.github.io/world-electronic-components/docs/ ）

| 访客可见 | 仅 GitHub 仓库内（协作者） |
|----------|---------------------------|
| 产品检索 | `scripts/` 校验/导入/采集 |
| 关于/分类/参数说明 | DigiKey 自动采集脚手架 |

### 若首页仍显示本 README

**Settings → Pages**：Source 用 **GitHub Actions**，或 Deploy from branch → `main` → **`/docs`**。

## DigiKey 自动采集（推荐）

申请 API 与用法见：**[docs/DIGIKEY_SETUP.md](docs/DIGIKEY_SETUP.md)**

```bash
# 无 Key 也可先验证流水线
python scripts/collectors/run_collect.py --dry-run --sub resistors --limit 5

# 申请到 Key 之后
# set DIGIKEY_CLIENT_ID / DIGIKEY_CLIENT_SECRET / DIGIKEY_ENV=sandbox
python scripts/collectors/run_collect.py --env sandbox --sub resistors --limit 10
```

## 协作者命令

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components
python scripts/validate.py
python scripts/search.py STM32
python scripts/build_catalog.py
python scripts/csv_to_json.py examples/import-template.csv -o data/passive-components/demo.json
```

- 品类参数：`schema/attribute-profiles.json`  
- 厂家入驻：`docs/MANUFACTURER_ONBOARDING.md`  
- 分类扩项：`docs/TAXONOMY.md`  

## 许可证

[MIT](LICENSE)
