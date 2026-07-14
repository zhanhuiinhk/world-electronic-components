# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 DigiKey、Mouser、Arrow 同类项。

## 对外网站（访客）

https://zhanhuiinhk.github.io/world-electronic-components/  
（推荐打开 https://zhanhuiinhk.github.io/world-electronic-components/docs/ ）

| 访客可见 | 仅 GitHub 仓库内（协作者） |
|----------|---------------------------|
| 产品检索 | `scripts/` 校验/导入/构建 |
| 关于/分类/参数说明 | 目录结构、CI、CSV 模板 |
| 公开产品数据摘要 | `CONTRIBUTING.md` 等协作细则 |

### 若首页仍显示本 README

仓库 **Settings → Pages**：

1. **推荐**：Source = **GitHub Actions**（`.github/workflows/pages.yml` 发布 `docs/`）  
2. 或：Deploy from branch → `main` → Folder = **`/docs`**  
3. **不要**用根目录发布（否则 README 会变成网站首页）

根目录已放置 `index.html`，在「根目录发布」模式下会跳转到 `docs/` 检索页。

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
