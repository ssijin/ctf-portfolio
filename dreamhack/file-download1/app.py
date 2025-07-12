#!/usr/bin/env python3
import os
import shutil

from flask import Flask, request, render_template, redirect

from flag import FLAG

APP = Flask(__name__)

# 업로드된 파일을 저장할 디렉터리 경로 - 서버 실제 디렉터리 경로
# 해당 폴더 안에 있는 파일 목록을 운영체제 파일 시스템에서 가져오는 것
UPLOAD_DIR = "uploads"


@APP.route("/")
def index():
    files = os.listdir(UPLOAD_DIR)
    return render_template("index.html", files=files)


@APP.route("/upload", methods=["GET", "POST"])
def upload_memo():
    if request.method == "POST":
        filename = request.form.get("filename")
        content = request.form.get("content").encode("utf-8")

        # 상위 디렉터리 이동 차단
        if filename.find("..") != -1:
            return render_template("upload_result.html", data="bad characters,,")

        with open(f"{UPLOAD_DIR}/{filename}", "wb") as f:
            f.write(content)

        return redirect("/")

    return render_template("upload.html")


@APP.route("/read")
def read_memo():
    error = False
    data = b""

    filename = request.args.get("name", "")

    try:
        with open(f"{UPLOAD_DIR}/{filename}", "rb") as f:
            data = f.read()
    except (IsADirectoryError, FileNotFoundError):
        error = True

    return render_template(
        "read.html", filename=filename, content=data.decode("utf-8"), error=error
    )


# 초기화
if __name__ == "__main__":
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

    os.mkdir(UPLOAD_DIR)

    APP.run(host="0.0.0.0", port=8000)
