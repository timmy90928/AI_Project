# pigar gen --with-referenced-comments
# pip freeze > requirements.txt
from routes import app as APP
from routes import ALL_BP as ALL_BP
from routes import admin as _admin

from flask_admin import Admin as FlaskAdmin
from dotenv import load_dotenv # pip install python-dotenv

admin_view = FlaskAdmin(APP, name=APP.config['TITLE'], template_mode='bootstrap3')
for view in _admin.ALL_ADMIN_VIEW:
    admin_view.add_view(view)

### Register blueprint ###
DEBUG = True
for bp in ALL_BP:
    APP.register_blueprint(bp)

if __name__ == "__main__":
    load_dotenv()
    APP.run(host="0.0.0.0",port="121",debug=DEBUG)