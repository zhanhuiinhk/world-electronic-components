# 分类体系说明（Taxonomy）

## 1. 设计原则

参考并合并 [DigiKey](https://www.digikey.com/)、[Mouser](https://www.mouser.com/)、[Arrow](https://www.arrow.com/) 的顶级类目：

| 原则 | 说明 |
|------|------|
| **合并同类项** | 名称不同但语义相同的类（如 Passives / Passive Components）合并为一 |
| **补充分销商独立类** | 如 Circuit Protection、Wire & Cable、Industrial Automation 等原八大类未覆盖的 |
| **元器件 / 部件 / 组件** | 用 `product_class` 区分粒度，而不是再拆一套平行树 |
| **可扩展** | 二级自由 PR；一级走 Issue；保留 `other` 作为缓冲 |

权威数据文件：[`taxonomy/categories.json`](../taxonomy/categories.json)

## 2. 三层产品粒度（product_class）

| 值 | 中文 | 例子 |
|----|------|------|
| `component` | 元器件 | 电阻、MCU、二极管、板对板连接器 |
| `part` | 部件 | 线束、散热器、机箱、电池座 |
| `module` | 组件/模组 | 电源模块、Wi-Fi 模组、SOM、开发板 |

录入产品时在 JSON 中填写 `product_class`（可选但推荐）。分类节点上的 `typical_class` 仅作默认建议。

## 3. 当前一级分类（v2）

1. semiconductors — 半导体  
2. passive-components — 无源器件  
3. circuit-protection — 电路保护  
4. connectors-interconnects — 连接器与互连  
5. electromechanical — 机电元件  
6. sensors-transducers — 传感器与换能器  
7. rf-wireless — 射频/微波/无线  
8. optoelectronics-displays — 光电与显示  
9. power-energy — 电源与能源  
10. thermal-management — 热管理  
11. wire-cable — 线材电缆线束  
12. enclosures-mechanical — 机箱结构件  
13. embedded-modules-boards — 嵌入式模组与开发板  
14. industrial-automation — 工业自动化  
15. audio — 音频  
16. test-measurement-tools — 测试测量与工具  
17. materials-prototyping — 材料与打样  
18. other — 其他/待归类  

相对 v1 的变更：拆分/重命名见 `categories.json` 中 `deprecated_slugs`。

## 4. 如何扩项（社区）

### 4.1 新增二级分类（推荐、轻量）

1. 确认 `categories.json` 中不存在同义 slug。  
2. 在对应一级的 `children` 增加：
   ```json
   { "slug": "your-slug", "name_en": "English", "name_zh": "中文" }
   ```
3. PR 说明：为何需要、对应 DigiKey/Mouser 哪个类目、是否与现有项重复。  
4. CI 通过后即可在 `data/{l1_slug}/` 下用该 `sub_category_slug` 录产品。

### 4.2 新增一级分类（慎重）

1. 使用 Issue 模板 **Category extension**。  
2. 说明与现有 18 类的边界、三大分销商是否有对应顶级类。  
3. 维护者同意后：改 `taxonomy/categories.json` + 新建 `data/{new-slug}/`。  

### 4.3 暂无类可放哪

先放入 `other / uncategorized`，积累样本后再提案正式类，避免 taxonomy 膨胀。

## 5. 与数据目录的关系

```text
data/{category_slug}/{manufacturer_id}.json
```

- `category_slug` 必须是本文件一级 `slug`  
- `sub_category_slug` 必须是该一级下 `children[].slug`  
- 校验脚本会强制检查  

详见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
