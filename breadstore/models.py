"""breadStore model definitions."""

# Standard modyles
import datetime
import hashlib
import pytz
import re

# Third-party modules
import bcrypt
import sqlalchemy
from sqlalchemy import (
    Boolean, Date, Enum, Integer, SmallInteger, String, Text, Unicode)
from sqlalchemy.dialects import mysql as types
from sqlalchemy.ext import declarative
from sqlalchemy import orm

# Application modules
from . import util

# ##############################################################################
# Declarative base for SQLAlchemy and ORM to JSON conversion
#
def declarative_base(cls):
  """Decorator for SQLAlchemy's declarative base."""
  return declarative.declarative_base(cls=cls)


@declarative_base
class Base(object):
  """Extended SQLAlchemy declarative base class."""
  @declarative.declared_attr
  def __tablename__(cls):
    underscorer = lambda match: '_{}'.format(match.group(0).lower())
    return re.sub(r'[A-Z]', underscorer, cls.__name__).strip('_')

  def __json__(self, request=None):
    """Converts all the properties of the object into a dict for use in JSON.

    You can define the following in your class

    _base_blacklist :
        top level blacklist list of which properties not to include in JSON.

    _json_blacklist :
        blacklist list of which properties not to include in JSON.

    _json_eager_load :
        list of relations which need to be eagerly loaded. This applies to
        one-to-one and one-to-many relationships defined in SQLAlchemy classes.
    """
    prefixes_to_ignore = '__', '_sa_'
    json_result = {}

    # Set up the blacklist from its various sources
    blacklist = set(getattr(self, '_base_blacklist', []))
    blacklist.update(getattr(self, '_json_blacklist', []))

    # Request all attributes marked for eager loading
    json_eager_load = set(getattr(self, '_json_eager_load', []))
    for attr in json_eager_load:
      getattr(self, attr, None)

    # Make a copy of keys and add properties to include in the output
    for key in set(vars(self)) | json_eager_load:
      # skip blacklisted, private and SQLAlchemy properties
      if key in blacklist or key.startswith(prefixes_to_ignore):
        continue
      attr = getattr(self, key)

      if isinstance(attr, datetime.date):
        attr = attr.isoformat()
      elif isinstance(attr, (datetime.datetime, datetime.time)):
        attr = pytz.utc.localize(attr).isoformat()
      else:
        if isinstance(attr, Base):
          # Non-list relationship, recursively convert to JSON
          attr = attr.__json__(request)
        elif isinstance(attr, orm.collections.InstrumentedList):
          # List of related objects, iterate and convert all to JSON
          attr = [x.__json__(request) for x in attr]
        else:
          # convert all non float or integer objects to string or if string
          # conversion is not possible, convert it to Unicode
          if attr and not isinstance(attr, (int, float)):
            try:
              attr = str(attr)
            except UnicodeEncodeError:
              attr = unicode(attr)  # .encode('utf-8')
      # Change naming convention on the key to match JSON norms and store attr
      json_result[util.case_transform_json(key)] = attr
    return json_result


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
  # Column definitions
  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  uitgifte_cyclus_id = Column(StrictForeignKey('uitgifte_cyclus.id'))
  datum_start = Column(Date)
  datum_einde = Column(Date, nullable=True, index=True)
  pakket_aantal = Column(SmallInteger)
  opmerking = Column(Unicode(200))

  # Relationships
  klant = orm.relationship('Klant')
  uitgifte_cyclus = orm.relationship('UitgifteCyclus')
  dieets = orm.relationship(
      'Dieet', secondary='abonnement_dieet')
  pakketten = orm.relationship(
      'Pakket', innerjoin=True, passive_deletes=True)

  # JSON blacklist
  _base_blacklist = 'klant',

  @property
  def completed(self):
    """Returns whether or not the subscription has been completed.

    A subscription is considered complete when the provided package count is
    equal to the package count planned for it.
    """
    return self.pakket_aantal == len(self.packages_provided())

  def packages_provided(self):
    """Returnst a list of packages that have been handed out to customers.

    This excludes any packages that remain in planning phase.
    """
    return [package for package in self.pakketten if package.completed]


t_abonnement_dieet = sqlalchemy.Table(
    'abonnement_dieet',
    Base.metadata,
    Column('abonnement_id', ForeignKey('abonnement.id'), primary_key=True),
    Column('dieet_id', ForeignKey('dieet.id'), primary_key=True))


class Contactpersoon(Base):
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
  id = Column(SmallInteger, primary_key=True)
  planning = Column(Date, unique=True)
  aanpassing = Column(Date)


class Dieet(Base):
  id = Column(SmallInteger, primary_key=True)
  naam = Column(Unicode(45))
  sticker_kleur = Column(String(16))


class Gezinslid(Base):
  __table_args__ = sqlalchemy.Index('klant', 'klant_id', 'naam', unique=True),

  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  naam = Column(Unicode(90))
  geboorte_datum = Column(Date)
  geslacht = Column(Enum('onbekend', 'man', 'vrouw'))

  klant = orm.relationship('Klant')


class Klant(Base):
  # Column definitions
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

  # Relationships
  abonnementen = orm.relationship(
      'Abonnement', passive_deletes=True)
  contactpersonen = orm.relationship(
      'Contactpersoon', passive_deletes=True)
  gezin = orm.relationship(
      'Gezinslid', passive_deletes=True)

  def add_subscription(self, **attrs):
    """Adds a subscription to the customer."""
    attrs['klant'] = self
    self.abonnementen.append(Abonnement(**attrs))
    return self.abonnementen[-1]

  def package_size(self):
    """Returns the appropriate package size for the current family size."""
    session = sqlalchemy.inspect(self).session
    family_size = len(self.gezin) + 1  # Family members + self
    required_size = PakketGrootte.min_gezinsgrootte
    return session.query(PakketGrootte).\
        filter(family_size >= required_size).\
        order_by(required_size.desc()).first()


class KlantFoto(Klant):
  klant_id = Column(ForeignKey('klant.id'), primary_key=True)
  foto = Column(types.MEDIUMBLOB)


class KlantStatus(Base):
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
  id = Column(Integer, primary_key=True)
  klant_id = Column(ForeignKey('klant.id'))
  soort = Column(Enum('mobiel', 'thuis', 'werk'))
  nummer = Column(String(10))

  klant = orm.relationship('Klant')


class Locatie(Base):
  id = Column(SmallInteger, primary_key=True)
  naam = Column(Unicode(45))


class Medewerker(Base):
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
  __table_args__ = sqlalchemy.Index(
      'abonnement', 'abonnement_id', 'volgnummer', unique=True),

  id = Column(Integer, primary_key=True)
  abonnement_id = Column(ForeignKey('abonnement.id'))
  volgnummer = Column(Integer)
  pakket_grootte_id = Column(StrictForeignKey('pakket_grootte.id'))

  abonnement = orm.relationship('Abonnement')
  pakket_grootte = orm.relationship('PakketGrootte')
  statussen = orm.relationship(
      'PakketStatus', innerjoin=True, lazy='joined', passive_deletes=True)

  @property
  def completed(self):
    """Returns whether or not a package has been completed.

    A package is completed when it is past its planned pickup date, and has not
    been rescheduled. In this case, the most recent status should have
    `verwerkt == True`.
    """
    return any(status.verwerkt for status in self.statussen)


class PakketGrootte(Base):
  id = Column(SmallInteger, primary_key=True)
  code = Column(types.CHAR(1))
  min_gezinsgrootte = Column(SmallInteger)
  omschrijving = Column(Unicode(45), server_default='')


class PakketStatus(Base):
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
  id = Column(SmallInteger, primary_key=True)
  naam = Column(String(32))
  omschrijving = Column(Text)


class Rol(Base):
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
  __table_args__ = sqlalchemy.Index(
      'uitgifte', 'ophaaldag', 'locatie_id', unique=True),

  id = Column(SmallInteger, primary_key=True)
  omschrijving = Column(Unicode(64))
  ophaaldag = Column(Integer)
  locatie_id = Column(ForeignKey('locatie.id'))
  actief = Column(Boolean, server_default='1')
  kleur = Column(types.CHAR(6))

  locatie = orm.relationship('Locatie')
