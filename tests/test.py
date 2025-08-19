import sys
import os
import unittest
from io import BytesIO
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.models import db, Employee, Role, Department, Position, EvaluationCycle, PerformanceMetric

class TestApp(unittest.TestCase):

    def setUp(self):
        """Настройка тестового клиента и БД"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'testkey'

        self.app = app.test_client()

        with app.app_context():
            db.create_all()

            # Чистим данные
            db.session.query(Employee).delete()
            db.session.query(Role).delete()
            db.session.query(Department).delete()
            db.session.query(Position).delete()
            db.session.query(EvaluationCycle).delete()
            db.session.query(PerformanceMetric).delete()
            db.session.commit()

            # Создаём роли
            admin_role = Role(name='admin', description='Админ')
            employee_role = Role(name='employee', description='Сотрудник')
            db.session.add_all([admin_role, employee_role])
            db.session.commit()

            # Подразделение и должность
            dept = Department(name="Тестовый отдел")
            db.session.add(dept)
            db.session.commit()

            pos = Position(title="Тестовая должность", department_id=dept.id)
            db.session.add(pos)
            db.session.commit()

            # Администратор
            from werkzeug.security import generate_password_hash
            admin = Employee(
                full_name="Тест Админ",
                email="admin@test.ru",
                password_hash=generate_password_hash("admin123"),
                role_id=admin_role.id,
                department_id=dept.id,
                position_id=pos.id
            )
            db.session.add(admin)
            db.session.commit()

            # Активный цикл оценки (обязательно!)
            cycle = EvaluationCycle(
                name="Тестовый цикл",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 31),
                is_active=True
            )
            db.session.add(cycle)
            db.session.commit()

            # Метрика (обязательно для импорта)
            metric = PerformanceMetric(
                name="Производительность",
                category_id=1,
                max_score=10.0,
                is_active=True
            )
            db.session.add(metric)
            db.session.commit()

    def tearDown(self):
        """Очистка после тестов"""
        with app.app_context():
            db.drop_all()

    def test_index_page(self):
        """Главная страница загружается"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('ИС ОЭРСК'.encode('utf-8'), response.data)

    def test_login_page(self):
        """Страница входа доступна"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Войти'.encode('utf-8'), response.data)

    def test_login_success(self):
        """Успешный вход"""
        response = self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Кабинет'.encode('utf-8'), response.data)
        self.assertIn('Добро пожаловать'.encode('utf-8'), response.data)

    def test_login_failure(self):
        """Неверный пароль"""
        response = self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неверный email или пароль'.encode('utf-8'), response.data)

    def test_dashboard_page(self):
        """Кабинет доступен после входа"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Кабинет'.encode('utf-8'), response.data)

    def test_employees_page(self):
        """Страница сотрудников доступна"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.get('/employees')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Сотрудники'.encode('utf-8'), response.data)

    def test_stats_page(self):
        """Страница статистики доступна"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Статистика'.encode('utf-8'), response.data)

    def test_faq_page(self):
        """Страница FAQ доступна"""
        response = self.app.get('/faq')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вопросы'.encode('utf-8'), response.data)

    def test_logout(self):
        """Выход из системы"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вы вышли из системы'.encode('utf-8'), response.data)

    def test_invalid_route_404(self):
        """404 на несуществующий маршрут"""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Страница не найдена'.encode('utf-8'), response.data)

    def test_export_import_page_requires_login(self):
        """Доступ к /export-import без входа — 401 Unauthorized"""
        response = self.app.get('/export-import', follow_redirects=False)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized'.encode('utf-8'), response.data)

    def test_export_import_page_accessible_for_admin(self):
        """Страница импорта/экспорта доступна админу"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.get('/export-import')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Импорт и экспорт данных'.encode('utf-8'), response.data)

    def test_export_pdf_all_employees(self):
        """Экспорт PDF — все сотрудники"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.post('/export-pdf', data={
            'report_type': 'all'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')

    def test_export_pdf_filtered(self):
        """Экспорт PDF — фильтр выше среднего"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        response = self.app.post('/export-pdf', data={
            'report_type': 'above_avg'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')

    def test_import_csv_success(self):
        """Попытка импорта CSV — отклонена (поддерживаются только .xlsx)"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        csv_content = """email,metric,score,comment
admin@test.ru,Производительность,8.5,Отличная работа
"""
        data = {
            'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')
        }
        response = self.app.post('/import-data', data=data,
                               content_type='multipart/form-data',
                               follow_redirects=True)
        # Система не поддерживает .csv
        self.assertIn('Поддерживаются только .xlsx и .xls файлы'.encode('utf-8'), response.data)

    def test_import_invalid_format(self):
        """Импорт неподдерживаемого формата (.txt)"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)
        txt_content = "это не Excel"
        data = {
            'file': (BytesIO(txt_content.encode('utf-8')), 'test.txt')
        }
        response = self.app.post('/import-data', data=data,
                               content_type='multipart/form-data',
                               follow_redirects=True)
        self.assertIn('Поддерживаются только .xlsx и .xls файлы'.encode('utf-8'), response.data)

    def test_import_xlsx_success(self):
        """Успешный импорт XLSX"""
        self.app.post('/login', data={
            'email': 'admin@test.ru',
            'password': 'admin123'
        }, follow_redirects=True)

        try:
            from openpyxl import Workbook
            from io import BytesIO as IOBuffer
        except ImportError:
            self.skipTest("openpyxl не установлен")

        wb = Workbook()
        ws = wb.active
        ws.append(["email", "metric", "score", "comment"])
        ws.append(["admin@test.ru", "Производительность", 8.5, "Тест XLSX"])

        xlsx_buffer = IOBuffer()
        wb.save(xlsx_buffer)
        xlsx_buffer.seek(0)

        data = {
            'file': (xlsx_buffer, 'test.xlsx')
        }
        response = self.app.post('/import-data', data=data,
                               content_type='multipart/form-data',
                               follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Успешно импортировано'.encode('utf-8'), response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)