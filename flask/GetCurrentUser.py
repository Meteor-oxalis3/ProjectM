import os
import uuid
def current_user(session, User, jsonify):
    if 'user_id' in session:
        user = User.query.get(uuid.UUID(session['user_id']))
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "username": user.username
                }
            }), 200
    return jsonify({"success": False, "message": "User not logged in"}), 401