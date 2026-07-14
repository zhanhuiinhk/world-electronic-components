# 厂家入驻通道（Manufacturer Onboarding）

欢迎尚未收录的原厂、代理品牌或方案商将产品加入本库。**不需要事先获得邀请**，按本流程 Fork → 登记 → 提交数据 → PR 即可。

## 谁可以入驻

- 元器件 / 部件 / 模组原厂  
- 有权公开规格与 datasheet 的品牌方  
- 工程师代为整理的**公开**产品信息（须可核验的官方手册链接）  

请勿上传涉密、未公开或无权分发的资料。

## 五步入驻

### ① Fork 仓库

打开 https://github.com/zhanhuiinhk/world-electronic-components → **Fork**

### ② 登记厂家

复制：

```text
manufacturers/_template.json  →  manufacturers/{your-id}.json
```

规则：

| 字段 | 要求 |
|------|------|
| `id` | 小写 kebab-case，与文件名一致，如 `acme-semi` |
| `name` | 官方英文名 |
| `website` | 官网 URL |
| `name_zh` / `country` / `aliases` | 建议填写 |

### ③ 选择分类

查阅 [`taxonomy/categories.json`](../taxonomy/categories.json) 或 [TAXONOMY.md](TAXONOMY.md)：

- 已有二级类 → 直接使用其 `slug`  
- 没有合适二级类 → 先（或同时）PR 扩项二级分类  
- 完全新领域 → 先开 **Category extension** Issue  

### ④ 提交产品 JSON

路径：

```text
data/{category_slug}/{manufacturer_id}.json
```

内容为**数组**，元素符合 `schema/component.schema.json`。

最低字段：

- `part_number`, `manufacturer`, `manufacturer_id`  
- `category`, `category_slug`, `sub_category`, `sub_category_slug`  
- `datasheet_url`  

推荐：`package`, `origin`, `product_class`（`component` | `part` | `module`）, `attributes`

示例：`data/semiconductors/stmicroelectronics.json`、`examples/component.example.json`

### ⑤ 本地校验并开 PR

```bash
python scripts/validate.py
python scripts/search.py YOUR-PART
```

提交 PR 时勾选模板中的检查清单。CI 会再次运行校验。

## 批量导入

若产品很多：

1. 可按**一级分类**拆成多个文件（仍建议 `{manufacturer_id}.json` 或 `{manufacturer_id}-{batch}.json`，若用 batch 后缀需保持 `manufacturer_id` 字段正确；当前校验按目录+内容校验，文件名推荐等于 `manufacturer_id`）。  
2. 大批量可先开 Issue 说明规模，便于维护者协助。  

> 说明：当前 `validate.py` 不强制文件名等于 `manufacturer_id`，但强烈建议一致，便于人工检索。

## 常见问题

**Q: 我们还没有 GitHub 账号？**  
A: 注册免费账号即可；也可委托社区贡献者代提 PR，但 datasheet 须官方可访问。

**Q: 分类不合适怎么办？**  
A: 见 [TAXONOMY.md §4 扩项](TAXONOMY.md)。过渡期可用 `other/uncategorized`。

**Q: 能否改别人厂家的数据？**  
A: 可以提 PR 修正错误链接/参数，但请在说明中标注依据；品牌官方 PR 优先。

**Q: 商业授权？**  
A: 本库数据默认 MIT（见 LICENSE）；厂商商标归原厂所有。

## 通道汇总

| 诉求 | 入口 |
|------|------|
| 新厂家 + 产品 | 本文流程 + PR |
| 仅新二级分类 | PR 改 `taxonomy/categories.json` |
| 新一级分类 | Issue 模板 Category extension |
| 流程疑问 | 开普通 Issue |
