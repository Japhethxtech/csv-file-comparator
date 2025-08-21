"""
命令行接口
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .comparator import CSVComparator
from .reporter import ComparisonReporter

def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="CSV文件字符级精确比对工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 比对两个文件
  python -m csv_comparator compare base.csv target.csv
  
  # 批量比对多个文件
  python -m csv_comparator batch-compare base.csv file1.csv file2.csv file3.csv
  
  # 生成HTML报告
  python -m csv_comparator compare base.csv target.csv --html-report
  
  # 忽略大小写差异
  python -m csv_comparator compare base.csv target.csv --ignore-case
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单文件比对命令
    compare_parser = subparsers.add_parser('compare', help='比对两个CSV文件')
    compare_parser.add_argument('base_file', help='基准文件路径')
    compare_parser.add_argument('target_file', help='目标文件路径')
    compare_parser.add_argument('--ignore-case', action='store_true', help='忽略大小写差异')
    compare_parser.add_argument('--ignore-whitespace', action='store_true', help='忽略首尾空白字符')
    compare_parser.add_argument('--output-dir', default='reports', help='报告输出目录')
    compare_parser.add_argument('--html-report', action='store_true', help='生成HTML可视化报告')
    compare_parser.add_argument('--csv-report', action='store_true', help='生成CSV详细报告')
    
    # 批量比对命令
    batch_parser = subparsers.add_parser('batch-compare', help='批量比对多个CSV文件')
    batch_parser.add_argument('base_file', help='基准文件路径')
    batch_parser.add_argument('target_files', nargs='+', help='目标文件路径列表')
    batch_parser.add_argument('--ignore-case', action='store_true', help='忽略大小写差异')
    batch_parser.add_argument('--ignore-whitespace', action='store_true', help='忽略首尾空白字符')
    batch_parser.add_argument('--output-dir', default='reports', help='报告输出目录')
    batch_parser.add_argument('--html-report', action='store_true', help='生成HTML可视化报告')
    batch_parser.add_argument('--csv-report', action='store_true', help='生成CSV详细报告')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 创建比对器
    comparator = CSVComparator(
        ignore_case=args.ignore_case,
        ignore_whitespace=args.ignore_whitespace
    )
    
    # 创建报告器
    reporter = ComparisonReporter()
    
    try:
        if args.command == 'compare':
            # 单文件比对
            result = comparator.compare_files(args.base_file, args.target_file)
            
            # 打印摘要
            reporter.print_summary(result, args.target_file)
            
            # 生成报告
            if args.csv_report or (not args.html_report and not args.csv_report):
                csv_path = output_dir / f"comparison_details_{reporter.timestamp}.csv"
                reporter.generate_csv_report(result, str(csv_path))
            
            if args.html_report:
                html_path = output_dir / f"comparison_report_{reporter.timestamp}.html"
                reporter.generate_html_report(result, str(html_path), args.target_file)
        
        elif args.command == 'batch-compare':
            # 批量比对
            results = comparator.batch_compare(args.base_file, args.target_files)
            
            # 打印每个文件的摘要
            for target_file, result in results.items():
                if result is not None:
                    print(f"\n{'='*80}")
                    reporter.print_summary(result, target_file)
            
            # 生成汇总报告
            reporter.generate_batch_summary(results, str(output_dir))
            
            # 为每个文件生成详细报告
            if args.csv_report or args.html_report:
                for target_file, result in results.items():
                    if result is None:
                        continue
                    
                    file_name = Path(target_file).stem
                    
                    if args.csv_report or (not args.html_report and not args.csv_report):
                        csv_path = output_dir / f"details_{file_name}_{reporter.timestamp}.csv"
                        reporter.generate_csv_report(result, str(csv_path))
                    
                    if args.html_report:
                        html_path = output_dir / f"report_{file_name}_{reporter.timestamp}.html"
                        reporter.generate_html_report(result, str(html_path), target_file)
        
        print(f"\n✅ 所有报告已生成到目录: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
