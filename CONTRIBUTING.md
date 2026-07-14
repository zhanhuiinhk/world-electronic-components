# 贡献指南 (Contributing Guide)

感谢关注 **World Electronic Components Database**。

## 文档与站点

| 语言 | 在线文档 | 仓库 Markdown |
|------|----------|----------------|
| 中文 | `/zh/` on GitHub Pages | `docs/TAXONOMY.md`, `docs/MANUFACTURER_ONBOARDING.md` |
| English | `/en/` on GitHub Pages | same files (Chinese primary; EN pages on site) |

在线检索：GitHub Pages 根路径 `/`。

## 常用工具

```bash
# 校验（含品类 attributes 必填）
python scripts/validate.py

# 搜索
python scripts/search.py NE555

# CSV 批量导入
python scripts/csv_to_json.py your.csv -o data/{category}/{mfr}.json

# 构建 Pages 数据目录
python scripts/build_catalog.py
```

## 品类专用 attributes

见 `schema/attribute-profiles.json`。例如 `resistors` **必须**提供 `attributes.resistance_ohm`。  
未配置 profile 的二级分类不强制 attributes 字段。

## 厂家入驻 / 分类扩项

- [厂家入驻](docs/MANUFACTURER_ONBOARDING.md) — 无白名单，Fork + PR  
- [分类扩项](docs/TAXONOMY.md) — 二级 PR；一级 Issue  

## 目录约定

```text
manufacturers/{manufacturer_id}.json
data/{category_slug}/{manufacturer_id}.json
```

PR 模板检查清单见 `.github/PULL_REQUEST_TEMPLATE.md`。CI 会运行 `validate.py` 与 `build_catalog.py`。
