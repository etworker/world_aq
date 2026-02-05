"""
自定义异常类
"""


class WorldAQException(Exception):
    """基础异常类"""

    pass


class DataNotFoundError(WorldAQException):
    """数据未找到异常"""

    pass


class ModelNotFoundError(WorldAQException):
    """模型未找到异常"""

    pass


class ConfigurationError(WorldAQException):
    """配置错误异常"""

    pass


class TrainingError(WorldAQException):
    """训练错误异常"""

    pass


class InferenceError(WorldAQException):
    """推理错误异常"""

    pass


class ValidationError(WorldAQException):
    """验证错误异常"""

    pass


class ExperimentError(WorldAQException):
    """实验错误异常"""

    pass
