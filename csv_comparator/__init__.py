"""
CSV文件字符级精确比对工具
专门用于检测隐藏字符差异和精确计算相似度
"""

from .comparator import CSVComparator
from .analyzer import CharacterAnalyzer
from .reporter import ComparisonReporter

__version__ = "1.0.0"
__author__ = "Japhethxtech"

__all__ = [
    "CSVComparator",
    "CharacterAnalyzer", 
    "ComparisonReporter"
]
