from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import get_settings

# echo控制sql执行过程中的信息输出，开发过程用True比较好，也可以先比较看看
async_engine = create_async_engine(get_settings().ASYNC_DATABASE_URL, echo=False)
# 创建orm模型基类
Base = declarative_base()
# 创建异步会话管理对象
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)
