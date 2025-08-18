from datetime import datetime
from app.extensions import db
from datetime import datetime

# Роль пользователя
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

# Подразделение
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

# Должность
class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    department = db.relationship('Department', backref='positions')
    description = db.Column(db.Text)

# Сотрудник
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)
    ip_address = db.Column(db.String(45))  # IP рабочего места
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    role = db.relationship('Role')
    department = db.relationship('Department')
    position = db.relationship('Position')

# Цикл оценки
class EvaluationCycle(db.Model):
    __tablename__ = 'evaluation_cycles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)

# Категория метрики
class MetricCategory(db.Model):
    __tablename__ = 'metric_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=0.25)

# Шаблон метрики
class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('metric_categories.id'), nullable=False)
    category = db.relationship('MetricCategory')
    max_score = db.Column(db.Float, default=10.0)
    scale_type = db.Column(db.String(20), default='10-point')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    is_active = db.Column(db.Boolean, default=True)
    weight = db.Column(db.Float, default=1.0)

    department = db.relationship('Department', backref='custom_metrics')

# Оценка сотрудника по метрике
class EmployeeMetric(db.Model):
    __tablename__ = 'employee_metrics'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    metric_id = db.Column(db.Integer, db.ForeignKey('performance_metrics.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('evaluation_cycles.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='metrics_received')
    metric = db.relationship('PerformanceMetric')
    cycle = db.relationship('EvaluationCycle', backref='evaluations')
    evaluator = db.relationship('Employee', foreign_keys=[evaluator_id])

# Тип обратной связи
class FeedbackType(db.Model):
    __tablename__ = 'feedback_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Обратная связь
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('evaluation_cycles.id'))
    feedback_type_id = db.Column(db.Integer, db.ForeignKey('feedback_types.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='received_feedback')
    sender = db.relationship('Employee', foreign_keys=[sender_id])
    cycle = db.relationship('EvaluationCycle', backref='feedbacks')
    feedback_type = db.relationship('FeedbackType')

# Сообщение из формы обратной связи (публичное)
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

# --- Контент для сайта (редактируется админом/менеджером) ---
class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Общее')
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    
    author = db.relationship('Employee', backref='faqs_created')


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    image_url = db.Column(db.String(500))

    author = db.relationship('Employee', backref='news_created')