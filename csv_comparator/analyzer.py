"""
字符分析器 - 专门分析字符级差异
"""

import unicodedata
from typing import Dict, List, Tuple
import re

class CharacterAnalyzer:
    """字符级分析器"""
    
    def __init__(self):
        # 定义特殊字符类别
        self.special_chars = {
            # 空白字符
            '\u0020': '普通空格',
            '\u00A0': '不间断空格',
            '\u2009': '细空格',
            '\u200A': '发丝空格',
            '\u200B': '零宽空格',
            '\u200C': '零宽非连字符',
            '\u200D': '零宽连字符',
            '\u2028': '行分隔符',
            '\u2029': '段分隔符',
            '\u202F': '窄不间断空格',
            '\u205F': '中等数学空格',
            '\u3000': '中文空格',
            '\t': '制表符',
            '\n': '换行符',
            '\r': '回车符',
            '\f': '换页符',
            '\v': '垂直制表符',
            
            # 常见的相似字符
            '\u2010': '连字符',
            '\u2011': '不间断连字符',
            '\u2012': '数字短横线',
            '\u2013': '短破折号',
            '\u2014': '长破折号',
            '\u2015': '水平线',
            
            # 引号
            '\u2018': '左单引号',
            '\u2019': '右单引号',
            '\u201A': '下单引号',
            '\u201B': '上单引号',
            '\u201C': '左双引号',
            '\u201D': '右双引号',
            '\u201E': '下双引号',
            '\u201F': '上双引号',
        }
    
    def get_char_info(self, char: str) -> Dict:
        """
        获取字符的详细信息
        
        Args:
            char: 单个字符
            
        Returns:
            字符信息字典
        """
        if not char:
            return {}
        
        info = {
            'char': char,
            'ord': ord(char),
            'hex': f'U+{ord(char):04X}',
            'repr': repr(char),
            'name': self.special_chars.get(char, ''),
            'unicode_name': '',
            'category': '',
            'is_printable': char.isprintable(),
            'is_space': char.isspace(),
            'is_control': unicodedata.category(char).startswith('C'),
            'is_invisible': not char.isprintable() or char in self.special_chars
        }
        
        try:
            info['unicode_name'] = unicodedata.name(char)
            info['category'] = unicodedata.category(char)
        except ValueError:
            info['unicode_name'] = 'UNKNOWN'
            info['category'] = 'UNKNOWN'
        
        return info
    
    def find_string_differences(self, str1: str, str2: str) -> List[Dict]:
        """
        找出两个字符串的所有差异位置
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            差异位置列表
        """
        differences = []
        max_len = max(len(str1), len(str2))
        
        for i in range(max_len):
            char1 = str1[i] if i < len(str1) else ''
            char2 = str2[i] if i < len(str2) else ''
            
            if char1 != char2:
                diff = {
                    'position': i,
                    'char1': char1,
                    'char2': char2,
                    'char1_info': self.get_char_info(char1) if char1 else None,
                    'char2_info': self.get_char_info(char2) if char2 else None,
                    'type': self._classify_difference(char1, char2)
                }
                differences.append(diff)
        
        return differences
    
    def _classify_difference(self, char1: str, char2: str) -> str:
        """分类差异类型"""
        if not char1:
            return 'insertion'
        elif not char2:
            return 'deletion'
        elif char1.isspace() and char2.isspace():
            return 'whitespace_substitution'
        elif char1.isspace() or char2.isspace():
            return 'whitespace_difference'
        elif ord(char1) > 127 or ord(char2) > 127:
            return 'unicode_difference'
        else:
            return 'character_substitution'
    
    def analyze_difference(self, str1: str, str2: str) -> Dict:
        """
        全面分析两个字符串的差异
        
        Args:
            str1: 字符串1
            str2: 字符串2
            
        Returns:
            详细分析结果
        """
        # 基本信息
        analysis = {
            'length_diff': len(str2) - len(str1),
            'are_equal': str1 == str2,
            'str1_length': len(str1),
            'str2_length': len(str2),
        }
        
        # 找出所有差异
        differences = self.find_string_differences(str1, str2)
        analysis['differences'] = differences
        analysis['diff_count'] = len(differences)
        analysis['diff_positions'] = [d['position'] for d in differences]
        
        # 分析差异类型
        diff_types = {}
        for diff in differences:
            diff_type = diff['type']
            if diff_type not in diff_types:
                diff_types[diff_type] = 0
            diff_types[diff_type] += 1
        analysis['diff_types'] = diff_types
        
        # 特殊字符分析
        analysis['str1_special_chars'] = self._find_special_chars(str1)
        analysis['str2_special_chars'] = self._find_special_chars(str2)
        
        # 编码分析
        analysis['str1_encoding_info'] = self._analyze_encoding(str1)
        analysis['str2_encoding_info'] = self._analyze_encoding(str2)
        
        return analysis
    
    def _find_special_chars(self, text: str) -> List[Dict]:
        """找出文本中的特殊字符"""
        special_chars = []
        for i, char in enumerate(text):
            if char in self.special_chars or not char.isprintable():
                special_chars.append({
                    'position': i,
                    'char_info': self.get_char_info(char)
                })
        return special_chars
    
    def _analyze_encoding(self, text: str) -> Dict:
        """分析文本编码信息"""
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252', 'gbk']
            encoding_info = {}
            
            for encoding in encodings:
                try:
                    encoded = text.encode(encoding)
                    encoding_info[encoding] = {
                        'success': True,
                        'byte_length': len(encoded),
                        'bytes_repr': repr(encoded)
                    }
                except UnicodeEncodeError as e:
                    encoding_info[encoding] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return encoding_info
        except Exception as e:
            return {'error': str(e)}
    
    def generate_char_map(self, text: str) -> str:
        """
        生成字符映射表（用于可视化）
        
        Args:
            text: 输入文本
            
        Returns:
            字符映射字符串
        """
        if not text:
            return "空字符串"
        
        char_map = []
        for i, char in enumerate(text):
            info = self.get_char_info(char)
            if info['is_invisible']:
                display = f"[{info['name'] or info['unicode_name'] or f'U+{info['hex'][2:]}'} at {i}]"
            else:
                display = char
            char_map.append(display)
        
        return ''.join(char_map)
