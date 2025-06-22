from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.database import async_engine, Base, AsyncSession
from dependencies import get_db_session
from services.short import ShortServeries
from services.user import UserServeries
from starlette.status import HTTP_401_UNAUTHORIZED
from utils.auth_helper import AuthToeknHelper
from utils.passlib_helper import PasslibHelper
from datetime import timedelta, datetime
from schemas import SingleShortUrlCreate
from utils.random_helper import generate_short_url
from fastapi import File, UploadFile

router_user = APIRouter(prefix="/api/v1", tags=["用户创建短链管理"])
# 需要请求的是完整的路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth2/authorize")


# 定义用户认证接口
@router_user.post("/oauth2/authorize", summary="请求授权url地址")
async def login(user_data: OAuth2PasswordRequestForm = Depends(), db_session: AsyncSession = Depends(get_db_session)):
    if not user_data:
        raise HTTPException(status_code=400, detail="用户数据不能为空")
    # 查询用户是否存在
    user_info = await UserServeries.get_user_by_name(db_session, username=user_data.username)
    if not user_info:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="不存在此用户信息",
                            headers={"WWW-Authenticate": "Basic"})
    if not PasslibHelper.verity_password(user_data.password, user_info.password):
        raise HTTPException(status_code=400, detail="密码错误")
    data = {
        'iss': user_info.username,
        'sub': 'zwp',
        'username': user_info.username,
        'admin': True,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    }
    # 生成token
    token = AuthToeknHelper.token_encode(data=data)
    return {"access_token": token, "token_type": "bearer"}


# 定义单挑短链生成接口
@router_user.post("/create/single/short", summary="创建单条短链")
async def create_single(createinfo: SingleShortUrlCreate, token: str = Depends(oauth2_scheme),
                        db_session: AsyncSession = Depends(get_db_session)):
    payload = AuthToeknHelper.token_decode(token=token)
    # 定义认证异常信息
    username = payload.get('username')
    createinfo.short_tag = generate_short_url()
    createinfo.short_url = f"{createinfo.short_url}{createinfo.short_tag}"
    createinfo.created_by = username
    createinfo.msg_context = f"{createinfo.msg_context},了解详情请点击 {createinfo.short_url} ！"
    result = await ShortServeries.create_short_url(db_session, **createinfo.dict())
    return {"code": 200, "msg": "创建短链成功", "data": {
        "short_url": result.short_url
    }}


# 定义多条短链生成接口
@router_user.post("/creat/batch/short", summary="通过上传文件方式,批量创建短链")
async def creat_batch(*, file: UploadFile = File(...),
                      token: str = Depends(oauth2_scheme),
                      db_session: AsyncSession = Depends(get_db_session)):
    payload = AuthToeknHelper.token_decode(token=token)
    # 定义认证异常信息
    username = payload.get('username')
    contents = await file.read()
    shorl_msg = contents.decode(encoding='utf-8').split("\n")

    def make_short_url(item):
        split_item = item.split("#")
        short_tag = generate_short_url()
        short_url = f"http://127.0.0.1:8000/{short_tag}"
        return SingleShortUrlCreate(
            long_url=f"{split_item[2]}{split_item[0]}",
            short_tag=short_tag,
            short_url=short_url,
            created_by=username,
            msg_context=f"{split_item[1].replace('chanename', split_item[0]).replace('url', 'short_url')}")

    result = await ShortServeries.create_batch_short_url(db_session, [make_short_url(item) for item in shorl_msg])
    return {"code": 200, "msg": "批量创建短链成功", "data":None}
