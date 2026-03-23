"""
监控和日志系统
"""
import time
import logging
from functools import wraps
from typing import Callable, Any
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aloadecor-api")

# Prometheus metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'method', 'status']
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

ACTIVE_REQUESTS = Gauge(
    'api_active_requests',
    'Number of active API requests'
)

ERROR_COUNT = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['endpoint', 'error_type']
)


def monitor_api(endpoint_name: str):
    """
    API监控装饰器
    
    Args:
        endpoint_name: 端点名称
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            method = kwargs.get('request', Request).method if 'request' in kwargs else 'UNKNOWN'
            
            ACTIVE_REQUESTS.inc()
            
            try:
                result = await func(*args, **kwargs)
                
                # 记录成功请求
                status = '200'
                if hasattr(result, 'status_code'):
                    status = str(result.status_code)
                
                REQUEST_COUNT.labels(endpoint=endpoint_name, method=method, status=status).inc()
                
                return result
                
            except Exception as e:
                # 记录错误
                error_type = type(e).__name__
                ERROR_COUNT.labels(endpoint=endpoint_name, error_type=error_type).inc()
                logger.error(f"Error in {endpoint_name}: {str(e)}", exc_info=True)
                raise
            finally:
                ACTIVE_REQUESTS.de()
                duration = time.time() - start_time
                REQUEST_DURATION.labels(endpoint=endpoint_name, method=method).observe(duration)
        
        return wrapper
    return decorator


async def monitor_middleware(request: Request, call_next: Callable) -> Response:
    """
    FastAPI监控中间件
    
    Args:
        request: FastAPI请求对象
        call_next: 下一个处理函数
        
    Returns:
        Response对象
    """
    start_time = time.time()
    endpoint = request.url.path
    method = request.method
    
    ACTIVE_REQUESTS.inc()
    
    try:
        response = await call_next(request)
        
        # 记录成功请求
        REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=str(response.status_code)).inc()
        
        return response
        
    except Exception as e:
        # 记录错误
        error_type = type(e).__name__
        ERROR_COUNT.labels(endpoint=endpoint, error_type=error_type).inc()
        logger.error(f"Error processing {method} {endpoint}: {str(e)}", exc_info=True)
        raise
    finally:
        ACTIVE_REQUESTS.de()
        duration = time.time() - start_time
        REQUEST_DURATION.labels(endpoint=endpoint, method=method).observe(duration)


def get_metrics() -> tuple[str, str]:
    """
    获取Prometheus指标
    
    Returns:
        (metrics_content, content_type)
    """
    return generate_latest().decode('utf-8'), CONTENT_TYPE_LATEST
