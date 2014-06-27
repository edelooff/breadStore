"""Quick script to drop and recreate the schema for verification."""

# Third-party modules
import sqlalchemy

# Application modules
import model


SQLA_URL = 'mysql://breadstore:%s@localhost/breadstore_schema'


def main():
  password = raw_input('Password for breadstore@localhost? ')
  engine = sqlalchemy.create_engine(SQLA_URL % password, echo=True)
  model.Base.metadata.bind = engine
  model.Base.metadata.drop_all()
  model.Base.metadata.create_all()


if __name__ == '__main__':
  main()
