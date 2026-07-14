# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 DigiKey、Mouser、Arrow 同类项。

## 对外网站（访客看到的内容）

**检索站：** https://zhanhuiinhk/github.io 请使用正式地址：  
https://zhanhuiinhk.github.io/world-electronic-components/  
（或 `/docs/` 路径下的检索页）

对外站点**只展示**：产品检索、公开说明、分类与参数介绍。  
**不对外展示**（仅在本 GitHub 仓库中给协作者看）：开发命令、目录结构、CI、CSV 导入脚本说明等。

> 若首页仍显示本 README 全文，请到仓库 **Settings → Pages**：
> - 推荐：**Source = GitHub Actions**（使用 `.github/workflows/pages.yml`），或  
> - **Deploy from branch** → Branch `main` → Folder **`/docs`**  
> 不要用「根目录 / root」直接发布，否则会把 README 当成网站首页。

## 协作者快速开始（仅仓库内）

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components
python scripts/validate.py
python scripts/search.py STM32
python scripts/build_catalog.py
python -m http.server 8080 --directory docs
```

- CSV 导入：`python scripts/csv_to_json.py examples/import-template.csv -o data/...`
- 品类参数表：`schema/attribute-profiles.json`
- 厂家入驻：`docs/MANUFACTURER_ONBOARDING.md`（仓库 Markdown，非站点营销页）
- 分类扩项：`docs/TAXONOMY.md`

## 许可证

[MIT](LICENSE)
