"""
模型注册表
管理模型类和算法的注册（惰性加载）
"""

from typing import Dict, Type, Any, Callable

from loguru import logger


class ModelRegistry:
    """模型注册表 - 支持惰性加载"""

    _models: Dict[str, Type] = {}
    _algorithms: Dict[str, Dict[str, Any]] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        """确保已初始化（惰性加载）"""
        if not cls._initialized:
            cls._initialized = True
            _register_all_models()

    @classmethod
    def register_model(cls, name: str, model_class: Type) -> None:
        """
        注册模型类

        Args:
            name: 模型名称
            model_class: 模型类
        """
        cls._models[name] = model_class
        logger.debug(f"注册模型: {name}")

    @classmethod
    def get_model_class(cls, name: str) -> Type:
        """
        获取模型类

        Args:
            name: 模型名称

        Returns:
            模型类

        Raises:
            KeyError: 模型未注册
        """
        cls._ensure_initialized()
        if name not in cls._models:
            raise KeyError(f"未注册的模型: {name}，可用模型: {list(cls._models.keys())}")
        return cls._models[name]

    @classmethod
    def register_algorithm(
        cls,
        name: str,
        model_class: Type,
        default_params: Dict[str, Any] = None,
    ) -> None:
        """
        注册算法

        Args:
            name: 算法名称
            model_class: 模型类
            default_params: 默认参数
        """
        cls._models[name] = model_class
        cls._algorithms[name] = {
            "class": model_class,
            "default_params": default_params or {},
        }
        logger.debug(f"注册算法: {name}")

    @classmethod
    def create_model(cls, name: str, **params) -> Any:
        """
        创建模型实例

        Args:
            name: 算法名称
            **params: 模型参数

        Returns:
            模型实例
        """
        cls._ensure_initialized()
        if name not in cls._algorithms:
            raise KeyError(f"未注册的算法: {name}")

        algorithm_info = cls._algorithms[name]
        model_class = algorithm_info["class"]
        default_params = algorithm_info["default_params"].copy()
        default_params.update(params)

        return model_class(**default_params)

    @classmethod
    def list_algorithms(cls) -> list:
        """列出所有已注册算法"""
        cls._ensure_initialized()
        return list(cls._algorithms.keys())

    @classmethod
    def get_algorithm_info(cls, name: str) -> Dict[str, Any]:
        """获取算法信息"""
        cls._ensure_initialized()
        return cls._algorithms.get(name, {})


def _register_sklearn_models():
    """注册sklearn模型"""
    try:
        from sklearn.linear_model import Ridge, Lasso, ElasticNet
        from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor

        ModelRegistry.register_algorithm("Ridge", Ridge, {"alpha": 1.0})
        ModelRegistry.register_algorithm("Lasso", Lasso, {"alpha": 1.0})
        ModelRegistry.register_algorithm("ElasticNet", ElasticNet, {"alpha": 1.0, "l1_ratio": 0.5})
        ModelRegistry.register_algorithm(
            "RandomForest", RandomForestRegressor, {"n_estimators": 100, "max_depth": 15, "random_state": 42, "n_jobs": -1}
        )
        ModelRegistry.register_algorithm(
            "GradientBoosting", HistGradientBoostingRegressor, {"max_iter": 200, "max_depth": 5, "random_state": 42}
        )
        logger.info("已注册sklearn模型")
    except ImportError as e:
        logger.warning(f"sklearn导入失败: {e}")


def _register_autogluon():
    """注册AutoGluon模型包装器"""
    try:
        from ..training.core.autogluon_trainer import AutoGluonTrainer, AUTOGluon_AVAILABLE

        if AUTOGluon_AVAILABLE:
            ModelRegistry.register_algorithm(
                "AutoGluon",
                AutoGluonTrainer,
                {
                    "time_limit": 300,
                    "presets": "medium_quality",
                    "eval_metric": "rmse",
                },
            )
            logger.info("已注册AutoGluon模型")
    except ImportError:
        logger.debug("AutoGluon 不可用，跳过注册")


def _register_all_models():
    """注册所有模型（内部调用）"""
    _register_sklearn_models()
    _register_autogluon()


# 兼容性保留：显式注册函数
def register_sklearn_models():
    """注册sklearn模型（兼容性保留）"""
    _register_sklearn_models()


def register_autogluon():
    """注册AutoGluon模型（兼容性保留）"""
    _register_autogluon()
