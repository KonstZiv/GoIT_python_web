from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, MetaData
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata_obj = MetaData()


class Abonents(Base):
    __tablename__ = "abonents",
    id_abonent = Column(Integer, primary_key=True)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    birthday = Column(Date)
    address = Column(String)
    phones = relationship("Phones", backref=backref("abonents"))
    emails = relationship("Emails", backref=backref("abonents"))
    notes = relationship("Notes", backref=backref("abonents"))


class Phones(Base):
    __tablename__ = "phones",
    id_phone = Column(Integer, ForeignKey("abonents.id_abonent")),
    phone_number = Column(Integer)


class Notes(Base):
    __tablename__ = "notes",
    id_note = Column(Integer, ForeignKey("abonents.id_abonent")),
    note = Column(String),
    date = Column(Date)


class Emails(Base):
    __tablename__ = "emails",
    id_email = Column(Integer, ForeignKey("abonents.id_abonent")),
    email = Column(String),
