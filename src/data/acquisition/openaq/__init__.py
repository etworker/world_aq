"""
OpenAQ数据获取模块

从OpenAQ API获取空气质量数据
"""

from .client import OpenAQClient

try:
    from .s3_downloader import OpenAQS3Downloader

    __all__ = ["OpenAQClient", "OpenAQS3Downloader"]
except ImportError:
    __all__ = ["OpenAQClient"]
