from flask import Flask, render_template  # ← добавь render_template
from app.extensions import db, login_manager
from app.config import config
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Employee, Role

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Employee, int(user_id))

    from app.views import views as views_blueprint
    from app.auth import auth as auth_blueprint

    app.register_blueprint(views_blueprint)
    app.register_blueprint(auth_blueprint)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error_404.html'), 404

    with app.app_context():
            db.create_all()
            if Role.query.count() == 0:
                admin_role = Role(name='admin', description='Полный доступ')
                manager_role = Role(name='manager', description='Руководитель подразделения')
                employee_role = Role(name='employee', description='Обычный сотрудник')
                db.session.add_all([admin_role, manager_role, employee_role])
                db.session.commit()
    return app