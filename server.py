from flask import Flask, request, render_template_string, send_from_directory
import os
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

UPLOAD_FORM_HTML = """
<!doctype html>
<html>
<head>
  <title>파일 업로드 서버</title>
</head>
<body>
  <h2>파일 업로드 (피해자 → 공격자 : 파일 다운로드)</h2>
  <form method="POST" action="/upload" enctype="multipart/form-data">
    태그: <input type="text" name="tag"><br>
    파일: <input type="file" name="file"><br>
    <input type="submit" value="업로드">
  </form>
  {% if msg %}
    <p style="color:green;">{{ msg }}</p>
  {% endif %}
  <hr>
  <h3>파일 다운로드 (공격자 → 피해자 : 업로드)</h3>
  <form method="GET" action="/download">
    파일명: <input type="text" name="filename"><br>
    <input type="submit" value="다운로드">
  </form>
  {% if download_msg %}
    <p style="color:red;">{{ download_msg }}</p>
  {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UPLOAD_FORM_HTML, msg=None, download_msg=None)

# 피해자 → 공격자 (파일 다운로드)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template_string(UPLOAD_FORM_HTML, msg="파일이 첨부되지 않았습니다.", download_msg=None)
    f = request.files['file']
    tag = request.form.get('tag', 'unknown')
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tag}_{ts}_{secure_filename(f.filename)}"
    f.save(os.path.join(UPLOAD_FOLDER, filename))
    return render_template_string(UPLOAD_FORM_HTML, msg=f"업로드 완료: {filename}", download_msg=None)

# 공격자 → 피해자 (업로드) : HTML 없이 바로 파일 내려주기 (바이너리 깨짐 방지)
@app.route('/file/<filename>', methods=['GET'])
def get_file_raw(filename):
    safe_name = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    if not os.path.isfile(file_path):
        return "File not found", 404
    return send_from_directory(UPLOAD_FOLDER, safe_name, as_attachment=True)

# 기존 HTML 폼 기반 다운로드 (웹 브라우저에서 수동)
@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return render_template_string(UPLOAD_FORM_HTML, msg=None, download_msg="파일명을 입력하세요.")
    safe_name = os.path.basename(filename)
    file_path = os.path.join(UPLOAD_FOLDER, safe_name)
    if not os.path.isfile(file_path):
        return render_template_string(UPLOAD_FORM_HTML, msg=None, download_msg="존재하지 않는 파일입니다.")
    return send_from_directory(UPLOAD_FOLDER, safe_name, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9998)
