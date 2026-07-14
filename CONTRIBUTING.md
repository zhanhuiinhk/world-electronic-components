# 贡献指南 (Contributing Guide)

感谢关注 **World Electronic Components Database**。为保证可检索、可扩展与数据质量，请遵循本指南。

## 目录约定

```text
manufacturers/{manufacturer_id}.json     # 厂家登记
data/{category_slug}/{manufacturer_id}.json  # 该厂家在该大类下的产品数组
taxonomy/categories.json                 # 官方分类树（新增种类改这里）
schema/                                  # JSON Schema 定义
scripts/search.py                        # 本地搜索
scripts/validate.py                      # 本地/CI 校验
```

## 一、厂家入驻并提交产品

1. **Fork** 本仓库并创建分支。
2. 复制 `manufacturers/_template.json` 为 `manufacturers/{your-id}.json`，填写官方名称与官网。
   - `id` 必须为小写 kebab-case，且与文件名一致，如 `acme-semi.json` → `"id": "acme-semi"`。
3. 在 `data/{category_slug}/` 下新建或编辑 `{manufacturer_id}.json`。
   - 文件内容必须是 **JSON 数组**，每个元素是一条元器件记录。
   - 字段须符合 `schema/component.schema.json`。
   - `category_slug` 必须等于所在文件夹名，且存在于 `taxonomy/categories.json`。
4. 本地校验：
   ```bash
   python scripts/validate.py
   python scripts/search.py STM32
   ```
5. 发起 **Pull Request**，等待 CI（`.github/workflows/validate.yml`）通过。

### 产品字段最低要求

| 字段 | 说明 |
|------|------|
| `part_number` | 官方型号 |
| `manufacturer` / `manufacturer_id` | 厂家名与 slug |
| `category` / `category_slug` | 一级分类 |
| `sub_category` / `sub_category_slug` | 二级分类 |
| `datasheet_url` | 官方手册链接 |
| `package` | 强烈建议填写封装 |
| `origin` | 建议填写产地 |
| `attributes` | 品类相关弹性参数 |

完整示例见 `examples/component.example.json` 与 `data/semiconductors/`。

## 二、新增分类（种类）

**不要**在数据文件里随意 invent 新的 `category_slug`。

### 新增二级分类（推荐）

1. 打开 Issue 说明用途与边界（可选但推荐）。
2. 修改 `taxonomy/categories.json`，在对应一级分类的 `children` 中增加：
   ```json
   { "slug": "your-sub-slug", "name_en": "English Name", "name_zh": "中文名" }
   ```
3. `slug` 规则：`^[a-z0-9]+(?:-[a-z0-9]+)*$`（小写、数字、连字符）。
4. 单独或随数据 PR 一并提交；校验脚本会拒绝未知 slug。

### 新增一级分类

1. **必须先开 Issue 讨论**（命名、边界、是否与现有八大类重叠）。
2. 维护者同意后，再 PR 修改 `taxonomy/categories.json`，并创建 `data/{new-slug}/` 目录。
3. 一级分类参考 Mouser / DigiKey / Arrow 的常见划分，避免过细或过宽。

## 三、数据质量规则

- 同一文件内：`(part_number + manufacturer)` 不得重复。
- `datasheet_url` 须为 `http://` 或 `https://` 官方或授权链接。
- 优先使用 taxonomy 中的英文 `name_en` 作为 `category` / `sub_category` 显示名。
- 技术参数放 `attributes`，不要为每个参数新增顶层字段。
- 不要提交密钥、未公开内部文档链接或侵权资料。

## 四、搜索

```bash
python scripts/search.py 555
python scripts/search.py STMicroelectronics
python scripts/search.py SOIC
```

脚本会递归扫描 `data/**/*.json`，按型号、厂家、分类、封装、描述、标签匹配。

## 五、自动化

PR 与 push 到 `main` 时，GitHub Actions 会运行 `python scripts/validate.py`。校验失败的 PR 不应合并。
