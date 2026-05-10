import os
def register(session, db, bcrypt, User, request, jsonify, text):
    # 尝试解析 JSON 数据
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Invalid request data format."
        }), 400

    # 从 JSON 数据中提取字段
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')  # 注意 key 是 confirmPassword
    captcha = data.get('captcha', '').upper()

    # 验证必填字段是否存在
    if not all([username, email, password, confirm_password, captcha]):
        return jsonify({
            "success": False,
            "message": "All fields are required!"
        }), 400

    # 验证验证码
    if captcha != session.get('captcha_text', ''):
        return jsonify({
            "success": False,
            "message": "Invalid captcha!"
        }), 400

    # 验证密码匹配
    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match!"
        }), 400

    # 验证用户名和邮箱是否已存在
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return jsonify({
            "success": False,
            "message": "Username or Email already exists!"
        }), 400

    # 创建新用户
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, passwd_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # 查询用户id而不是名字
        user = User.query.filter_by(username=username).first()

        # 创建用户数据目录(/ProjectM/users/{user_id}/data)
        user_dir = os.path.join('/ProjectM', 'users', str(user.id), 'data')
        os.makedirs(user_dir, exist_ok=True)

        return jsonify({
            "success": True,
            "message": "Registration successful!",
            "redirect": "/login"
        }), 200
    
    except Exception as e:
        db.session.rollback()  # 回滚事务
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }), 500
    