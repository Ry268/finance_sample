from flask import Flask
from .models import db
import os

def create_app():
    app = Flask(__name__)

    # データベースのURIを設定
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'company_database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # SQLAlchemyの初期化
    db.init_app(app)

    with app.app_context():
        db.create_all()  # モデルに基づいてテーブルを作成
        print("Database and tables created successfully.")

    return app
