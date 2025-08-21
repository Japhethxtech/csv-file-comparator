"""
比较结果报告生成器
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import pandas as pd

from .comparator import ComparisonResult, CellDifference

class ComparisonReporter:
    """比较结果报告生成器"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def print_summary(self, result: ComparisonResult, target_file: str = ""):
        """打印摘要信息到控制台"""
        print(f"\n{'='*60}")
        print(f"📊 CSV文件比对结果摘要")
        if target_file:
            print(f"目标文件: {target_file}")
        print(f"{'='*60}")
        
        print(f"📈 总体相似度: {result.similarity:.2%}")
        print(f"📋 总单元格数: {result.total_cells:,}")
        print(f"✅ 相同单元格: {result.identical_cells:,}")
        print(f"❌ 不同单元格: {result.different_cells:,}")
        print(f"📉 差异率: {(result.different_cells/result.total_cells)*100:.2f}%")
        
        if result.different_cells > 0:
            print(f"\n🔍 差异详情预览 (前5个):")
            for i, diff in enumerate(result.differences[:5]):
                print(f"  {i+1}. 行{diff.row+1}, 列'{diff.col_name}':")
                print(f"     原始: {diff.original_repr}")
                print(f"     目标: {diff.target_repr}")
                if diff.unicode_analysis.get('diff_types'):
                    print(f"     差异类型: {list(diff.unicode_analysis['diff_types'].keys())}")
        
        print(f"\n📁 文件信息:")
        base_info = result.file_info['base_file']
        target_info = result.file_info['target_file']
        print(f"  基准文件: {base_info['rows']}行 x {base_info['columns']}列 ({base_info['encoding']})")
        print(f"  目标文件: {target_info['rows']}行 x {target_info['columns']}列 ({target_info['encoding']})")
    
    def generate_csv_report(self, result: ComparisonResult, output_path: str):
        """生成详细的CSV差异报告"""
        if not result.differences:
            print("没有发现差异，无需生成详细报告")
            return
        
        # 准备报告数据
        report_data = []
        for diff in result.differences:
            # 基本信息
            row_data = {
                '行号': diff.row + 1,
                '列号': diff.col + 1,
                '列名': diff.col_name,
                '原始值': diff.original,
                '目标值': diff.target,
                '原始值(repr)': diff.original_repr,
                '目标值(repr)': diff.target_repr,
                '长度差异': len(diff.target) - len(diff.original),
            }
            
            # Unicode分析信息
            unicode_analysis = diff.unicode_analysis
            if unicode_analysis:
                row_data.update({
                    '差异字符数': unicode_analysis.get('diff_count', 0),
                    '差异位置': str(unicode_analysis.get('diff_positions', [])),
                    '差异类型': str(list(unicode_analysis.get('diff_types', {}).keys())),
                })
                
                # 特殊字符信息
                special_chars_1 = unicode_analysis.get('str1_special_chars', [])
                special_chars_2 = unicode_analysis.get('str2_special_chars', [])
                
                if special_chars_1:
                    special_info_1 = [f"位置{sc['position']}:{sc['char_info']['name'] or sc['char_info']['unicode_name']}" 
                                    for sc in special_chars_1]
                    row_data['原始值特殊字符'] = '; '.join(special_info_1)
                
                if special_chars_2:
                    special_info_2 = [f"位置{sc['position']}:{sc['char_info']['name'] or sc['char_info']['unicode_name']}" 
                                    for sc in special_chars_2]
                    row_data['目标值特殊字符'] = '; '.join(special_info_2)
            
            report_data.append(row_data)
        
        # 创建DataFrame并保存
        df_report = pd.DataFrame(report_data)
        df_report.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"📄 详细差异报告已保存: {output_path}")
    
    def generate_html_report(self, result: ComparisonResult, output_path: str, target_file: str = ""):
        """生成HTML可视化报告"""
        
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV文件比对报告</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #e1e5e9; }}
        .header h1 {{ color: #2d3748; margin: 0; font-size: 2.5em; }}
        .header .subtitle {{ color: #718096; font-size: 1.1em; margin-top: 10px; }}
        
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .metric {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 20px; border-radius: 8px; text-align: center; 
        }}
        .metric.success {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric.warning {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .metric .value {{ font-size: 2em; font-weight: bold; margin-bottom: 5px; }}
        .metric .label {{ font-size: 0.9em; opacity: 0.9; }}
        
        .file-info {{ 
            display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; 
            background: #f8f9fa; padding: 20px; border-radius: 8px; 
        }}
        .file-card {{ background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #3182ce; }}
        .file-card h3 {{ margin: 0 0 10px 0; color: #2d3748; }}
        .file-card .info {{ color: #4a5568; line-height: 1.6; }}
        
        .differences {{ margin-top: 40px; }}
        .differences h2 {{ color: #2d3748; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0; }}
        .diff-item {{ 
            background: #fff; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 15px; 
            overflow: hidden; transition: box-shadow 0.2s; 
        }}
        .diff-item:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .diff-header {{ 
            background: #f7fafc; padding: 15px; border-bottom: 1px solid #e2e8f0; 
            font-weight: 600; color: #2d3748; 
        }}
        .diff-content {{ padding: 15px; }}
        .diff-row {{ margin-bottom: 10px; }}
        .diff-label {{ font-weight: 600; color: #4a5568; min-width: 100px; display: inline-block; }}
        .diff-value {{ 
            font-family: 'Courier New', monospace; background: #f1f5f9; padding: 4px 8px; 
            border-radius: 3px; border: 1px solid #cbd5e0; word-break: break-all; 
        }}
        .original {{ border-left: 3px solid #e53e3e; }}
        .target {{ border-left: 3px solid #38a169; }}
        
        .char-analysis {{ 
            background: #fffaf0; border: 1px solid #feb2b2; border-radius: 4px; 
            padding: 10px; margin-top: 10px; font-size: 0.9em; 
        }}
        .char-analysis h4 {{ margin: 0 0 8px 0; color: #c53030; }}
        
        .no-differences {{ 
            text-align: center; padding: 60px 20px; background: #f0fff4; 
            border: 1px solid #9ae6b4; border-radius: 8px; 
        }}
        .no-differences .icon {{ font-size: 4em; color: #38a169; margin-bottom: 20px; }}
        .no-differences h3 {{ color: #2f855a; margin: 0; }}
        
        .timestamp {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 CSV文件比对报告</h1>
            <div class="subtitle">字符级精确差异分析</div>
            {target_info}
        </div>
        
        <div class="summary">
            <div class="metric success">
                <div class="value">{similarity}</div>
                <div class="label">相似度</div>
            </div>
            <div class="metric">
                <div class="value">{total_cells:,}</div>
                <div class="label">总单元格数</div>
            </div>
            <div class="metric success">
                <div class="value">{identical_cells:,}</div>
                <div class="label">相同单元格</div>
            </div>
            <div class="metric warning">
                <div class="value">{different_cells:,}</div>
                <div class="label">差异单元格</div>
            </div>
        </div>
        
        <div class="file-info">
            <div class="file-card">
                <h3>📁 基准文件</h3>
                <div class="info">
                    <div><strong>路径:</strong> {base_path}</div>
                    <div><strong>大小:</strong> {base_size}</div>
                    <div><strong>维度:</strong> {base_rows} 行 × {base_cols} 列</div>
                    <div><strong>编码:</strong> {base_encoding}</div>
                </div>
            </div>
            <div class="file-card">
                <h3>📁 目标文件</h3>
                <div class="info">
                    <div><strong>路径:</strong> {target_path}</div>
                    <div><strong>大小:</strong> {target_size}</div>
                    <div><strong>维度:</strong> {target_rows} 行 × {target_cols} 列</div>
                    <div><strong>编码:</strong> {target_encoding}</div>
                </div>
            </div>
        </div>
        
        {differences_section}
        
        <div class="timestamp">
            报告生成时间: {timestamp}
        </div>
    </div>
</body>
</html>
        """
        
        # 准备模板数据
        base_info = result.file_info['base_file']
        target_info = result.file_info['target_file']
        
        # 格式化文件大小
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"
        
        template_data = {
            'target_info': f'<div class="subtitle">目标文件: {target_file}</div>' if target_file else '',
            'similarity': f"{result.similarity:.1%}",
            'total_cells': result.total_cells,
            'identical_cells': result.identical_cells,
            'different_cells': result.different_cells,
            'base_path': Path(base_info['path']).name,
            'base_size': format_size(base_info['size']),
            'base_rows': base_info['rows'],
            'base_cols': base_info['columns'],
            'base_encoding': base_info['encoding'],
            'target_path': Path(target_info['path']).name,
            'target_size': format_size(target_info['size']),
            'target_rows': target_info['rows'],
            'target_cols': target_info['columns'],
            'target_encoding': target_info['encoding'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 生成差异部分
        if result.differences:
            differences_html = '<div class="differences"><h2>🔍 详细差异分析</h2>'
            
            # 限制显示数量以避免HTML文件过大
            max_display = min(100, len(result.differences))
            for i, diff in enumerate(result.differences[:max_display]):
                differences_html += f'''
                <div class="diff-item">
                    <div class="diff-header">
                        差异 #{i+1} - 行 {diff.row+1}, 列 "{diff.col_name}"
                    </div>
                    <div class="diff-content">
                        <div class="diff-row">
                            <span class="diff-label">原始值:</span>
                            <span class="diff-value original">{self._escape_html(diff.original)}</span>
                        </div>
                        <div class="diff-row">
                            <span class="diff-label">目标值:</span>
                            <span class="diff-value target">{self._escape_html(diff.target)}</span>
                        </div>
                        <div class="diff-row">
                            <span class="diff-label">原始(repr):</span>
                            <span class="diff-value">{self._escape_html(diff.original_repr)}</span>
                        </div>
                        <div class="diff-row">
                            <span class="diff-label">目标(repr):</span>
                            <span class="diff-value">{self._escape_html(diff.target_repr)}</span>
                        </div>
                '''
                
                # 添加字符分析
                if diff.unicode_analysis:
                    analysis = diff.unicode_analysis
                    char_info = []
                    
                    if analysis.get('diff_count', 0) > 0:
                        char_info.append(f"差异字符数: {analysis['diff_count']}")
                    
                    if analysis.get('diff_types'):
                        char_info.append(f"差异类型: {', '.join(analysis['diff_types'].keys())}")
                    
                    if analysis.get('str1_special_chars') or analysis.get('str2_special_chars'):
                        char_info.append("包含特殊字符")
                    
                    if char_info:
                        differences_html += f'''
                        <div class="char-analysis">
                            <h4>🔬 字符分析</h4>
                            <div>{' | '.join(char_info)}</div>
                        </div>
                        '''
                
                differences_html += '</div></div>'
            
            if len(result.differences) > max_display:
                differences_html += f'''
                <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 6px; margin-top: 15px;">
                    <strong>注意:</strong> 共有 {len(result.differences)} 个差异，此处仅显示前 {max_display} 个。
                    完整差异信息请查看CSV详细报告。
                </div>
                '''
            
            differences_html += '</div>'
        else:
            differences_html = '''
            <div class="no-differences">
                <div class="icon">✅</div>
                <h3>恭喜！文件完全一致</h3>
                <p>两个CSV文件在字符级别完全相同，没有发现任何差异。</p>
            </div>
            '''
        
        template_data['differences_section'] = differences_html
        
        # 生成HTML文件
        html_content = html_template.format(**template_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 HTML可视化报告已生成: {output_path}")
    
    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        if not isinstance(text, str):
            text = str(text)
        
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        return "".join(html_escape_table.get(c, c) for c in text)
    
    def generate_batch_summary(self, results: Dict[str, ComparisonResult], output_dir: str):
        """生成批量比较的汇总报告"""
        summary_data = []
        
        for target_file, result in results.items():
            if result is None:
                continue
            
            summary_data.append({
                '目标文件': Path(target_file).name,
                '相似度': f"{result.similarity:.2%}",
                '总单元格数': result.total_cells,
                '相同单元格': result.identical_cells,
                '差异单元格': result.different_cells,
                '差异率': f"{(result.different_cells/result.total_cells)*100:.2f}%" if result.total_cells > 0 else "0%",
                '目标文件行数': result.file_info['target_file']['rows'],
                '目标文件列数': result.file_info['target_file']['columns'],
                '目标文件编码': result.file_info['target_file']['encoding']
            })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            summary_path = Path(output_dir) / f"batch_comparison_summary_{self.timestamp}.csv"
            df_summary.to_csv(summary_path, index=False, encoding='utf-8-sig')
            print(f"📊 批量比较汇总报告已生成: {summary_path}")
