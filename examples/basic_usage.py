"""
CSV文件比对工具使用示例
"""

from csv_comparator import CSVComparator, ComparisonReporter
import pandas as pd
from pathlib import Path

# 创建示例数据
def create_sample_data():
    """创建示例CSV文件用于测试"""
    
    # 创建示例目录
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # 基准文件 - 包含一些特殊字符
    base_data = {
        'ID': ['001', '002', '003'],
        'Name': ['张三', '李四', 'John Doe'],
        'Description': [
            'harrington is a small village located at the mouth of the manning river',
            '这是一个\u00A0包含不间断空格的文本',  # 不间断空格
            'Normal text with spaces'
        ],
        'URL': [
            'https://example.com',
            'https://test.com',
            'https://demo.com'
        ]
    }
    
    # 目标文件 - 包含一些差异
    target_data = {
        'ID': ['001', '002', '003'],
        'Name': ['张三', '李四', 'John Doe'],
        'Description': [
            'harrington is a small village located at the mouth of the manning river\nwith some additional text',  # 添加换行和文本
            '这是一个 包含普通空格的文本',  # 普通空格替换不间断空格
            'Normal text with\ttabs'  # 空格替换为制表符
        ],
        'URL': [
            'https://example.com',
            'https://test.com',
            'https://demo.com/'  # 添加斜杠
        ]
    }
    
    # 保存为CSV
    base_df = pd.DataFrame(base_data)
    target_df = pd.DataFrame(target_data)
    
    base_path = sample_dir / "base_file.csv"
    target_path = sample_dir / "target_file.csv"
    
    base_df.to_csv(base_path, index=False, encoding='utf-8')
    target_df.to_csv(target_path, index=False, encoding='utf-8')
    
    print(f"✅ 示例文件已创建:")
    print(f"   基准文件: {base_path}")
    print(f"   目标文件: {target_path}")
    
    return str(base_path), str(target_path)

def example_basic_comparison():
    """基础比较示例"""
    print("🚀 开始基础比较示例...")
    
    # 创建示例数据
    base_file, target_file = create_sample_data()
    
    # 创建比对器
    comparator = CSVComparator()
    
    # 执行比较
    result = comparator.compare_files(base_file, target_file)
    
    # 创建报告器并打印摘要
    reporter = ComparisonReporter()
    reporter.print_summary(result, target_file)
    
    # 生成详细报告
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # CSV详细报告
    csv_path = reports_dir / "detailed_differences.csv"
    reporter.generate_csv_report(result, str(csv_path))
    
    # HTML可视化报告
    html_path = reports_dir / "visual_report.html"
    reporter.generate_html_report(result, str(html_path), target_file)
    
    print(f"\n📊 报告已生成:")
    print(f"   CSV详细报告: {csv_path}")
    print(f"   HTML可视化报告: {html_path}")

def example_batch_comparison():
    """批量比较示例"""
    print("\n🚀 开始批量比较示例...")
    
    # 创建多个目标文件
    sample_dir = Path("sample_data")
    base_file, _ = create_sample_data()
    
    # 创建更多差异文件
    target_files = []
    for i in range(2, 5):
        target_data = {
            'ID': ['001', '002', '003'],
            'Name': [f'用户{i}', '李四', 'John Doe'],
            'Description': [
                f'文本{i}包含差异',
                f'第{i}个测试文件',
                f'测试数据{i}'
            ],
            'URL': [
                f'https://example{i}.com',
                'https://test.com',
                'https://demo.com'
            ]
        }
        
        target_path = sample_dir / f"target_file_{i}.csv"
        pd.DataFrame(target_data).to_csv(target_path, index=False, encoding='utf-8')
        target_files.append(str(target_path))
    
    # 创建比对器
    comparator = CSVComparator()
    
    # 批量比较
    results = comparator.batch_compare(base_file, target_files)
    
    # 创建报告器
    reporter = ComparisonReporter()
    
    # 为每个结果打印摘要
    for target_file, result in results.items():
        if result is not None:
            reporter.print_summary(result, target_file)
    
    # 生成汇总报告
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    reporter.generate_batch_summary(results, str(reports_dir))
    
    print(f"\n📊 批量比较报告已生成到: {reports_dir}")

def example_character_analysis():
    """字符分析示例"""
    print("\n🚀 开始字符分析示例...")
    
    from csv_comparator.analyzer import CharacterAnalyzer
    
    # 创建分析器
    analyzer = CharacterAnalyzer()
    
    # 测试字符串
    str1 = "hello\u00A0world"  # 包含不间断空格
    str2 = "hello world"       # 普通空格
    
    print(f"字符串1: {repr(str1)}")
    print(f"字符串2: {repr(str2)}")
    
    # 分析差异
    analysis = analyzer.analyze_difference(str1, str2)
    
    print(f"\n🔍 分析结果:")
    print(f"字符串相等: {analysis['are_equal']}")
    print(f"长度差异: {analysis['length_diff']}")
    print(f"差异数量: {analysis['diff_count']}")
    print(f"差异位置: {analysis['diff_positions']}")
    print(f"差异类型: {list(analysis['diff_types'].keys())}")
    
    # 特殊字符分析
    if analysis['str1_special_chars']:
        print(f"\n字符串1的特殊字符:")
        for sc in analysis['str1_special_chars']:
            char_info = sc['char_info']
            print(f"  位置{sc['position']}: {char_info['name'] or char_info['unicode_name']} ({char_info['hex']})")
    
    if analysis['str2_special_chars']:
        print(f"\n字符串2的特殊字符:")
        for sc in analysis['str2_special_chars']:
            char_info = sc['char_info']
            print(f"  位置{sc['position']}: {char_info['name'] or char_info['unicode_name']} ({char_info['hex']})")

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 CSV文件比对工具 - 使用示例")
    print("=" * 60)
    
    # 运行示例
    example_basic_comparison()
    example_batch_comparison()
    example_character_analysis()
    
    print("\n✅ 所有示例执行完成！")
    print("请查看生成的报告文件了解详细差异信息。")
