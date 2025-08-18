from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Роль пользователя
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Подразделение
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

# Должность
class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    department = db.relationship('Department', backref='positions')

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

    role = db.relationship('Role')
    department = db.relationship('Department')
    position = db.relationship('Position')

# Проект
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

# Задача
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, done
    priority = db.Column(db.String(50))  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    result_count = db.Column(db.Integer, default=0)  # счётчик подзадач/результатов
    accuracy_score = db.Column(db.Float, default=0.0)  # корректность выполнения

    employee = db.relationship('Employee', backref='tasks')
    project = db.relationship('Project', backref='tasks')

# Цикл оценки
class EvaluationCycle(db.Model):
    __tablename__ = 'evaluation_cycles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

# Шаблон KPI (метрика)
class PerformanceMetric(db.Model):
    __tablename__ = 'performance_metrics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)
    max_score = db.Column(db.Float, default=10.0)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    department = db.relationship('Department', backref='metrics')

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

    employee = db.relationship('Employee', backref='metrics')
    metric = db.relationship('PerformanceMetric')
    cycle = db.relationship('EvaluationCycle')

# Обратная связь
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    cycle_id = db.Column(db.Integer, db.ForeignKey('evaluation_cycles.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship('Employee', foreign_keys=[employee_id])
    manager = db.relationship('Employee', foreign_keys=[manager_id])
    cycle = db.relationship('EvaluationCycle', backref='feedbacks')

# Сообщение из формы обратной связи
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)