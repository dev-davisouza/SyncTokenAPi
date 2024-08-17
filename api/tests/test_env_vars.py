from django.test import TestCase
from synctokenapi.settings import BASE_DIR
import os
import dj_database_url


class dbProdcutionAPITest(TestCase):
    def test_env_var_IS_DEV_DATABASE_is_correct(self):
        inference = os.environ.get("IS_DEV_DATABASE")
        self.assertEqual(inference, '1')

    def test_env_var_DATABASE_URL_is_correct(self):
        db_url = os.environ.get('DATABASE_URL')
        db_connection = dj_database_url.config(default=os.environ.get(db_url))
        expected_connection_attrs = ["NAME", "USER", "PASSWORD",
                                     "HOST", "PORT", "CONN_MAX_AGE",
                                     "CONN_HEALTH_CHECKS",
                                     "DISABLE_SERVER_SIDE_CURSORS",
                                     "ENGINE"]
        for attr in expected_connection_attrs:
            self.assertIn(attr, db_connection)

    def test_env_var_DEBUG_is_correct(self):
        debug = os.environ.get('DEBUG')
        if debug:
            if debug == "1":
                debug = True
            if debug == "0":
                debug = False

        self.assertTrue(type(debug), "bool")

        """
         OBS: Aqui abaixo eu propositalmente tento levantar um erro, mas por
         padrão o os.environ.get() não levanta excessão, apenas retorna um
         None.

         Portanto seu uso é seguro caso uma variável de ambiente não seja
         encontrada, mas já tenha um valor padrão substituto. Entretanto,
         caso não tenha um valor padrão, uma excessão pode ser mais
         aplicável considerando alguns contextos como conexão à base de dados
         que não pode simplesmente retornar um None.
        """
        if not debug:
            raise AssertionError(
                "A variável de ambiente 'DEBUG' não está definida.")

    def test_connection_to_db_is_ok(self):
        """
         Neste caso eu estou testando exclusivamente supondo que vou manter
         a base de dados de desenvolvimento neste ambiente. Logicamente, os
         testes mudam caso o ambiente seja de Produção.

         Mas nas settings.py eu tento induzir o meu sistema a ter o padrão de
         configuração do ambiente de desenvolvimento.
        """
        DATABASES = {}
        if os.environ.get('IS_DEV_DATABASE') == '1':
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / "db.sqlite3",
                }
            }

        else:
            DATABASES = {
                'default':
                    dj_database_url.config(
                        default=os.environ.get('DATABASE_URL'))
            }

        # Supondo que aqui estou usando Sqlite como padrão da env.
        self.assertIn('django.db.backends.sqlite3', str(DATABASES))
