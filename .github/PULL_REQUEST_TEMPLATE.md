## 变更类型
- [ ] 新增/更新元器件数据
- [ ] 厂家入驻（manufacturers/）
- [ ] 新增/调整分类（taxonomy/）
- [ ] 文档或脚本

## 检查清单
- [ ] 已运行 `python scripts/validate.py` 且通过
- [ ] 厂家已在 `manufacturers/{id}.json` 登记（若为新产品）
- [ ] 分类 slug 来自 `taxonomy/categories.json`（若需新分类已先提 taxonomy PR）
- [ ] `datasheet_url` 为可访问的官方链接
- [ ] 文件路径为 `data/{category_slug}/{manufacturer_id}.json`

## 说明
<!-- 简述本次录入的厂家/型号范围 -->
