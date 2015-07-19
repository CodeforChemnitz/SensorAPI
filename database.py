# copy of the SQLAlchemy tutorial
# http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

engine = create_engine('sqlite:////tmp/sensor-data.db', echo=False, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

    for name in ['temperature', 'pressure']:
        try:
            db_session.query(models.SensorType).filter(models.SensorType.name == name).one()
        except NoResultFound:
            type = models.SensorType(name=name)
            db_session.add(type)

    db_session.commit()
