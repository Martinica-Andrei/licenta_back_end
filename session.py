def init_session(app):
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'none'
    app.config['SESSION_COOKIE_PARTITIONED'] = True
    # if true, each request refreshes the expiration date of token
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False