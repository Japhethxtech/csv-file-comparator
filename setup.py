"""
CSV文件比对工具安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="csv-file-comparator",
    version="1.0.0",
    author="Japhethxtech",
    author_email="your.email@example.com",
    description="专业的CSV文件字符级精确比对工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Japhethxtech/csv-file-comparator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "chardet>=4.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "csv-comparator=csv_comparator.cli:main",
        ],
    },
    keywords="csv comparison diff character analysis unicode",
    project_urls={
        "Bug Reports": "https://github.com/Japhethxtech/csv-file-comparator/issues",
        "Source": "https://github.com/Japhethxtech/csv-file-comparator",
        "Documentation": "https://github.com/Japhethxtech/csv-file-comparator#readme",
    },
)
