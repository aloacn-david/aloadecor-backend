# AI产品分析系统

基于规则的产品质量分析系统，用于分析电商平台产品链接的质量并提供改进建议。

## 功能特性

### 已实现功能

✅ **标题质量分析**
- 标题长度评估
- 关键词覆盖检查
- 规格信息识别
- 可读性评分

✅ **图片分析（第一阶段）**
- 图片数量统计
- 图片类型识别（主图、细节图、场景图、尺寸图）
- 多样性评分
- 缺失类型检测

✅ **参数完整性分析**
- 核心参数检查
- 完整性评分
- 格式问题识别
- 缺失参数提示

✅ **核心事实提取**
- 产品名称提取
- 尺寸信息提取
- 材质识别
- 颜色识别

✅ **智能优先级建议**
- 自动生成3条最高优先级改进建议
- 按问题严重程度排序
- 提供具体改进方案

### 待实现功能

🔄 **评论分析** - 提取差评主题和关键词
🔄 **跨平台一致性** - 对比多平台产品信息
🔄 **Playwright集成** - 自动抓取真实产品数据
🔄 **视觉质量分析** - 第二阶段图片质量评估

## 项目结构

```
ai-analyzer/
├── src/
│   ├── models/
│   │   └── product_analysis.py    # 统一数据模型
│   ├── analyzers/
│   │   └── rule_based_analyzer.py # 规则分析模块
│   ├── scrapers/
│   │   └── base_scraper.py        # Playwright抓取基础
│   └── utils/
│       └── exceptions.py          # 异常处理
├── tests/
│   ├── test_analyzer.py           # 单元测试
│   └── demo_analysis.py           # 功能演示
├── data/                          # 数据存储
└── venv/                          # Python虚拟环境
```

## 安装使用

### 1. 创建虚拟环境

```bash
cd ai-analyzer
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install playwright pydantic beautifulsoup4 requests
playwright install chromium
```

### 3. 运行测试

```bash
# 运行单元测试
python tests/test_analyzer.py

# 运行功能演示
python tests/demo_analysis.py
```

## 使用示例

### 基础分析

```python
from src.analyzers.rule_based_analyzer import RuleBasedAnalyzer

# 创建分析器
analyzer = RuleBasedAnalyzer()

# 准备产品数据
product_data = {
    "title": "Modern Black Iron Chandelier 24 inch 3-Light Ceiling Fixture",
    "images": [
        {"url": "https://example.com/main.jpg", "alt": "Main product image"},
        {"url": "https://example.com/detail.jpg", "alt": "Detail view"},
    ],
    "parameters": {
        "Dimensions": '24" x 12"',
        "Material": "Iron",
        "Color": "Black",
    }
}

# 执行分析
results = analyzer.analyze_product(product_data)

# 计算总体评分
overall_score = analyzer.calculate_overall_score(results)
print(f"总体评分: {overall_score}/100")
```

### 生成优先级建议

```python
from tests.demo_analysis import generate_priority_suggestions

# 基于分析结果生成建议
suggestions = generate_priority_suggestions(results)

for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. 【优先级{suggestion.priority}】{suggestion.category}")
    print(f"   问题: {suggestion.issue}")
    print(f"   建议: {suggestion.recommendation}")
    print(f"   预期效果: {suggestion.expected_impact}")
```

## 评分标准

### 标题评分
- **长度评分**: 30-200字符为合理范围，80字符为最优
- **可读性评分**: 基于特殊字符数量、大小写、数字比例
- **关键词评分**: 是否包含产品类型关键词

### 图片评分
- **多样性评分**: 基于图片类型覆盖度（主图、细节图、场景图、尺寸图）
- **数量要求**: 建议3-5张以上
- **类型要求**: 至少包含主图

### 参数评分
- **完整性评分**: 基于10个核心参数的覆盖度
- **核心参数**: dimensions, size, material, finish, color, weight, wattage, voltage, bulb_type, certification

## 异常处理

系统包含完善的异常处理机制：

- **PageLoadException**: 页面加载失败
- **ElementNotFoundException**: 页面结构变化
- **ContentMissingException**: 内容缺失
- **RateLimitException**: 访问限制
- **PriceDiscrepancyException**: 价格差异

## 数据模型

### ProductAnalysis
完整的产品分析结果，包含：
- 基本信息（product_id, sku, platform, url）
- 标题分析结果
- 图片分析结果
- 参数分析结果
- 评论分析结果
- 核心事实一致性
- 优先级建议列表
- 错误记录

## 下一步计划

1. **集成Playwright抓取**
   - 实现Amazon产品页面抓取
   - 实现Wayfair产品页面抓取
   - 添加异常重试机制

2. **评论分析**
   - 提取评论内容
   - 情感分析
   - 主题提取

3. **跨平台一致性**
   - 对比多平台产品信息
   - 识别不一致项

4. **前端集成**
   - 集成到Admin Panel
   - 可视化分析报告
   - 定期自动分析

## 技术栈

- **Python 3.9+**
- **Playwright**: 页面抓取
- **Pydantic**: 数据模型和验证
- **BeautifulSoup**: HTML解析

## License

MIT License
