
import os
from sqlalchemy import create_engine

basedir = os.path.abspath(os.path.dirname(__file__))
CONNECTION_STRING_SQLITE = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

engine = create_engine(CONNECTION_STRING_SQLITE, echo=True, future=True)
