from flask import Flask
from GenCaptcha import captcha
from TryRegister import register
from Logout import logout
from TryLogin import login
from GetCurrentUser import current_user
from GetUserUploadFiles import user_upload_files
from DeleteUserUploadFiles import delete_user_files
from GetUserWorkflows import user_workflows
from DeleteWorkflows import delete_user_workflows
from ReceiveTask import receive_files
from OpenWorkflowDialog import workflow_data
from GetResultsFiles import user_results
from DownloadResultsFiles import results_dowload
from Preview import preview_results
from UploadFiles import upload_raw_files
from DashboardResults import dashboard_results

from flask import Flask, request, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text, Column, String, UUID
import uuid
import os

# 创建一个Flask实例
app = Flask(__name__)

# flask的session需要用到secret_key
# 这个key值可以随便设置，但是一定要保密，不能泄露
# 我使用环境变量来设置这个值，如果环境变量没有设置，则使用默认值
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')

from datetime import timedelta

# 让 session 永不过期
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365 * 100)  # 100 年

@app.before_request
def make_session_permanent():
    session.permanent = True  # 让 session 持久化


# 配置数据库连接信息
# 这里也使用了环境变量来设置数据库连接信息
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://drcan:Ww112304@172.17.0.1:13306/drcan'
)

# 创建数据库对象
db = SQLAlchemy(app)
# 创建bcrypt对象
bcrypt = Bcrypt(app)
# 创建数据库模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # 使用 UUID 作为主键
    username = db.Column(db.String(20), unique=True, nullable=False)  # 用户名
    email = db.Column(db.String(255), unique=True, nullable=False)  # 邮箱
    passwd_hash = db.Column(db.String(255), nullable=False)  # 加密后的密码

class WorkflowAlias(db.Model):
    __tablename__ = 'workflowsAlias'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # 使用 UUID 作为主键
    user_id = db.Column(db.String(255), nullable=False)  # 用户id
    alias = db.Column(db.String(255), nullable=False)  # 别名
    uuid = db.Column(db.String(255), nullable=False)

# 生成验证码图片，返回一个图片文件
@app.route('/captcha', methods=['GET'])
def gen_captcha():
    result = captcha(send_file, session)
    return result

# 注册
@app.route('/register', methods=['POST'])
def to_register():
    result = register(session, db, bcrypt, User, request, jsonify, text)
    return result

# 登录
@app.route('/login', methods=['POST'])
def to_login():
    result = login(request, jsonify, session, bcrypt, User)
    return result

# 登出
@app.route('/logout', methods=['POST'])
def tryLogout():
    result = logout(session, jsonify)
    return result

# 获取当前用户
@app.route('/current_user', methods=['GET'])
def get_current_user():
    result = current_user(session, User, jsonify)
    return result

# 获取当前用户文件
@app.route('/user_upload_files', methods=['GET'])
def get_user_upload_files():
    result = user_upload_files(session, User, jsonify)
    return result

# 删除用户上传的文件
@app.route('/delete_files', methods=['POST'])
def to_delete_files():
    result = delete_user_files(User, session, request, jsonify)
    return result

# 接受前端传来的文件列表和提示词信息给ai处理
@app.route('/receive', methods=['POST'])
def receive_task():
    result = receive_files(request, jsonify, WorkflowAlias, db)
    return result

# 获取用户的工作流
@app.route('/user_workflows', methods=['GET'])
def get_user_workflows():
    result = user_workflows(session, User, jsonify, WorkflowAlias, db)
    return result

# 删除用户的工作流
@app.route('/delete_workflows', methods=['POST'])
def delete_workflows():
    result = delete_user_workflows(User, session, request, jsonify, WorkflowAlias, db)
    return result

# 获取DAG图数据
@app.route('/workflow_data', methods=['POST'])
def get_workflow_data():
    result = workflow_data(jsonify, session, request)
    return result

# 获取用户结果文件
@app.route('/user_results', methods=['GET'])
def get_user_results():
    result = user_results(session, User, jsonify, WorkflowAlias, db)
    return result

# 下载用户结果文件
@app.route('/results_download', methods=['POST'])
def get_results_dowload():
    result = results_dowload(session, jsonify, request)
    return result

# 一点进来就能看见哪个流程跑完了的结果
@app.route('/dashboard_results', methods=['GET'])
def get_dashboard_results():
    result = dashboard_results(session, User, jsonify, WorkflowAlias, db)
    return result

# 预览
@app.route('/preview', methods=['POST'])
def to_preview():
    result = preview_results(jsonify, request, session)
    return result

# 上传文件
@app.route('/upload_raw_files', methods=['POST'])
def to_upload_raw_files():
    result = upload_raw_files(session, request, jsonify)
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
