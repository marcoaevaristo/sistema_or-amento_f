# Sistema de Orçamento

Um sistema de orçamento pessoal dinâmico e fácil de usar, desenvolvido com Python e Flask.

## Funcionalidades

- Cadastro de receitas e despesas
- Categorização de lançamentos
- Dashboard com visão geral das finanças
- Relatórios de saldo, receitas e despesas
- Interface responsiva e moderna

## Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- PostgreSQL (para produção)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd sistema_orcamento
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
# Linux/Mac
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=sua_chave_secreta

# Windows
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=sua_chave_secreta
```

5. Inicialize o banco de dados:
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Executando localmente

```bash
flask run
```

O sistema estará disponível em `http://localhost:5000`

## Deploy no Heroku

1. Crie uma conta no Heroku e instale o Heroku CLI

2. Faça login no Heroku:
```bash
heroku login
```

3. Crie um novo app:
```bash
heroku create nome-do-seu-app
```

4. Adicione o banco de dados PostgreSQL:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

5. Configure as variáveis de ambiente:
```bash
heroku config:set SECRET_KEY=sua_chave_secreta
```

6. Faça o deploy:
```bash
git push heroku main
```

7. Inicialize o banco de dados:
```bash
heroku run python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Contribuindo

Sinta-se à vontade para contribuir com o projeto através de pull requests.

## Licença

Este projeto está licenciado sob a licença MIT. 