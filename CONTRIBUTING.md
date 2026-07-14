# 贡献指南 (Contributing Guide)

感谢关注 **World Electronic Components Database**。

本库支持三类协作：

1. **查询使用** — 搜索已有元器件 / 部件 / 组件数据  
2. **厂家入驻** — 新厂家登记品牌并提交产品  
3. **分类扩项** — 在官方 taxonomy 上增加二级或（经讨论后）一级分类  

详细文档：

- [厂家入驻通道](docs/MANUFACTURER_ONBOARDING.md)  
- [分类体系与扩项规则](docs/TAXONOMY.md)  
- 权威分类树：[`taxonomy/categories.json`](taxonomy/categories.json)（当前 **v2**，对齐 DigiKey / Mouser / Arrow 合并结果）

## 目录约定

```text
manufacturers/{manufacturer_id}.json
data/{category_slug}/{manufacturer_id}.json
taxonomy/categories.json
schema/
scripts/search.py
scripts/validate.py
```

## 厂家入驻（摘要）

1. Fork 本仓库  
2. 复制 `manufacturers/_template.json` → `manufacturers/{id}.json`  
3. 在 `data/{category_slug}/` 提交产品 JSON 数组  
4. `python scripts/validate.py` 通过后开 PR  

**不需要事先申请白名单**；有公开 datasheet 即可走 PR。批量导入可开 Issue（模板 *Manufacturer onboarding*）。

### 产品字段

| 字段 | 说明 |
|------|------|
| `part_number` | 官方型号 |
| `manufacturer` / `manufacturer_id` | 厂家 |
| `product_class` | `component` 元器件 / `part` 部件 / `module` 组件（推荐） |
| `category` / `category_slug` | 一级分类 |
| `sub_category` / `sub_category_slug` | 二级分类 |
| `package` / `origin` | 封装、产地（强烈建议） |
| `datasheet_url` | 官方手册 |
| `attributes` | 品类弹性参数 |

## 分类扩项（摘要）

| 级别 | 做法 |
|------|------|
| 新二级 | PR 修改 `taxonomy/categories.json` 的 `children` |
| 新一级 | 先开 Issue（模板 *Category extension*），再改 taxonomy 并建 `data/{slug}/` |
| 暂无类 | 使用 `other` / `uncategorized`，稳定后再迁入正式类 |

slug 规则：`^[a-z0-9]+(?:-[a-z0-9]+)*$`，禁止与现有语义重复。

## 数据质量

- 同文件内 `(part_number + manufacturer)` 不重复  
- `datasheet_url` 为 http(s)  
- `category_slug` 必须等于所在文件夹名且存在于 taxonomy  
- `sub_category_slug` 必须属于该一级下的 children  
- `manufacturer_id` 应已在 `manufacturers/` 登记  

```bash
python scripts/validate.py
python scripts/search.py STM32
```

PR 与 push 到 `main` 时 GitHub Actions 自动校验。
