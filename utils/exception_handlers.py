from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import general_exception_handler, http_exception_handler, integrity_error_handler, sqlalchemy_error_handler

#注册全局异常处理:子类在前，父类在后
def register_exception_handler(app):
    #注册异常处理器的方法，异常处理器的类型，名字
    app.add_exception_handler(HTTPException, http_exception_handler)#业务层报错
    app.add_exception_handler(IntegrityError, integrity_error_handler)#数据完整性约束
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)#数据库
    app.add_exception_handler(Exception, general_exception_handler)