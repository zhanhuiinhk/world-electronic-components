# 贡献指南 (Contributing Guide)

感谢您关注 World Electronic Components Database！为了确保数据库的可扩展性和数据质量，请遵循以下流程：

## 💡 厂家自主入驻流程
如果您是元器件原厂，希望将产品收录至本库，请按以下步骤操作：

1. **Fork** 本仓库。
2. 在 `manufacturers/` 目录下登记您的品牌基本信息。
3. 在 `data/` 对应的分类文件夹下，以 JSON 格式提交您的产品列表。
4. 发起 **Pull Request (PR)**。

我们的自动化脚本会对您的数据进行格式校验，通过后即可自动合并。

## 🛠️ 数据结构规范
请参考 `schema/component.schema.json` 中的字段定义。我们支持 `attributes` 字段的灵活扩展，您可以根据产品特性添加自定义技术参数。
