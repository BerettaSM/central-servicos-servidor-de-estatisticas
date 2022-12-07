import requests


def get_jwt():
    body = {
        'username': 'STATISTICS_SERVER',
        'password': 'Ask*odsJ@231S(*u2XShjdh89123'
    }
    res = requests.post('http://localhost:8080/api/auth/login', json=body)
    return res.headers.get('Authorization')
