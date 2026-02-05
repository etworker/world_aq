"""
统一命令行接口

提供实验、训练、推理的统一入口
"""

import argparse
import sys

from .core.logger import LoggerManager
from .config import ensure_dirs


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    return LoggerManager.get_logger("world_aq", level=level)


def experiment_command(args):
    """实验命令"""
    from .training.experiment import ExperimentRunner
    from .data.storage.loader import load_training_data

    logger = setup_logging(args.verbose)
    logger.info("运行实验模式...")

    ensure_dirs()

    # 加载数据
    df = load_training_data(args.data)

    # 运行实验
    runner = ExperimentRunner(output_dir=args.output)
    summary = runner.run_all_experiments(
        df=df,
        modes=args.modes.split(",") if args.modes else None,
        algorithms=args.algorithms.split(",") if args.algorithms else None,
    )

    print(f"\n实验完成!")
    print(f"实验ID: {runner.experiment_id}")
    print(f"汇总: {summary}")

    return runner.experiment_id


def train_command(args):
    """训练命令"""
    from .training.production import ProductionPipeline

    logger = setup_logging(args.verbose)
    logger.info("运行生产训练模式...")

    ensure_dirs()

    # 创建流水线
    pipeline = ProductionPipeline(
        config_path=args.config,
        output_dir=args.output,
    )

    # 训练
    if args.mode:
        model_dir = pipeline.train_mode(args.mode, data_path=args.data)
        print(f"\n模型训练完成: {model_dir}")
    else:
        results = pipeline.train_all_modes(data_path=args.data)
        print(f"\n所有模型训练完成:")
        for mode, model_dir in results.items():
            print(f"  {mode}: {model_dir}")


def inference_command(args):
    """推理命令"""
    from .inference import Predictor, list_models

    logger = setup_logging(args.verbose)
    logger.info("运行推理模式...")

    if args.list:
        list_models()
        return

    if not args.model:
        print("错误: 请指定模型路径 (--model) 或使用 --list 查看可用模型")
        sys.exit(1)

    # 加载预测器
    predictor = Predictor(args.model, mode=args.mode)

    # 准备输入数据
    weather_data = {
        "temp_avg_c": args.temperature,
        "wind_speed_kmh": args.wind_speed,
        "visibility_km": args.visibility,
        "station_pressure_hpa": args.pressure,
    }

    # 预测
    result = predictor.predict(
        weather_data=weather_data,
        city=args.city,
    )

    # 输出结果
    print("\n预测结果:")
    print(f"  城市: {result['city']}")
    print(f"  PM2.5: {result['pm25']} μg/m³")
    print(f"  AQI: {result['aqi']}")
    print(f"  类别: {result['category']} ({result['category_chinese']})")
    print(f"  建议: {result['health_advice']}")


def aqi_command(args):
    """AQI命令"""
    from .aqi import calculate_aqi, get_category, format_advice

    if args.calculate:
        aqi = calculate_aqi(args.concentration, args.pollutant)
        category = get_category(aqi)
        print(f"\n{args.pollutant.upper()} = {args.concentration}")
        print(f"AQI = {aqi}")
        print(f"类别: {category['label']} ({category['chinese']})")

    if args.advice:
        advice = format_advice(args.aqi_value)
        print(f"\n{advice}")


def api_command(args):
    """API服务命令"""
    from .api import start_server

    print(f"启动API服务: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    start_server(host=args.host, port=args.port, reload=args.reload)


def autogluon_command(args):
    """AutoGluon AutoML 命令"""
    from .training.experiment import ExperimentRunner
    from .training.core import check_autogluon_available
    from .data.storage.loader import load_training_data

    logger = setup_logging(args.verbose)

    # 检查 AutoGluon 可用性
    if not check_autogluon_available():
        print("错误: AutoGluon 未安装。请运行: pip install autogluon")
        sys.exit(1)

    logger.info("运行 AutoGluon AutoML 模式...")

    ensure_dirs()

    # 加载数据
    df = load_training_data(args.data)

    # 运行实验（仅使用 AutoGluon）
    runner = ExperimentRunner(output_dir=args.output)
    summary = runner.run_all_experiments(
        df=df,
        modes=args.modes.split(",") if args.modes else None,
        algorithms=["AutoGluon"],
    )

    print(f"\nAutoGluon 实验完成!")
    print(f"实验ID: {runner.experiment_id}")
    print(f"汇总: {summary}")

    return runner.experiment_id


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="World Air Quality Prediction CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 实验命令
    exp_parser = subparsers.add_parser("experiment", help="运行实验探索最佳模型")
    exp_parser.add_argument("--data", default="data/processed/merged/all_cities.csv", help="数据路径")
    exp_parser.add_argument("--output", default=None, help="输出目录")
    exp_parser.add_argument("--modes", default=None, help="模式列表，逗号分隔")
    exp_parser.add_argument("--algorithms", default=None, help="算法列表，逗号分隔")
    exp_parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    # 训练命令
    train_parser = subparsers.add_parser("train", help="训练生产模型")
    train_parser.add_argument("--config", required=True, help="最佳配置文件路径")
    train_parser.add_argument("--mode", default=None, help="指定模式，None则训练所有")
    train_parser.add_argument("--data", default=None, help="数据路径")
    train_parser.add_argument("--output", default=None, help="输出目录")
    train_parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    # 推理命令
    inf_parser = subparsers.add_parser("inference", help="模型推理")
    inf_parser.add_argument("--model", default=None, help="模型路径")
    inf_parser.add_argument("--mode", default=None, help="预测模式")
    inf_parser.add_argument("--list", action="store_true", help="列出可用模型")
    inf_parser.add_argument("--city", default="Unknown", help="城市名称")
    inf_parser.add_argument("--temperature", type=float, default=20.0, help="温度(°C)")
    inf_parser.add_argument("--wind-speed", type=float, default=10.0, help="风速(km/h)")
    inf_parser.add_argument("--visibility", type=float, default=10.0, help="能见度(km)")
    inf_parser.add_argument("--pressure", type=float, default=1013.0, help="气压(hPa)")
    inf_parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    # AQI命令
    aqi_parser = subparsers.add_parser("aqi", help="AQI工具")
    aqi_parser.add_argument("--calculate", action="store_true", help="计算AQI")
    aqi_parser.add_argument("--pollutant", default="pm25", help="污染物")
    aqi_parser.add_argument("--concentration", type=float, help="浓度")
    aqi_parser.add_argument("--advice", action="store_true", help="获取健康建议")
    aqi_parser.add_argument("--aqi-value", type=int, help="AQI值")

    # API服务命令
    api_parser = subparsers.add_parser("api", help="启动API服务")
    api_parser.add_argument("--host", default="0.0.0.0", help="主机地址")
    api_parser.add_argument("--port", type=int, default=8000, help="端口")
    api_parser.add_argument("--reload", action="store_true", help="热重载模式")

    # AutoGluon 命令
    ag_parser = subparsers.add_parser("autogluon", help="运行AutoGluon自动机器学习")
    ag_parser.add_argument("--data", default="data/processed/merged/all_cities.csv", help="数据路径")
    ag_parser.add_argument("--output", default=None, help="输出目录")
    ag_parser.add_argument("--modes", default=None, help="模式列表，逗号分隔")
    ag_parser.add_argument("--time-limit", type=int, default=300, help="训练时间限制(秒)")
    ag_parser.add_argument("--presets", default="medium_quality", help="预设配置")
    ag_parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    args = parser.parse_args()

    if args.command == "experiment":
        experiment_command(args)
    elif args.command == "train":
        train_command(args)
    elif args.command == "inference":
        inference_command(args)
    elif args.command == "aqi":
        aqi_command(args)
    elif args.command == "api":
        api_command(args)
    elif args.command == "autogluon":
        autogluon_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
