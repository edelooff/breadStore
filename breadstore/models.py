"""breadStore model definitions."""

# Standard modyles
import hashlib

# Third-party modules
import bcrypt
import sqlalchemy
from sqlalchemy import (
    Boolean, Date, Enum, Integer, SmallInteger, String, Text, Unicode)
from sqlalchemy.dialects import mysql as types
from sqlalchemy.ext import declarative
from sqlalchemy import orm


Base = declarative.declarative_base()
metadata = Base.metadata


# ##############################################################################
# Utility functions to simplify model declaration
#
def Column(sql_type, *args, **kwds):
  kwds.setdefault('nullable', False)
  return sqlalchemy.Column(sql_type, *args, **kwds)


def ForeignKey(field, **kwds):
  kwds.setdefault('onupdate', 'CASCADE')
  kwds.setdefault('ondelete', 'CASCADE')
  return sqlalchemy.ForeignKey(field, **kwds)


def StrictForeignKey(field, **kwds):
  kwds.setdefault('ondelete', 'RESTRICT')
  return ForeignKey(field, **kwds)


# ##############################################################################
# The actual breadStore model definition
#
class Abonnement(Base):
  __tablename__ = 'abonnement'

  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  uitgifte_cyclus_id = Column(StrictForeignKey('uitgifte_cyclus.id'))
  datum_start = Column(Date)
  datum_einde = Column(Date, nullable=True, index=True)
  pakket_aantal = Column(SmallInteger)
  opmerking = Column(Unicode(200))

  klant = orm.relationship('Klant')
  uitgifte_cyclus = orm.relationship('UitgifteCyclus')
  dieets = orm.relationship('Dieet', secondary='abonnement_dieet')


t_abonnement_dieet = sqlalchemy.Table(
    'abonnement_dieet',
    Base.metadata,
    Column('abonnement_id', ForeignKey('abonnement.id'), primary_key=True),
    Column('dieet_id', ForeignKey('dieet.id'), primary_key=True))


class Contactpersoon(Base):
  __tablename__ = 'contactpersoon'

  id = Column(SmallInteger, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  rol = Column(Unicode(32), server_default='')
  naam = Column(Unicode(64))
  telefoonnummer = Column(String(10), nullable=True)
  email_adres = Column(String(64), nullable=True)
  adres_straat = Column(Unicode(64), nullable=True)
  adres_postcode = Column(String(6), nullable=True)
  adres_plaats = Column(Unicode(32), nullable=True)

  klant = orm.relationship('Klant')


class Datumwijziging(Base):
  __tablename__ = 'datumwijziging'

  id = Column(SmallInteger, primary_key=True)
  planning = Column(Date, unique=True)
  aanpassing = Column(Date)


class Dieet(Base):
  __tablename__ = 'dieet'

  id = Column(SmallInteger, primary_key=True)
  naam = Column(Unicode(45))
  sticker_kleur = Column(String(16))


class Gezinslid(Base):
  __tablename__ = 'gezinslid'
  __table_args__ = sqlalchemy.Index('klant', 'klant_id', 'naam', unique=True),

  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  naam = Column(Unicode(90))
  geboorte_datum = Column(Date)
  geslacht = Column(Enum('onbekend', 'man', 'vrouw'))

  klant = orm.relationship('Klant')


class Klant(Base):
  __tablename__ = 'klant'

  id = Column(Integer, primary_key=True)
  klantcode = Column(types.CHAR(8), unique=True)
  voorletters = Column(Unicode(16), server_default='')
  tussenvoegsel = Column(Unicode(16), server_default='')
  achternaam = Column(Unicode(32))
  geslacht = Column(Enum('onbekend', 'man', 'vrouw'))
  geboorte_datum = Column(Date, nullable=True)
  email_adres = Column(String(64), nullable=True)
  adres_straat = Column(Unicode(64))
  adres_postcode = Column(types.CHAR(6))
  adres_plaats = Column(Unicode(32))


class KlantFoto(Klant):
  __tablename__ = 'klant_foto'

  klant_id = Column(ForeignKey('klant.id'), primary_key=True)
  foto = Column(types.MEDIUMBLOB)


class KlantStatus(Base):
  __tablename__ = 'klant_status'

  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  status = Column(Enum(
      'nieuw', 'afgewezen', 'doorverwezen', 'klant',
      'verhuisd', 'regulier beeindigd', 'weggestuurd'))
  opmerking = Column(Text, server_default='')
  wijzigingsdatum = Column(Date, nullable=True)
  medewerker_id = Column(ForeignKey('medewerker.id'))
  update_tijd = Column(types.TIMESTAMP, server_default=sqlalchemy.text(
      'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

  klant = orm.relationship('Klant')
  medewerker = orm.relationship('Medewerker')


class KlantTelefoonnummer(Base):
  __tablename__ = 'klant_telefoonnummer'

  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  soort = Column(Enum('mobiel', 'thuis', 'werk'))
  nummer = Column(String(10))

  klant = orm.relationship('Klant')


class Locatie(Base):
  __tablename__ = 'locatie'

  id = Column(SmallInteger, primary_key=True)
  naam = Column(Unicode(45))


class Medewerker(Base):
  __tablename__ = 'medewerker'

  id = Column(SmallInteger, primary_key=True)
  naam = Column(Unicode(32))
  email_adres = Column(String(64))
  rol_id = Column(StrictForeignKey('rol.id'))
  actief = Column(Boolean, server_default='1')
  login = Column(String(32))
  wachtwoord = Column(String(80))

  rol = orm.relationship('Rol')

  def set_password(self, password, work_factor=10):
    """(Re)sets the password for the user."""
    salt = bcrypt.gensalt(work_factor)
    self.wachtwoord = bcrypt.hashpw(password.encode('utf8'), salt)

  def verify_password(self, password):
    """Checks the provided password against the stored hash."""
    password = password.encode('utf8')
    if self.wachtwoord.startswith('$2a$'):
      pw_hash = bcrypt.hashpw(password, self.wachtwoord)
      return pw_hash == self.wachtwoord
    salt = self.wachtwoord[:16].decode('hex')
    result = ''
    for _step in range(100):
      result = hashlib.sha256(salt + result + password).digest()
    if result == self.wachtwoord[16:].decode('hex'):
      self.set_password(password)
      return True


class Pakket(Base):
  __tablename__ = 'pakket'
  __table_args__ = sqlalchemy.Index(
      'abonnement', 'abonnement_id', 'volgnummer', unique=True),

  id = Column(Integer, primary_key=True)
  abonnement_id = Column(ForeignKey('abonnement.id'))
  volgnummer = Column(Integer)
  pakket_grootte_id = Column(StrictForeignKey('pakket_grootte.id'))

  abonnement = orm.relationship('Abonnement')
  pakket_grootte = orm.relationship('PakketGrootte')


class PakketGrootte(Base):
  __tablename__ = 'pakket_grootte'

  id = Column(SmallInteger, primary_key=True)
  code = Column(types.CHAR(1))
  min_gezinsgrootte = Column(SmallInteger)
  omschrijving = Column(Unicode(45), server_default='')


class PakketStatus(Base):
  __tablename__ = 'pakket_status'

  id = Column(Integer, primary_key=True)
  pakket_id = Column(ForeignKey('pakket.id'))
  ophaaldatum = Column(Date)
  verwerkt = Column(Boolean, server_default='0')
  opgehaald = Column(Boolean, server_default='0')
  malus = Column(Boolean, server_default='0')
  medewerker_id = Column(ForeignKey('medewerker.id'))
  update_tijd = Column(
      types.TIMESTAMP, server_default=sqlalchemy.text('CURRENT_TIMESTAMP'))

  medewerker = orm.relationship('Medewerker')
  pakket = orm.relationship('Pakket')


class Permissie(Base):
  __tablename__ = 'permissie'

  id = Column(SmallInteger, primary_key=True)
  naam = Column(String(32))
  omschrijving = Column(Text)


class Rol(Base):
  __tablename__ = 'rol'

  id = Column(SmallInteger, primary_key=True)
  naam = Column(String(32))
  omschrijving = Column(Unicode(200))

  permissies = orm.relationship('Permissie', secondary='rol_permissie')


t_rol_permissie = sqlalchemy.Table(
    'rol_permissie',
    Base.metadata,
    Column('rol_id', ForeignKey('rol.id'), primary_key=True),
    Column('permissie_id', ForeignKey('permissie.id'), primary_key=True))


class UitgifteCyclus(Base):
  __tablename__ = 'uitgifte_cyclus'
  __table_args__ = sqlalchemy.Index(
      'uitgifte', 'ophaaldag', 'locatie_id', unique=True),

  id = Column(SmallInteger, primary_key=True)
  omschrijving = Column(Unicode(64))
  ophaaldag = Column(Integer)
  locatie_id = Column(ForeignKey('locatie.id'))
  actief = Column(Boolean, server_default='1')
  kleur = Column(types.CHAR(6))

  locatie = orm.relationship('Locatie')
