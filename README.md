# Clínica Mentalize - Backend

## Descrição

Este é o backend da aplicação Clínica Mentalize. O sistema permite o gerenciamento de usuários (psicólogos e pacientes), agendamentos de consultas e prontuários médicos.

## Funcionalidades

- Autenticação e autorização de usuários
- Gerenciamento de usuários (psicólogos e pacientes)
- Agendamento de consultas
- Gerenciamento de prontuários médicos
- Análise de dados e estatísticas

## Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate
- Outras dependências listadas em requirements.txt

## Instalação

1. Clone o repositório:
   ```
   git clone [https://github.com/natachasiqueira/backend_projetointegrador2]
   cd backend_projetointegrador2
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   DATABASE_URL=sqlite:///app.db
   JWT_SECRET_KEY=seu-segredo-aqui
   ```

## Inicialização do Banco de Dados

1. Execute as migrações do banco de dados:
   ```
   flask db upgrade
   ```

2. (Opcional) Popule o banco de dados com dados de exemplo:
   ```
   python init_db.py
   ```

## Executando o Servidor

1. Inicie o servidor Flask:
   ```
   flask run
   ```

2. O servidor estará disponível em `http://localhost:5000`

## Estrutura do Projeto

```
backend/
├── app.py                  # Ponto de entrada da aplicação
├── config.py               # Configurações da aplicação
├── extensions.py           # Extensões do Flask
├── init_db.py              # Script para inicializar o banco de dados
├── models/                 # Modelos de dados
│   ├── __init__.py
│   ├── usuario.py
│   ├── psicologo.py
│   ├── paciente.py
│   ├── agendamento.py
│   └── prontuario_medico.py
├── routes/                 # Rotas da API
│   ├── __init__.py
│   ├── autenticacao.py
│   ├── usuarios.py
│   ├── agendamentos.py
│   ├── prontuarios_medicos.py
│   └── analises.py
├── migrations/             # Migrações do banco de dados
├── tests/                  # Testes unitários
│   ├── __init__.py
│   ├── test_autenticacao.py
│   ├── test_agendamentos.py
│   └── test_prontuarios_medicos.py
└── swagger.py              # Configuração do Swagger/OpenAPI
```

## Endpoints da API

### Autenticação

- `POST /login` - Autenticar usuário
- `POST /registro` - Registrar novo usuário
- `GET /perfil` - Obter perfil do usuário autenticado

### Usuários

- `GET /usuarios` - Listar todos os usuários (somente psicólogos)
- `GET /usuarios/<id>` - Obter detalhes de um usuário específico
- `PUT /usuarios/<id>` - Atualizar informações de um usuário
- `DELETE /usuarios/<id>` - Excluir um usuário
- `GET /psicologos` - Listar todos os psicólogos
- `GET /pacientes` - Listar todos os pacientes (somente psicólogos)

### Agendamentos

- `GET /agendamentos` - Listar agendamentos do usuário autenticado
- `GET /agendamentos/<id>` - Obter detalhes de um agendamento específico
- `POST /agendamentos` - Criar novo agendamento (somente psicólogos)
- `PUT /agendamentos/<id>` - Atualizar um agendamento
- `DELETE /agendamentos/<id>` - Excluir um agendamento (somente psicólogos)

### Prontuários Médicos

- `GET /prontuarios` - Listar prontuários do usuário autenticado
- `GET /prontuarios/<id>` - Obter detalhes de um prontuário específico
- `POST /prontuarios` - Criar novo prontuário (somente psicólogos)
- `PUT /prontuarios/<id>` - Atualizar um prontuário (somente psicólogos)
- `DELETE /prontuarios/<id>` - Excluir um prontuário (somente psicólogos)

### Análises

- `GET /analises/agendamentos` - Obter estatísticas de agendamentos (somente psicólogos)
- `GET /analises/prontuarios` - Obter estatísticas de prontuários (somente psicólogos)
- `GET /analises/pacientes` - Obter estatísticas de pacientes (somente psicólogos)

## Documentação da API

A documentação completa da API está disponível através do Swagger UI em:

```
http://localhost:5000/swagger
```

## Testes

Para executar os testes unitários:

```
pytest
```
