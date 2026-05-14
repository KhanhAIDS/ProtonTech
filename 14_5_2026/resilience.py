import asyncio
import time
import logging
from typing import Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: int = 2, *args, **kwargs):
    """9.10.1: Gọi lại API với exponential backoff"""
    delay = base_delay
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"[Retry] Max retries reached. Error: {e}")
                raise
            logger.warning(f"[Retry] Attempt {attempt + 1} failed. Retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay *= 2

async def call_with_timeout(func: Callable, timeout: float, default_response: Any = None, *args, **kwargs):
    """9.10.2: Đặt timeout cho API call"""
    try:
        return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"[Timeout] Hủy request sau {timeout}s.")
        if default_response is not None:
            return default_response
        raise

async def fallback_chain(primary_func: Callable, default_response: Any, *args, **kwargs):
    """9.10.3: Thử API chính, nếu fail thì trả cache/default"""
    try:
        return await primary_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"[Fallback] Primary failed ({e}). Trả response mặc định.")
        return default_response

class CircuitBreaker:
    """9.10.4: Ngắt gọi API nếu fail quá nhiều lần liên tục"""
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0

    async def call(self, func: Callable, *args, **kwargs):
        current_time = time.time()
        
        if self.state == "OPEN":
            if current_time - self.last_failure_time > self.recovery_timeout:
                logger.info("[CircuitBreaker] HALF_OPEN: Thử lại request...")
                self.state = "HALF_OPEN"
            else:
                raise Exception("[CircuitBreaker] OPEN: Request bị từ chối.")
                
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                logger.info("[CircuitBreaker] Phục hồi thành công -> CLOSED.")
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = current_time
            logger.warning(f"[CircuitBreaker] Lỗi {self.failures}/{self.failure_threshold}")
            if self.failures >= self.failure_threshold:
                logger.error("[CircuitBreaker] Vượt ngưỡng lỗi -> OPEN.")
                self.state = "OPEN"
            raise e

openai_circuit = CircuitBreaker()