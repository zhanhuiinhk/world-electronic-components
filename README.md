# World Electronic Components Database

全球开源电子元器件数据库：按种类分类收录各厂家器件的型号、封装、产地、手册与技术参数，支持社区检索、厂家入驻与按规则扩展分类。

A global, open-source repository for electronic components — specifications, packages, origins, and datasheets — built for collaborative expansion by engineers and manufacturers.

## 目标能力

1. **搜索与查询**：本地脚本按型号 / 厂家 / 分类 / 封装检索。
2. **厂家入驻**：登记品牌后，按分类提交 JSON 产品数据。
3. **扩展种类**：通过 `taxonomy/categories.json` 按规则新增二级（或经讨论后的一级）分类。

## 仓库结构

```text
world-electronic-components/
├── taxonomy/categories.json      # 官方分类树（八大类 + 二级）
├── schema/                       # JSON Schema
│   ├── component.schema.json
│   ├── manufacturer.schema.json
│   └── category.schema.json
├── manufacturers/                # 厂家登记
├── data/                         # 产品数据 data/{category}/{manufacturer}.json
│   └── semiconductors/
├── examples/                     # 示例记录
├── scripts/
│   ├── search.py                 # 搜索
│   └── validate.py               # 校验
├── CONTRIBUTING.md               # 贡献与入驻规则
└── .github/workflows/validate.yml
```

## 分类架构（摘要）

参考主流分销商划分，当前八大一级分类：

| # | slug | 中文 |
|---|------|------|
| 1 | `semiconductors` | 半导体 |
| 2 | `passive-components` | 无源器件 |
| 3 | `connectors-switches` | 连接与机电 |
| 4 | `sensors` | 传感器 |
| 5 | `rf-wireless` | 射频与无线 |
| 6 | `optoelectronics-displays` | 光电与显示 |
| 7 | `power-thermal` | 电源与散热 |
| 8 | `dev-boards-tools` | 开发工具 |

完整二级分类见 [`taxonomy/categories.json`](taxonomy/categories.json)。

## 快速开始

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components

# 搜索
python scripts/search.py STM32
python scripts/search.py NE555

# 校验全部数据
python scripts/validate.py
```

## 单条数据长什么样

```json
{
  "part_number": "STM32F103C8T6",
  "manufacturer": "STMicroelectronics",
  "manufacturer_id": "stmicroelectronics",
  "category": "Semiconductors",
  "category_slug": "semiconductors",
  "sub_category": "Microcontrollers",
  "sub_category_slug": "microcontrollers",
  "package": "LQFP-48",
  "origin": "France",
  "datasheet_url": "https://www.st.com/resource/en/datasheet/stm32f103c8.pdf",
  "attributes": { "core": "ARM Cortex-M3", "flash": "64KB" }
}
```

## 如何贡献

- **厂商入驻 / 提交产品 / 新建分类**：请读 [CONTRIBUTING.md](CONTRIBUTING.md)。
- **技术规范**：`schema/` 下 JSON Schema。
- **Pull Request** 会自动跑格式校验。

## 许可证

[MIT](LICENSE)
