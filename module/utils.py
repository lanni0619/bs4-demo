# 3rd party package
import requests

# Standard module
import time
from typing import Any, Callable
from functools import wraps
import json

# Custom module
from module.logger import logger

# ===== 工具函式 =====
def all_key_not_none (data: dict) -> bool:
    if not all(data[key] is not None for key in data):
        logger.warning(f"[all_key_not_none] Key have None value")
        return False
    return True

def dict_to_json(data: dict) -> str:
    #  https://stackoverflow.com/questions/7408647/convert-dynamic-python-object-to-json
    return json.dumps(
        data,
        ensure_ascii=False,
        # default=lambda o: o.__dict__,
        sort_keys=False,
        indent=4
    )

# ===== 業務邏輯 =====
def tic_tok(func: Callable) -> Callable:
    """It's a tic_tok function"""
    # position & keyword argument. The prefix star is meaning Any number.
    def wrapper(*arg, **kwargs) -> Any:
        t1: float = time.time()
        logger.info(f"[{func.__name__}] arg={arg}, kwargs={kwargs}")
        result:Any = func(*arg, **kwargs)
        t2: float = time.time() - t1
        logger.info(f"[{func.__name__}] took {round(t2, 3)} seconds")
        return result
    return wrapper

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except requests.exceptions.RequestException as e:
            logger.error(f"[{func.__name__}] Network error: {e}")
            raise(requests.exceptions.RequestException(e))
        except AttributeError as e:
            logger.error(f"[{func.__name__}] Parsing error: {e}")
            raise(AttributeError(e))
        except Exception as e:
            logger.error(f"[{func.__name__}] Exception: {e}")
            raise(Exception(e))
            
    return wrapper

class TicTok:
    """It's a TicTok class"""
    def __init__(self, func:Callable):
        self.func = func
        """wraps(func) return a decorator"""
        # 複製func的metadata, __name__, __doc__, __annotations__ ...etc
        wraps(func)(self)
    
    def __call__(self, *args, **kwargs) -> Any:
        t1: float = time.time()
        logger.info(f"[{self.func.__name__}] args={args}, kwargs={kwargs}")
        result:Any = self.func(*args, **kwargs)
        t2: float = time.time() - t1
        logger.info(f"{self.func.__name__} took {round(t2, 3)} seconds")
        return result

@TicTok
def test_func(num):
    """It's a test_func"""
    for i in range(num):
        pass
    return None

if __name__ == "__main__":
    print(test_func.__class__)
    print(test_func.__doc__)
    test_func(1000000)