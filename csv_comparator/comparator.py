"""
CSV文件比对器核心类
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
import chardet
from pathlib import Path

@dataclass
class CellDifference:
    """单元格差异信息"""
    row: int
    col: int
    col_name: str
    original: str
    target: str
    original_repr: str
    target_repr: str
    char_diff_positions: List[int]
    unicode_analysis: Dict

@dataclass
class ComparisonResult:
    """比对结果"""
    similarity: float
    total_cells: int
    different_cells: int
    identical_cells: int
    differences: List[CellDifference]
    file_info: Dict
    summary: Dict

class CSVComparator:
    """CSV文件比对器"""
    
    def __init__(self, ignore_case: bool = False, ignore_whitespace: bool = False):
        """
        初始化比对器
        
        Args:
            ignore_case: 是否忽略大小写
            ignore_whitespace: 是否忽略首尾空白字符
        """
        self.ignore_case = ignore_case
        self.ignore_whitespace = ignore_whitespace
        self.encoding_detector = chardet
        
    def detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 读取前10KB检测编码
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    
    def load_csv(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        安全加载CSV文件
        
        Args:
            file_path: 文件路径
            encoding: 指定编码，None时自动检测
            
        Returns:
            DataFrame
        """
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        try:
            df = pd.read_csv(file_path, encoding=encoding, dtype=str, keep_default_na=False)
            # 将NaN转换为空字符串
            df = df.fillna('')
            return df
        except UnicodeDecodeError:
            # 尝试其他常见编码
            for enc in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, encoding=enc, dtype=str, keep_default_na=False)
                    df = df.fillna('')
                    print(f"Warning: 使用编码 {enc} 加载文件 {file_path}")
                    return df
                except UnicodeDecodeError:
                    continue
            raise Exception(f"无法确定文件 {file_path} 的编码格式")
    
    def normalize_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        标准化两个DataFrame使其具有相同的结构
        
        Args:
            df1: 基准DataFrame
            df2: 目标DataFrame
            
        Returns:
            标准化后的两个DataFrame
        """
        # 确保列名一致
        all_columns = set(df1.columns) | set(df2.columns)
        
        # 为缺失的列添加空值
        for col in all_columns:
            if col not in df1.columns:
                df1[col] = ''
            if col not in df2.columns:
                df2[col] = ''
        
        # 重新排序列
        df1 = df1.reindex(columns=sorted(all_columns))
        df2 = df2.reindex(columns=sorted(all_columns))
        
        # 确保行数一致
        max_rows = max(len(df1), len(df2))
        if len(df1) < max_rows:
            empty_rows = pd.DataFrame('', index=range(len(df1), max_rows), columns=df1.columns)
            df1 = pd.concat([df1, empty_rows])
        if len(df2) < max_rows:
            empty_rows = pd.DataFrame('', index=range(len(df2), max_rows), columns=df2.columns)
            df2 = pd.concat([df2, empty_rows])
        
        return df1.reset_index(drop=True), df2.reset_index(drop=True)
    
    def analyze_character_difference(self, str1: str, str2: str) -> Dict:
        """
        分析两个字符串的字符级差异
        
        Args:
            str1: 原字符串
            str2: 目标字符串
            
        Returns:
            字符差异分析结果
        """
        from .analyzer import CharacterAnalyzer
        analyzer = CharacterAnalyzer()
        return analyzer.analyze_difference(str1, str2)
    
    def compare_cells(self, val1: str, val2: str) -> Tuple[bool, Dict]:
        """
        比较两个单元格的值
        
        Args:
            val1: 值1
            val2: 值2
            
        Returns:
            (是否相同, 差异分析)
        """
        # 预处理
        if self.ignore_whitespace:
            val1 = val1.strip()
            val2 = val2.strip()
        
        if self.ignore_case:
            val1 = val1.lower()
            val2 = val2.lower()
        
        # 简单比较
        if val1 == val2:
            return True, {}
        
        # 详细字符分析
        analysis = self.analyze_character_difference(val1, val2)
        return False, analysis
    
    def compare_files(self, base_file: str, target_file: str) -> ComparisonResult:
        """
        比较两个CSV文件
        
        Args:
            base_file: 基准文件路径
            target_file: 目标文件路径
            
        Returns:
            比较结果
        """
        # 加载文件
        print(f"正在加载文件: {base_file}")
        df1 = self.load_csv(base_file)
        print(f"正在加载文件: {target_file}")
        df2 = self.load_csv(target_file)
        
        # 标准化DataFrame
        df1, df2 = self.normalize_dataframes(df1, df2)
        
        # 初始化结果
        differences = []
        total_cells = df1.shape[0] * df1.shape[1]
        different_cells = 0
        
        print(f"开始逐行逐列比对... (共 {df1.shape[0]} 行, {df1.shape[1]} 列)")
        
        # 逐行逐列比较
        for row in range(df1.shape[0]):
            if row % 100 == 0:  # 进度提示
                print(f"已处理 {row}/{df1.shape[0]} 行")
                
            for col_idx, col_name in enumerate(df1.columns):
                val1 = str(df1.iloc[row, col_idx])
                val2 = str(df2.iloc[row, col_idx])
                
                is_same, analysis = self.compare_cells(val1, val2)
                
                if not is_same:
                    different_cells += 1
                    
                    # 创建差异记录
                    difference = CellDifference(
                        row=row,
                        col=col_idx,
                        col_name=col_name,
                        original=val1,
                        target=val2,
                        original_repr=repr(val1),
                        target_repr=repr(val2),
                        char_diff_positions=analysis.get('diff_positions', []),
                        unicode_analysis=analysis
                    )
                    differences.append(difference)
        
        # 计算相似度
        identical_cells = total_cells - different_cells
        similarity = identical_cells / total_cells if total_cells > 0 else 0
        
        # 文件信息
        file_info = {
            'base_file': {
                'path': base_file,
                'size': Path(base_file).stat().st_size,
                'rows': len(df1),
                'columns': len(df1.columns),
                'encoding': self.detect_encoding(base_file)
            },
            'target_file': {
                'path': target_file,
                'size': Path(target_file).stat().st_size,
                'rows': len(df2),
                'columns': len(df2.columns),
                'encoding': self.detect_encoding(target_file)
            }
        }
        
        # 摘要信息
        summary = {
            'accuracy': similarity,
            'total_cells': total_cells,
            'identical_cells': identical_cells,
            'different_cells': different_cells,
            'difference_rate': different_cells / total_cells if total_cells > 0 else 0
        }
        
        return ComparisonResult(
            similarity=similarity,
            total_cells=total_cells,
            different_cells=different_cells,
            identical_cells=identical_cells,
            differences=differences,
            file_info=file_info,
            summary=summary
        )
    
    def batch_compare(self, base_file: str, target_files: List[str]) -> Dict[str, ComparisonResult]:
        """
        批量比较多个文件
        
        Args:
            base_file: 基准文件
            target_files: 目标文件列表
            
        Returns:
            比较结果字典
        """
        results = {}
        
        for target_file in target_files:
            print(f"\n{'='*50}")
            print(f"正在比较: {base_file} vs {target_file}")
            print(f"{'='*50}")
            
            try:
                result = self.compare_files(base_file, target_file)
                results[target_file] = result
                print(f"✅ 完成比较，相似度: {result.similarity:.2%}")
            except Exception as e:
                print(f"❌ 比较失败: {str(e)}")
                results[target_file] = None
        
        return results
