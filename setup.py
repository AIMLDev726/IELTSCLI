"""
Setup script for IELTS Practice CLI package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]
else:
    requirements = [
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "SQLAlchemy>=2.0.25",
        "aiosqlite>=0.19.0",
        "aiohttp>=3.9.1",
        "openai>=1.12.0",
        "cryptography>=41.0.8",
        "pydantic>=2.5.3",
    ]


setup(
    name="ieltscli",
    version="1.0.0",
    description="AI-powered IELTS writing practice and assessment CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AIML Development Team",
    author_email="aistudentlearn4@gmail.com",
    url="https://github.com/AIMLDev726/IELTSCLI",
    license="MIT",
    
    # Package information
    packages=find_packages(),
    include_package_data=True,
    
    # Dependencies
    install_requires=requirements,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for CLI commands
    entry_points={
        "console_scripts": [
            "ieltscli=main:app",
        ],
    },
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Education :: Testing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    
    # Keywords
    keywords=[
        "ielts", "writing", "assessment", "cli", "ai", "education", 
        "language", "test", "practice", "feedback", "english", "band-score"
    ],
    
    # Additional metadata
    project_urls={
        "Documentation": "https://github.com/AIMLDev726/IELTSCLI/tree/main/docs",
        "Source": "https://github.com/AIMLDev726/IELTSCLI",
        "Bug Reports": "https://github.com/AIMLDev726/IELTSCLI/issues",
        "Homepage": "https://github.com/AIMLDev726/IELTSCLI",
    },
    
    # Package data
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"],
        "docs": ["*.md"],
    },
    
    # Development dependencies (optional)
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.2",
            "pytest-mock>=3.12.0",
            "coverage>=7.4.0",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "mypy>=1.8.0",
        ],
        "analysis": [
            "nltk>=3.8.1",
            "textstat>=0.7.3",
        ],
    },
    
    # Zip safe
    zip_safe=False,
)
