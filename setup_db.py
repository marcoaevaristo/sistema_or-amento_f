from app import db, app
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_database():
    with app.app_context():
        try:
            # Remover todas as tabelas existentes
            logger.info("Tentando remover tabelas existentes...")
            db.drop_all()
            logger.info("Tabelas removidas com sucesso!")

            # Criar todas as tabelas novamente
            logger.info("Tentando criar novas tabelas...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")

            # Verificar se as tabelas foram criadas
            tables = db.engine.table_names()
            logger.info(f"Tabelas criadas: {tables}")

            return True
        except Exception as e:
            logger.error(f"Erro durante a configuração do banco de dados: {str(e)}")
            return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("Banco de dados configurado com sucesso!")
    else:
        print("Erro ao configurar o banco de dados. Verifique os logs.") 