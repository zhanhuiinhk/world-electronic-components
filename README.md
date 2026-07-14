# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 [DigiKey](https://www.digikey.com/)、[Mouser](https://www.mouser.com/)、[Arrow](https://www.arrow.com/) 同类项，并保留社区**扩项**与**新厂家入驻**通道。

## 三大能力

| # | 能力 | 怎么做 |
|---|------|--------|
| 1 | **搜索查询** | `python scripts/search.py <关键词>` |
| 2 | **新厂家加入产品** | 见 [厂家入驻](docs/MANUFACTURER_ONBOARDING.md) — 无需白名单，Fork + PR |
| 3 | **扩展分类** | 见 [分类体系](docs/TAXONOMY.md) — 二级可 PR；一级走 Issue |

## 元器件 · 部件 · 组件

| product_class | 中文 | 例子 |
|---------------|------|------|
| `component` | 元器件 | 电阻、MCU、二极管 |
| `part` | 部件 | 线束、散热器、机箱 |
| `module` | 组件/模组 | 电源模块、无线模组、开发板 |

## 一级分类（taxonomy v2）

| slug | 中文 |
|------|------|
| `semiconductors` | 半导体 |
| `passive-components` | 无源器件 |
| `circuit-protection` | 电路保护 |
| `connectors-interconnects` | 连接器与互连 |
| `electromechanical` | 机电元件 |
| `sensors-transducers` | 传感器与换能器 |
| `rf-wireless` | 射频 / 微波 / 无线 |
| `optoelectronics-displays` | 光电与显示 |
| `power-energy` | 电源与能源 |
| `thermal-management` | 热管理 |
| `wire-cable` | 线材 / 电缆 / 线束 |
| `enclosures-mechanical` | 机箱 / 结构件 |
| `embedded-modules-boards` | 嵌入式模组与开发板 |
| `industrial-automation` | 工业自动化 |
| `audio` | 音频 |
| `test-measurement-tools` | 测试测量与工具 |
| `materials-prototyping` | 材料与打样 |
| `other` | 其他 / 待归类 |

完整二级分类与分销商映射：[`taxonomy/categories.json`](taxonomy/categories.json) · [说明文档](docs/TAXONOMY.md)

## 仓库结构

```text
taxonomy/categories.json     # 官方分类树（可扩项）
schema/                      # JSON Schema
manufacturers/               # 厂家登记（新厂加入入口）
data/{category}/{mfr}.json   # 产品数据
docs/                        # 入驻与分类说明
scripts/search.py | validate.py
.github/ISSUE_TEMPLATE/      # 扩项 / 入驻 Issue 模板
```

## 快速开始

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components
python scripts/validate.py
python scripts/search.py STM32
```

## 新厂家 / 新分类

- **厂家入驻** → [docs/MANUFACTURER_ONBOARDING.md](docs/MANUFACTURER_ONBOARDING.md)  
- **分类扩项** → [docs/TAXONOMY.md](docs/TAXONOMY.md)  
- **贡献总则** → [CONTRIBUTING.md](CONTRIBUTING.md)  

## 许可证

[MIT](LICENSE)
