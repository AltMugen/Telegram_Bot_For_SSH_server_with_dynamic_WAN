# path_to_your_webapp.py
from webapp import app
from config import webapp_local_port

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=webapp_local_port, ssl_context='adhoc')
