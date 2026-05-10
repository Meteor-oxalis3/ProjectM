def logout(session, jsonify):
    try:
        # 清除会话
        session.clear()

        response = jsonify({
            "success": True,
            "message": "Logged out successfully.",
            "redirect": "/login"
        })
        response.set_cookie('session', '', expires=0)  # 让 session 失效
        return response, 200

    except Exception as e:
        print(f"Logout error: {e}")  # 仅在服务器端打印日志
        return jsonify({
            "success": False,
            "message": "An internal server error occurred."
        }), 500
