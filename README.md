# World Electronic Components Database

全球开源电子元器件 / 部件 / 组件数据库。  
分类参考并合并 [DigiKey](https://www.digikey.com/)、[Mouser](https://www.mouser.com/)、[Arrow](https://www.arrow.com/) 同类项。

**在线检索（GitHub Pages）：**  
https://zhanhuiinhk.github.io/world-electronic-components/  
（需在仓库 Settings → Pages 选用 GitHub Actions；首次 push 后由 workflow 部署）

**双语文档站：**  
- 中文：https://zhanhuiinhk.github.io/world-electronic-components/zh/  
- English：https://zhanhuiinhk.github.io/world-electronic-components/en/  

## 能力一览

| 能力 | 入口 |
|------|------|
| 在线检索 | GitHub Pages `docs/index.html` |
| 本地搜索 | `python scripts/search.py STM32` |
| 品类专用参数 | `schema/attribute-profiles.json`（电阻必填 `resistance_ohm` 等） |
| CSV 批量导入 | `python scripts/csv_to_json.py …` |
| 新厂家入驻 | [docs/MANUFACTURER_ONBOARDING.md](docs/MANUFACTURER_ONBOARDING.md) |
| 分类扩项 | [docs/TAXONOMY.md](docs/TAXONOMY.md) |

## 快速开始

```bash
git clone https://github.com/zhanhuiinhk/world-electronic-components.git
cd world-electronic-components

python scripts/validate.py
python scripts/search.py 10K
python scripts/build_catalog.py   # 生成 docs/assets/catalog.json 供本地打开 docs/index.html
```

### CSV → JSON

```bash
python scripts/csv_to_json.py examples/import-resistors-sample.csv \
  -o data/passive-components/yageo.json
python scripts/validate.py
```

模板：`examples/import-template.csv`

### 本地预览站点

```bash
python scripts/build_catalog.py
# 用任意静态服务器打开 docs/，例如：
python -m http.server 8080 --directory docs
# 浏览器访问 http://127.0.0.1:8080/
```

## 仓库结构

```text
taxonomy/categories.json
schema/component.schema.json
schema/attribute-profiles.json   # 品类 attributes 必填/推荐表
manufacturers/
data/{category}/{manufacturer}.json
scripts/
  search.py / validate.py / csv_to_json.py / build_catalog.py
docs/                            # GitHub Pages：检索 UI + 中英文档
  index.html                     # 检索
  zh/  en/                       # 双语文档站
  assets/catalog.json            # 由 build_catalog 生成
```

## 一级分类（摘要）

`semiconductors` · `passive-components` · `circuit-protection` · `connectors-interconnects` · `electromechanical` · `sensors-transducers` · `rf-wireless` · `optoelectronics-displays` · `power-energy` · `thermal-management` · `wire-cable` · `enclosures-mechanical` · `embedded-modules-boards` · `industrial-automation` · `audio` · `test-measurement-tools` · `materials-prototyping` · `other`

完整树见 [`taxonomy/categories.json`](taxonomy/categories.json)。

## 许可证

[MIT](LICENSE)
