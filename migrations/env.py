from __future__ import with_statement

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Este é o objeto Config do Alembic, que fornece
# acesso aos valores dentro do arquivo .ini em uso.
config = context.config

# Interpreta o arquivo de configuração para logging do Python.
# Esta linha configura os loggers basicamente.
fileConfig(config.config_file_name)

# adicione o objeto MetaData do seu modelo aqui
# para suporte ao 'autogenerate'
from models import Usuario, Psicologo, Paciente, Agendamento, ProntuarioMedico
from extensions import db
target_metadata = db.metadata

# outros valores da configuração, definidos pelas necessidades do env.py,
# podem ser obtidos:
# minha_opcao_importante = config.get_main_option("minha_opcao_importante")
# ... etc.


def run_migrations_offline():
    """Executa migrações no modo 'offline'.

    Isso configura o contexto apenas com uma URL
    e não um Engine, embora um Engine seja aceitável
    aqui também. Ao pular a criação do Engine
    nem precisamos de uma DBAPI disponível.

    Chamadas para context.execute() aqui emitem a string fornecida para a
    saída do script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrações no modo 'online'.

    Neste cenário precisamos criar um Engine
    e associar uma conexão com o contexto.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()