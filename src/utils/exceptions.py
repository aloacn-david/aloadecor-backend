"""
异常处理模块
定义各种抓取和分析过程中可能出现的异常
"""
from typing import Optional, Dict, Any
from datetime import datetime


class ScrapingException(Exception):
    """基础抓取异常"""
    def __init__(self, message: str, error_type: str = "scraping_error", 
                 context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context
        }


class PageLoadException(ScrapingException):
    """页面加载失败异常"""
    def __init__(self, message: str, url: str, 
                 retry_count: int = 0, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"url": url, "retry_count": retry_count})
        super().__init__(message, "page_load_failed", ctx)


class ElementNotFoundException(ScrapingException):
    """元素未找到异常（页面结构变化）"""
    def __init__(self, message: str, selector: str, 
                 url: str, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"selector": selector, "url": url})
        super().__init__(message, "element_not_found", ctx)


class ContentMissingException(ScrapingException):
    """内容缺失异常"""
    def __init__(self, message: str, content_type: str, 
                 url: str, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"content_type": content_type, "url": url})
        super().__init__(message, "content_missing", ctx)


class RateLimitException(ScrapingException):
    """访问限制异常"""
    def __init__(self, message: str, url: str, 
                 retry_after: Optional[int] = None,
                 context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"url": url, "retry_after": retry_after})
        super().__init__(message, "rate_limited", ctx)


class PriceDiscrepancyException(ScrapingException):
    """价格差异异常"""
    def __init__(self, message: str, expected_price: float, 
                 actual_price: float, region: str,
                 context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({
            "expected_price": expected_price,
            "actual_price": actual_price,
            "region": region,
            "difference": abs(expected_price - actual_price)
        })
        super().__init__(message, "price_discrepancy", ctx)


class ValidationException(ScrapingException):
    """数据验证异常"""
    def __init__(self, message: str, field: str, 
                 value: Any, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"field": field, "value": value})
        super().__init__(message, "validation_error", ctx)


class RetryableException(ScrapingException):
    """可重试的异常"""
    def __init__(self, message: str, error_type: str,
                 max_retries: int = 3, context: Optional[Dict[str, Any]] = None):
        ctx = context or {}
        ctx.update({"max_retries": max_retries})
        super().__init__(message, error_type, ctx)
        self.max_retries = max_retries


class NonRetryableException(ScrapingException):
    """不可重试的异常"""
    def __init__(self, message: str, error_type: str,
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_type, context)
