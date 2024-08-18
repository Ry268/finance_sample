from flask import Flask, request, jsonify
from rapidfuzz import process, fuzz
import jaconv
from . import create_app
from .models import db, Company

import yfinance as yf

app = create_app()

def romaji_to_hiragana(romaji):
    conversion_table = {
        # 3文字のローマ字変換 (例: kya, sha)
        'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
        'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
        'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',
        'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',
        'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
        'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',
        'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',
        'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',
        'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
        'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',
        'pya': 'ぴゃ', 'pyu': 'ぴゅ', 'pyo': 'ぴょ',
        'fa': 'ふぁ', 'fi': 'ふぃ', 'fu': 'ふ', 'fe': 'ふぇ', 'fo': 'ふぉ',
        'va': 'ゔぁ', 'vi': 'ゔぃ', 'vu': 'ゔ', 've': 'ゔぇ', 'vo': 'ゔぉ',

        # 2文字のローマ字変換 (例: ka, shi, si)
        'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
        'sa': 'さ', 'shi': 'し', 'si': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
        'ta': 'た', 'chi': 'ち', 'ti': 'ち', 'tsu': 'つ', 'tu': 'つ', 'te': 'て', 'to': 'と',
        'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
        'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
        'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
        'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
        'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
        'wa': 'わ', 'wo': 'を', 'n': 'ん',

        # 濁音・半濁音
        'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
        'za': 'ざ', 'ji': 'じ', 'zi': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
        'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
        'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
        'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',

        # 1文字のローマ字変換 (例: a, i, u, e, o)
        'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',

        # 長音符
        '-': 'ー'
    }

    hiragana = ''
    i = 0
    while i < len(romaji):
        # まず3文字の変換を試みる
        if i+2 < len(romaji) and romaji[i:i+3] in conversion_table:
            hiragana += conversion_table[romaji[i:i+3]]
            i += 3
        # 次に2文字の変換を試みる
        elif i+1 < len(romaji) and romaji[i:i+2] in conversion_table:
            hiragana += conversion_table[romaji[i:i+2]]
            i += 2
        # 最後に1文字の変換を試みる
        elif romaji[i:i+1] in conversion_table:
            hiragana += conversion_table[romaji[i:i+1]]
            i += 1
        # 変換テーブルにない場合、そのまま文字を追加
        else:
            hiragana += romaji[i]
            i += 1

    return hiragana

def hiragana_to_katakana(hiragana):
    # ひらがなをカタカナに変換
    katakana = jaconv.hira2kata(hiragana)
    return katakana

@app.route('/')
def hello():
    companies = Company.query.all()
    print(companies[1].company_name + " " + companies[1].stock_code)
    return 'Hello World!'

@app.route('/api/search', methods=['GET'])
def search_companies():
    query = request.args.get('query', '')
    if query:
        # ローマ字をひらがなに変換
        hiragana_query = romaji_to_hiragana(query)
        
        # ひらがなをカタカナに変換
        katakana_query = hiragana_to_katakana(hiragana_query)

        # すべての企業名とコードを取得
        companies = Company.query.all()
        
        # 証券コードの部分一致検索
        code_matches = [
            {"id": company.id, "name": company.company_name, "code": company.stock_code}
            for company in companies if query in company.stock_code
        ]

        # RapidFuzzで企業名の曖昧検索
        name_pool = [{"id": company.id, "name": company.company_name, "code": company.stock_code} for company in companies]
        
        # 漢字、ひらがな、カタカナクエリで検索
        results = []
        for search_query in [query, hiragana_query, katakana_query]:
            results.extend(process.extract(
                search_query, 
                name_pool, 
                scorer=fuzz.partial_ratio, 
                processor=lambda entry: entry['name'] if isinstance(entry, dict) else entry,  # 辞書であることを確認
                limit=10
            ))

        # 高スコアの結果を抽出し、重複を排除
        name_matches = {match[0]['id']: match[0] for match in results if match[1] > 70}
        
        # 証券コードのマッチと企業名のマッチを結合して、重複を排除
        matched_companies = {company['id']: company for company in (list(name_matches.values()) + code_matches)}.values()
        
        return jsonify(list(matched_companies))
    
    return jsonify([])


@app.route('/api/stock', methods=['GET'])
def get_stock_data():
    company_code = request.args.get('company_code')
    stock = yf.Ticker(company_code)
    current_price = stock.history(period="1d")['Close'][0]
    valuation = "適正" if current_price >= 100 else "割安" if current_price < 100 else "割高"
    return jsonify({"current_price": current_price, "valuation": valuation})

if __name__ == '__main__':
    app.run(debug=True)