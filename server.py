import os

from flask import Flask, request, jsonify
import logging


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response, 'слона')

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def handle_dialog(req, res, text):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = f'Привет! Купи {text}!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю',
        'я хочу купить'
    ]:
        res['response']['text'] = f'{text} можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {text}!"
    res['response']['buttons'] = get_suggests(user_id, text)[0]
    res['response']['text'] = 'Купи кролика!'
    text = get_suggests(user_id, text)[1]
    handle_dialog(request.json, res, text)


def get_suggests(user_id, text):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={text[:-1]}"
        })
    return (suggests, "кролика")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)