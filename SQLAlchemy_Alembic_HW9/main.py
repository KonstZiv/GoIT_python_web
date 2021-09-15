#from models import Abonents, Phones, Emails, Notes
from settings import engine
from sqlalchemy import text
from sqlalchemy.orm import Session


stmt = text(
    "SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=10)
with Session(engine) as session:
    result = session.execute(stmt)
    for x, y in result:
        print(f"x: {x}   y : {y}")
