from flask_talisman import Talisman

csp = {
    'default-src': [
        '\'self\'',
        'fonts.googleapis.com', # Если используете внешние шрифты
        'fonts.gstatic.com'  # Если используете внешние шрифты
    ],
    'style-src': [
        '\'self\'',
        'fonts.googleapis.com'  # Если используете внешние шрифты
    ],
    'script-src': [
        '\'self\''
    ]
}

talisman = Talisman(content_security_policy=csp)
