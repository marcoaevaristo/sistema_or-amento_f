from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import traceback

# Configuração de logging detalhado
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

# Configuração do banco de dados
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///orcamento.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Habilitar debug apenas em desenvolvimento
app.debug = os.environ.get('FLASK_ENV') == 'development'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orcamentos = db.relationship('Orcamento', backref='user', lazy=True)

class Orcamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    categoria = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('registro'))
        
        hashed_password = generate_password_hash(password)
        novo_usuario = User(username=username, password=hashed_password)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        orcamentos = Orcamento.query.filter_by(user_id=current_user.id).order_by(Orcamento.data.desc()).all()
        total_receitas = sum(o.valor for o in orcamentos if o.tipo == 'receita')
        total_despesas = sum(o.valor for o in orcamentos if o.tipo == 'despesa')
        saldo = total_receitas - total_despesas
        return render_template('index.html', orcamentos=orcamentos, saldo=saldo, total_receitas=total_receitas, total_despesas=total_despesas)
    return redirect(url_for('login'))

@app.route('/adicionar', methods=['GET', 'POST'])
@login_required
def adicionar():
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo')
            descricao = request.form.get('descricao', '')
            valor_str = request.form.get('valor', '0')
            categoria = request.form.get('categoria')
            tipo = request.form.get('tipo')

            # Validações
            if not titulo:
                flash('O título é obrigatório!', 'danger')
                return render_template('adicionar.html')

            if not categoria:
                flash('A categoria é obrigatória!', 'danger')
                return render_template('adicionar.html')

            if not tipo:
                flash('O tipo é obrigatório!', 'danger')
                return render_template('adicionar.html')

            try:
                valor = float(valor_str.replace(',', '.'))
            except ValueError:
                flash('Valor inválido! Use apenas números.', 'danger')
                return render_template('adicionar.html')

            novo_orcamento = Orcamento(
                titulo=titulo,
                descricao=descricao,
                valor=valor,
                categoria=categoria,
                tipo=tipo,
                user_id=current_user.id
            )
            
            db.session.add(novo_orcamento)
            db.session.commit()
            
            flash('Orçamento adicionado com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao adicionar orçamento: {str(e)}")
            flash('Erro ao salvar o orçamento. Por favor, tente novamente.', 'danger')
            return render_template('adicionar.html')
    
    return render_template('adicionar.html')

@app.route('/criar_master')
def criar_master():
    try:
        # Verifica se já existe algum usuário admin
        if User.query.filter_by(is_admin=True).first():
            logger.info("Tentativa de criar conta master quando já existe uma")
            flash('Já existe uma conta master!', 'danger')
            return redirect(url_for('login'))
        
        # Cria o usuário master
        master_user = User(
            username='master',
            password=generate_password_hash('master2024'),
            is_admin=True
        )
        
        logger.info("Tentando criar usuário master")
        db.session.add(master_user)
        db.session.commit()
        logger.info("Usuário master criado com sucesso")
        
        flash('Conta master criada com sucesso! Username: master, Senha: master2024', 'success')
        return redirect(url_for('login'))
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"Erro ao criar conta master: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        flash('Erro ao criar conta master. Verifique os logs.', 'danger')
        return str(error_msg), 500

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    # Verifica se o orçamento pertence ao usuário atual
    if orcamento.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo')
            descricao = request.form.get('descricao', '')
            valor_str = request.form.get('valor', '0')
            categoria = request.form.get('categoria')
            tipo = request.form.get('tipo')

            # Validações
            if not titulo:
                flash('O título é obrigatório!', 'danger')
                return render_template('editar.html', orcamento=orcamento)

            if not categoria:
                flash('A categoria é obrigatória!', 'danger')
                return render_template('editar.html', orcamento=orcamento)

            if not tipo:
                flash('O tipo é obrigatório!', 'danger')
                return render_template('editar.html', orcamento=orcamento)

            try:
                valor = float(valor_str.replace(',', '.'))
            except ValueError:
                flash('Valor inválido! Use apenas números.', 'danger')
                return render_template('editar.html', orcamento=orcamento)

            orcamento.titulo = titulo
            orcamento.descricao = descricao
            orcamento.valor = valor
            orcamento.categoria = categoria
            orcamento.tipo = tipo
            
            db.session.commit()
            flash('Orçamento atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao atualizar orçamento: {str(e)}")
            flash('Erro ao atualizar o orçamento. Por favor, tente novamente.', 'danger')
            return render_template('editar.html', orcamento=orcamento)
    
    return render_template('editar.html', orcamento=orcamento)

@app.route('/excluir/<int:id>')
@login_required
def excluir(id):
    orcamento = Orcamento.query.get_or_404(id)
    
    # Verifica se o orçamento pertence ao usuário atual
    if orcamento.user_id != current_user.id:
        abort(403)
    
    try:
        db.session.delete(orcamento)
        db.session.commit()
        flash('Orçamento excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir orçamento: {str(e)}")
        flash('Erro ao excluir o orçamento. Por favor, tente novamente.', 'danger')
    
    return redirect(url_for('index'))

# Manipulador de erros para debug
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    error_msg = f"Erro interno do servidor: {str(error)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    return str(error_msg), 500

# Criar tabelas do banco de dados
with app.app_context():
    try:
        logger.info("Tentando criar as tabelas do banco de dados...")
        db.create_all()
        logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True) 