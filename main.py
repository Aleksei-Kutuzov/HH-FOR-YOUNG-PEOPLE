import os
import threading

from flask import Flask, render_template, request, session
from turbo_flask import Turbo
from flask import request, render_template
import threading

import promts
from pix2pix import PIX2PIX
import uuid

# Создание случайного UUID
random_uuid = uuid.uuid4()
print(random_uuid)


class YouNeiroProfFrame(Flask):
    def __init__(self, import_name: str, MAX_CONTENT_LENGTH: int=16 * 1024 * 1024):
        super().__init__(import_name)
        self.turbo = Turbo(self)

        self.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Ограничение на размер файла: 16 MB
        self.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'} # Разрешенные типы файлов

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.config['ALLOWED_EXTENSIONS']

    def pix2pix_model_query(self, model: PIX2PIX, filename: str, profession: str, id: uuid.uuid4):
        promt = promts.promts[profession]
        with app.app_context():
            self.turbo.push(self.turbo.replace(render_template("preloader.html", id=str(id)), str(id)))
        PIX2PIX.model_query(model, filename, promt)
        print("Q RETURN")
        with app.app_context():
            print()
            print(str(id))
            self.turbo.push(self.turbo.replace(f"<img src='static/generates/{filename}' class='card-img-top' alt='...' id='{str(id)}'>", str(id)))


app = YouNeiroProfFrame(__name__)
os.environ["REPLICATE_API_TOKEN"] = "¯\_(ツ)_/¯"

model = PIX2PIX()

app.secret_key = 'secret_key'  # Задайте ключ для подписи сессий

@app.before_request
def assign_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Генерация уникального ID для пользователя


@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', name=__name__)

@app.route("/profession-choose", methods=['GET', 'POST'])
def choose_profession():
    user_id = session.get('user_id')  # Получаем текущий идентификатор пользователя
    loading_div_id = f"load-{user_id}"  # Уникальный ID для обновлений
    return render_template('profession-choose.html', profession_list=list(promts.promts.keys()), allowedTypes=list(app.config['ALLOWED_EXTENSIONS']), id=loading_div_id)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'profession-choose-file' not in request.files:
        return '', 400  # Вернуть код ошибки
    file = request.files['profession-choose-file']
    if file.filename == '':
        return '', 400  # Вернуть код ошибки
    if file and app.allowed_file(file.filename):
        user_id = session.get('user_id')  # Получаем текущий идентификатор пользователя
        loading_div_id = f"load-{user_id}"  # Уникальный ID для обновлений
        filename = file.filename + user_id
        file.save(f"uploads/" + filename)
        # Запуск фоновой задачи
        profession = request.form.get("profession-option")
        print(profession)
        if profession:
            threading.Thread(target=app.pix2pix_model_query, args=(model, filename, profession, loading_div_id)).start()
        else:
            return '', 400  # Вернуть код ошибки
        return '', 204  # Возвращаем статус "No Content"
    return '', 400  # Вернуть код ошибки



if __name__ == "__main__":
    app.run(debug=True)