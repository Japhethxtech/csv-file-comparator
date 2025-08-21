# 🎯 CSV文件字符级精确比对工具

专门用于检测人眼无法识别的隐藏字符差异的专业CSV文件比对工具。

## ✨ 特色功能

### 🔍 字符级精确检测
- **不可见字符检测**: 零宽空格、不间断空格、各种Unicode空白字符
- **编码差异分析**: 自动检测文件编码，识别编码引起的字符差异  
- **空白字符分类**: 区分普通空格、制表符、换行符等不同类型的空白字符
- **Unicode分析**: 详细分析字符的Unicode编码和分类

### 📊 精确统计分析
- **相似度计算**: 提供精确的百分比相似度
- **差异定位**: 精确到行号、列号的差异位置信息
- **统计摘要**: 总单元格数、相同数、差异数等详细统计

### 📝 多格式报告
- **控制台摘要**: 快速查看比对结果概览
- **CSV详细报告**: 包含每个差异位置的详细信息
- **HTML可视化报告**: 美观的网页格式报告，支持差异高亮显示
- **批量汇总报告**: 多文件比对的汇总统计

### 🚀 易用性
- **Python API**: 灵活的编程接口
- **命令行工具**: 简单易用的CLI命令
- **批量处理**: 支持一次比对多个文件
- **内存优化**: 支持处理大型CSV文件

## 📦 安装

### 方式1: 直接使用源码
```bash
git clone https://github.com/Japhethxtech/csv-file-comparator.git
cd csv-file-comparator
pip install -r requirements.txt
```

### 方式2: 安装为Python包
```bash
git clone https://github.com/Japhethxtech/csv-file-comparator.git
cd csv-file-comparator
pip install -e .
```

## 🎯 使用场景

### 数据质量检查
你刚完成了数据清洗，需要验证处理前后的数据差异：
```python
from csv_comparator import CSVComparator
comparator = CSVComparator
