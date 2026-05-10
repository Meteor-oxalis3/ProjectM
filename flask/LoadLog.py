from CleanLog import clean_log
def load_log(text_file_path, jsonify):
    try:
        # 注释掉的是直接读取文件内容的方法，现在改为调用clean_log函数，正则匹配日志文件内容
        # with open(text_file_path, 'r') as file:
            # content = file.read()
            content = clean_log(text_file_path)
            return jsonify({
                "success": True,
                "content": content
            })
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "message": "File not found."
        })