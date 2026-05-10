import os

def upload_raw_files(session, request, jsonify):
    """ 处理文件上传 """
    user_id = session.get("user_id")
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # 目标文件存储路径
    upload_dir = os.path.join("/ProjectM/users", str(user_id), "data")
    os.makedirs(upload_dir, exist_ok=True)  # 确保目录存在

    filepath = os.path.join(upload_dir, file.filename)
    
    file.save(filepath)  # 保存文件

    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200
