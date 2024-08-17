import sys
import os
import pandas as pd

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from finance_sample import create_app
from finance_sample.models import db, Company

# アプリケーションの作成とデータベースの初期化
app = create_app()

# Excelファイルのパス
excel_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data_j.xls')

# Excelファイルを読み込む
data = pd.read_excel(excel_file_path)

# Flaskアプリケーションコンテキスト内でデータをデータベースに挿入
with app.app_context():
    for index, row in data.iterrows():
        company = Company(company_name=row['銘柄名'], stock_code=row['コード'])
        db.session.add(company)
    db.session.commit()
    print("Data inserted successfully into the database.")
