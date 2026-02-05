"""
FastAPI 服务主入口

启动命令:
    uvicorn src.api.server:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

# 创建应用
app = FastAPI(
    title="World Air Quality Prediction API",
    description="空气质量预测API服务",
    version="1.0.0",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "World Air Quality Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/docs")
async def docs_redirect():
    """API文档"""
    return {"url": "/docs"}


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    启动服务器

    Args:
        host: 主机地址
        port: 端口
        reload: 是否热重载
    """
    import uvicorn

    uvicorn.run("src.api.server:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    start_server()
