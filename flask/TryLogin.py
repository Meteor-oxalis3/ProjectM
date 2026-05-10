def login(request, jsonify, session, bcrypt, User):
    if request.method == 'POST':
        try:
            # 获取 JSON 数据
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # 验证必填字段是否存在
            if not username or not password:
                return jsonify({
                    "success": False,
                    "message": "Username and password are required."
                }), 400

            # 查询用户
            user = User.query.filter_by(username=username).first()

            if user and bcrypt.check_password_hash(user.passwd_hash, password):
                # 设置会话
                session['user_id'] = user.id

                return jsonify({
                    "success": True,
                    "message": "Logged in successfully!",
                    "redirect": "/upload",
                    "user": {
                        "id": user.id,
                        "username": user.username
                    }
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "Invalid username or password."
                }), 401

        except Exception as e:
            print(f"Login error: {e}")  # 记录错误日志，避免直接暴露给前端
            return jsonify({
                "success": False,
                "message": "An internal server error occurred."
            }), 500
