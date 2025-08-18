from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Department, db
from app.models import (
    ContactMessage, Employee, EvaluationCycle, MetricCategory,
    PerformanceMetric, EmployeeMetric, Feedback, FeedbackType,
    FAQ, News
)
from datetime import datetime

views = Blueprint('views', __name__)

# Вспомогательная функция для хлебных крошек
def render_with_breadcrumbs(template, breadcrumbs, **context):
    return render_template(template, breadcrumbs=breadcrumbs, **context)

# Проверка прав: только admin и manager
def admin_or_manager_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role.name not in ['admin', 'manager']:
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@views.route('/')
@views.route('/index')
def index():
    active_cycles = EvaluationCycle.query.filter_by(is_active=True).all()
    latest_news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(3).all()
    breadcrumbs = [("Главная", url_for('views.index'))]
    return render_with_breadcrumbs('index.html', breadcrumbs, active_cycles=active_cycles, latest_news=latest_news)

@views.route('/about')
def about():
    breadcrumbs = [("Главная", url_for('views.index')), ("О компании", url_for('views.about'))]
    return render_with_breadcrumbs('about.html', breadcrumbs)

@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash('Заполните все поля.', 'error')
        else:
            msg = ContactMessage(name=name, email=email, message=message)
            db.session.add(msg)
            db.session.commit()
            flash('Сообщение отправлено! Спасибо.', 'success')
            return redirect(url_for('views.contact'))
    breadcrumbs = [("Главная", url_for('views.index')), ("Контакты", url_for('views.contact'))]
    return render_with_breadcrumbs('contact.html', breadcrumbs)

@views.route('/admin/employees')
@login_required
@admin_or_manager_required
def admin_employees():
    if current_user.role.name == 'manager':
        employees_list = Employee.query.filter_by(department_id=current_user.department_id).all()
    else:  # admin — все
        employees_list = Employee.query.all()

    breadcrumbs = [("Главная", url_for('views.index')), ("Управление сотрудниками", "")]
    return render_with_breadcrumbs('admin_employees.html', breadcrumbs, employees=employees_list)

@views.route('/employees')
def employees():
    emps = Employee.query.filter_by(is_active=True).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Сотрудники", url_for('views.employees'))]
    return render_with_breadcrumbs('employees.html', breadcrumbs, employees=emps)

@views.route('/metrics')
def metrics():
    categories = MetricCategory.query.all()
    metrics = PerformanceMetric.query.filter_by(is_active=True).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Метрики оценки", url_for('views.metrics'))]
    return render_with_breadcrumbs('metrics.html', breadcrumbs, categories=categories, metrics=metrics)

@views.route('/cycles')
def cycles():
    cycles_list = EvaluationCycle.query.order_by(EvaluationCycle.start_date.desc()).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Циклы оценки", url_for('views.cycles'))]
    return render_with_breadcrumbs('cycles.html', breadcrumbs, cycles=cycles_list)

@views.route('/faq')
def faq():
    faq_items = FAQ.query.filter_by(is_published=True).order_by(FAQ.category, FAQ.id).all()
    categories = sorted(set(item.category for item in faq_items))
    breadcrumbs = [("Главная", url_for('views.index')), ("Частые вопросы", url_for('views.faq'))]
    return render_with_breadcrumbs('faq.html', breadcrumbs, faq_items=faq_items, categories=categories)

@views.route('/documentation')
def documentation():
    breadcrumbs = [("Главная", url_for('views.index')), ("Документация", url_for('views.documentation'))]
    return render_with_breadcrumbs('documentation.html', breadcrumbs)

@views.route('/news')
def news_list():
    news_items = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Новости", url_for('views.news_list'))]
    return render_with_breadcrumbs('news.html', breadcrumbs, news_items=news_items)

@views.route('/news/<int:news_id>')
def news_detail(news_id):
    item = News.query.filter_by(id=news_id, is_published=True).first_or_404()
    breadcrumbs = [
        ("Главная", url_for('views.index')),
        ("Новости", url_for('views.news_list')),
        (item.title, url_for('views.news_detail', news_id=item.id))
    ]
    return render_with_breadcrumbs('news_detail.html', breadcrumbs, news=item)

@views.route('/stats')
def stats():
    total_emps = Employee.query.count()
    total_cycles = EvaluationCycle.query.count()
    active_metrics = PerformanceMetric.query.filter_by(is_active=True).count()
    feedback_count = Feedback.query.count()
    breadcrumbs = [("Главная", url_for('views.index')), ("Статистика", url_for('views.stats'))]
    return render_with_breadcrumbs('stats.html', breadcrumbs,
                                   total_emps=total_emps,
                                   total_cycles=total_cycles,
                                   active_metrics=active_metrics,
                                   feedback_count=feedback_count)

@views.route('/categories')
def categories():
    cats = MetricCategory.query.all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Категории KPI", url_for('views.categories'))]
    return render_with_breadcrumbs('categories.html', breadcrumbs, categories=cats)

@views.route('/admin/faq')
@login_required
@admin_or_manager_required
def admin_faq():
    faqs = FAQ.query.order_by(FAQ.category, FAQ.id).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Админ: FAQ", url_for('views.admin_faq'))]
    return render_with_breadcrumbs('admin_faq.html', breadcrumbs, faqs=faqs)

@views.route('/admin/faq/add', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def add_faq():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category', 'Общее')
        if question and answer:
            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                author_id=current_user.id
            )
            db.session.add(faq)
            db.session.commit()
            flash("Вопрос добавлен.", "success")
            return redirect(url_for('views.admin_faq'))
        else:
            flash("Заполните вопрос и ответ.", "error")
    breadcrumbs = [("Главная", url_for('views.index')), ("Добавить FAQ", "")]
    return render_with_breadcrumbs('add_faq.html', breadcrumbs)

@views.route('/admin/faq/edit/<int:faq_id>', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def edit_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    if request.method == 'POST':
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        faq.category = request.form.get('category', 'Общее')
        faq.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Вопрос обновлён.", "success")
        return redirect(url_for('views.admin_faq'))
    breadcrumbs = [("Главная", url_for('views.index')), ("Редактировать FAQ", "")]
    return render_with_breadcrumbs('edit_faq.html', breadcrumbs, faq=faq)

@views.route('/admin/faq/delete/<int:faq_id>', methods=['POST'])
@login_required
@admin_or_manager_required
def delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash("Вопрос удалён.", "success")
    return redirect(url_for('views.admin_faq'))

@views.route('/admin/news')
@login_required
@admin_or_manager_required
def admin_news():
    news_items = News.query.order_by(News.published_at.desc()).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Админ: Новости", url_for('views.admin_news'))]
    return render_with_breadcrumbs('admin_news.html', breadcrumbs, news_items=news_items)

@views.route('/admin/news/add', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def add_news():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        published_at = request.form.get('published_at')
        image_url = request.form.get('image_url')

        if not title or not content:
            flash("Заполните заголовок и текст.", "error")
        else:
            news = News(
                title=title,
                content=content,
                published_at=datetime.fromisoformat(published_at) if published_at else datetime.utcnow(),
                image_url=image_url,
                author_id=current_user.id
            )
            db.session.add(news)
            db.session.commit()
            flash("Новость добавлена.", "success")
            return redirect(url_for('views.admin_news'))
    breadcrumbs = [("Главная", url_for('views.index')), ("Добавить новость", "")]
    return render_with_breadcrumbs('add_news.html', breadcrumbs)

@views.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def edit_news(news_id):
    news = News.query.get_or_404(news_id)
    if request.method == 'POST':
        news.title = request.form.get('title')
        news.content = request.form.get('content')
        news.published_at = datetime.fromisoformat(request.form.get('published_at'))
        news.image_url = request.form.get('image_url')
        news.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Новость обновлена.", "success")
        return redirect(url_for('views.admin_news'))
    breadcrumbs = [("Главная", url_for('views.index')), ("Редактировать новость", "")]
    return render_with_breadcrumbs('edit_news.html', breadcrumbs, news=news)

@views.route('/admin/news/delete/<int:news_id>', methods=['POST'])
@login_required
@admin_or_manager_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash("Новость удалена.", "success")
    return redirect(url_for('views.admin_news'))

# --- Защищённые страницы (для всех авторизованных) ---

@views.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    received_evals = EmployeeMetric.query.filter_by(employee_id=user.id)\
        .join(EvaluationCycle).filter(EvaluationCycle.is_active == True).all()
    given_evals = EmployeeMetric.query.filter_by(evaluator_id=user.id)\
        .join(EvaluationCycle).filter(EvaluationCycle.is_active == True).all()
    feedbacks = Feedback.query.filter_by(employee_id=user.id).all()

    breadcrumbs = [("Главная", url_for('views.index')), ("Личный кабинет", url_for('views.dashboard'))]
    return render_with_breadcrumbs('dashboard.html', breadcrumbs,
                                   user=user,
                                   received_evals=received_evals,
                                   given_evals=given_evals,
                                   feedbacks=feedbacks)

@views.route('/evaluate/<int:emp_id>', methods=['GET', 'POST'])
@login_required
def evaluate(emp_id):
    employee = Employee.query.get_or_404(emp_id)
    cycle = EvaluationCycle.query.filter_by(is_active=True).first()
    if not cycle:
        flash("Нет активного цикла оценки.", "error")
        return redirect(url_for('views.dashboard'))

    metrics = PerformanceMetric.query.filter(
        (PerformanceMetric.department_id == employee.department_id) |
        (PerformanceMetric.department_id.is_(None))
    ).filter_by(is_active=True).all()

    if request.method == 'POST':
        for metric in metrics:
            score = request.form.get(f"score_{metric.id}")
            comment = request.form.get(f"comment_{metric.id}")
            if score:
                try:
                    score = float(score)
                    if 0 <= score <= metric.max_score:
                        eval_metric = EmployeeMetric(
                            employee_id=employee.id,
                            metric_id=metric.id,
                            cycle_id=cycle.id,
                            score=score,
                            comment=comment,
                            evaluator_id=current_user.id
                        )
                        db.session.add(eval_metric)
                    else:
                        flash(f"Балл за '{metric.name}' вне диапазона.", "error")
                except ValueError:
                    flash(f"Некорректное значение для '{metric.name}'.", "error")
        db.session.commit()
        flash(f"Оценка сотрудника {employee.full_name} сохранена.", "success")
        return redirect(url_for('views.dashboard'))

    breadcrumbs = [("Главная", url_for('views.index')), ("Оценка", "")]
    return render_with_breadcrumbs('evaluate.html', breadcrumbs,
                                   employee=employee,
                                   metrics=metrics,
                                   cycle=cycle)

@views.route('/feedback/send', methods=['GET', 'POST'])
@login_required
def send_feedback():
    employees = Employee.query.filter(Employee.id != current_user.id).all()
    types = FeedbackType.query.all()

    if request.method == 'POST':
        emp_id = request.form.get('employee_id')
        type_id = request.form.get('type_id')
        content = request.form.get('content')
        is_anon = bool(request.form.get('anonymous'))

        if not emp_id or not type_id or not content:
            flash("Заполните все поля.", "error")
        else:
            fb = Feedback(
                employee_id=int(emp_id),
                sender_id=current_user.id,
                feedback_type_id=int(type_id),
                content=content,
                is_anonymous=is_anon
            )
            db.session.add(fb)
            db.session.commit()
            flash("Обратная связь отправлена.", "success")
            return redirect(url_for('views.dashboard'))

    breadcrumbs = [("Главная", url_for('views.index')), ("Отправить обратную связь", "")]
    return render_with_breadcrumbs('send_feedback.html', breadcrumbs,
                                   employees=employees, types=types)

@views.route('/admin/metrics')
@login_required
@admin_or_manager_required
def admin_metrics():
    if current_user.role.name == 'manager':
        metrics = PerformanceMetric.query.filter_by(department_id=current_user.department_id).all()
    else:
        metrics = PerformanceMetric.query.all()

    categories = MetricCategory.query.all()
    departments = Department.query.all()

    breadcrumbs = [("Главная", url_for('views.index')), ("Управление метриками", "")]
    return render_with_breadcrumbs('admin_metrics.html', breadcrumbs,
                                   metrics=metrics,
                                   categories=categories,
                                   departments=departments)

@views.route('/admin/cycles')
@login_required
@admin_or_manager_required
def admin_cycles():
    cycles = EvaluationCycle.query.order_by(EvaluationCycle.start_date.desc()).all()
    breadcrumbs = [("Главная", url_for('views.index')), ("Управление циклами", "")]
    return render_with_breadcrumbs('admin_cycles.html', breadcrumbs, cycles=cycles)

@views.route('/admin/metrics/add', methods=['GET', 'POST'])
@login_required
@admin_or_manager_required
def add_metric():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        max_score = float(request.form.get('max_score', 10))
        weight = float(request.form.get('weight', 1.0))
        description = request.form.get('description')
        department_id = request.form.get('department_id')  # Может быть None

        # Менеджер может добавить только в своё подразделение
        if current_user.role.name == 'manager':
            if department_id and int(department_id) != current_user.department_id:
                flash("Вы можете добавлять метрики только в своё подразделение.", "error")
                return redirect(url_for('views.admin_metrics'))

        metric = PerformanceMetric(
            name=name,
            category_id=category_id,
            max_score=max_score,
            weight=weight,
            description=description,
            department_id=department_id if department_id else None
        )
        db.session.add(metric)
        db.session.commit()
        flash("Метрика добавлена.", "success")
        return redirect(url_for('views.admin_metrics'))

    categories = MetricCategory.query.all()
    departments = [current_user.department] if current_user.role.name == 'manager' else Department.query.all()
    return render_template('add_metric.html', categories=categories, departments=departments)