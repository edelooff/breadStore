# coding: utf-8
from sqlalchemy import BINARY, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, SmallInteger, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.base import MEDIUMBLOB
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Abonnement(Base):
    __tablename__ = 'abonnement'

    id = Column(Integer, primary_key=True)
    klant_id = Column(ForeignKey('klant.id'), nullable=False)
    uitgifte_cyclus_id = Column(ForeignKey('uitgifte_cyclus.id'), nullable=False)
    datum_start = Column(Date, nullable=False)
    datum_einde = Column(Date, index=True)
    pakket_aantal = Column(Integer, nullable=False)
    opmerking = Column(String(200), nullable=False)

    klant = relationship('Klant')
    uitgifte_cyclus = relationship('UitgifteCyclus')
    dieets = relationship('Dieet', secondary='abonnement_dieet')


t_abonnement_dieet = Table(
    'abonnement_dieet', metadata,
    Column('abonnement_id', ForeignKey('abonnement.id'), primary_key=True, nullable=False),
    Column('dieet_id', ForeignKey('dieet.id'), primary_key=True, nullable=False)
)


class Contactpersoon(Base):
    __tablename__ = 'contactpersoon'

    id = Column(SmallInteger, primary_key=True)
    klant_id = Column(ForeignKey('klant.id'), nullable=False)
    rol = Column(String(32))
    naam = Column(String(64), nullable=False)
    telefoonnummer = Column(String(10))
    email_adres = Column(String(64))
    adres_straat = Column(String(64))
    adres_postcode = Column(String(6))
    adres_plaats = Column(String(32))

    klant = relationship('Klant')


class Datumwijziging(Base):
    __tablename__ = 'datumwijziging'

    id = Column(Integer, primary_key=True)
    planning = Column(Date, nullable=False, unique=True)
    aanpassing = Column(Date, nullable=False)


class Dieet(Base):
    __tablename__ = 'dieet'

    id = Column(Integer, primary_key=True)
    naam = Column(String(45))
    sticker_kleur = Column(String(16), nullable=False)


class Gezinslid(Base):
    __tablename__ = 'gezinslid'
    __table_args__ = (
        Index('klant', 'klant_id', 'naam'),)

    id = Column(Integer, primary_key=True)
    klant_id = Column(ForeignKey('klant.id'), nullable=False)
    naam = Column(String(90), nullable=False)
    geboorte_datum = Column(Date, nullable=False)
    geslacht = Column(Enum('onbekend', 'man', 'vrouw'), nullable=False)

    klant = relationship('Klant')


class Klant(Base):
    __tablename__ = 'klant'

    id = Column(SmallInteger, primary_key=True)
    klantcode = Column(String(8), nullable=False, unique=True)
    voorletters = Column(String(16))
    tussenvoegsel = Column(String(16))
    achternaam = Column(String(32), nullable=False)
    geslacht = Column(Enum('onbekend', 'man', 'vrouw'), nullable=False)
    geboorte_datum = Column(Date)
    email_adres = Column(String(64))
    adres_straat = Column(String(64), nullable=False)
    adres_postcode = Column(String(6), nullable=False)
    adres_plaats = Column(String(32), nullable=False)


class KlantFoto(Klant):
    __tablename__ = 'klant_foto'

    klant_id = Column(ForeignKey('klant.id'), primary_key=True)
    foto = Column(MEDIUMBLOB, nullable=False)


class KlantStatus(Base):
    __tablename__ = 'klant_status'

    id = Column(Integer, primary_key=True)
    klant_id = Column(ForeignKey('klant.id'), nullable=False)
    status = Column(Enum('nieuw', 'afgewezen', 'doorverwezen', 'klant', 'verhuisd', 'regulier beeindigd', 'weggestuurd'), nullable=False)
    opmerking = Column(Text)
    wijzigingsdatum = Column(Date)
    medewerker_id = Column(ForeignKey('medewerker.id'), nullable=False)
    update_tijd = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    klant = relationship('Klant')
    medewerker = relationship('Medewerker')


class KlantTelefoonnummer(Base):
    __tablename__ = 'klant_telefoonnummer'

    id = Column(Integer, primary_key=True)
    klant_id = Column(ForeignKey('klant.id'), nullable=False)
    soort = Column(Enum('mobiel', 'thuis', 'werk'), nullable=False)
    nummer = Column(String(10), nullable=False)

    klant = relationship('Klant')


class Locatie(Base):
    __tablename__ = 'locatie'

    id = Column(Integer, primary_key=True)
    naam = Column(String(45), nullable=False)


class Medewerker(Base):
    __tablename__ = 'medewerker'

    id = Column(Integer, primary_key=True)
    naam = Column(String(32), nullable=False)
    email_adres = Column(String(64), nullable=False)
    rol_id = Column(ForeignKey('rol.id'), nullable=False)
    actief = Column(Integer, nullable=False, server_default='1')
    login = Column(String(32), nullable=False)
    wachtwoord_hash = Column(BINARY(32), nullable=False)
    wachtwoord_salt = Column(BINARY(8), nullable=False)

    rol = relationship('Rol')


class Pakket(Base):
    __tablename__ = 'pakket'
    __table_args__ = (
        Index('abonnement', 'abonnement_id', 'volgnummer'),)

    id = Column(Integer, primary_key=True)
    abonnement_id = Column(ForeignKey('abonnement.id'), nullable=False)
    volgnummer = Column(Integer, nullable=False)
    pakket_grootte_id = Column(ForeignKey('pakket_grootte.id'), nullable=False)

    abonnement = relationship('Abonnement')
    pakket_grootte = relationship('PakketGrootte')


class PakketGrootte(Base):
    __tablename__ = 'pakket_grootte'

    id = Column(Integer, primary_key=True)
    code = Column(String(1))
    min_gezinsgrootte = Column(Integer, nullable=False)
    omschrijving = Column(String(45))


class PakketStatus(Base):
    __tablename__ = 'pakket_status'

    id = Column(Integer, primary_key=True)
    pakket_id = Column(ForeignKey('pakket.id'), nullable=False)
    ophaaldatum = Column(Date, nullable=False)
    verwerkt = Column(Integer, nullable=False, server_default='0')
    opgehaald = Column(Integer, nullable=False, server_default='0')
    malus = Column(Integer, nullable=False, server_default='0')
    medewerker_id = Column(ForeignKey('medewerker.id'), nullable=False)
    update_tijd = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    medewerker = relationship('Medewerker')
    pakket = relationship('Pakket')


class Permissie(Base):
    __tablename__ = 'permissie'

    id = Column(Integer, primary_key=True)
    permissie = Column(String(32), nullable=False)
    omschrijving = Column(Text, nullable=False)


class Rol(Base):
    __tablename__ = 'rol'

    id = Column(Integer, primary_key=True)
    naam = Column(String(32), nullable=False)
    omschrijving = Column(String(200), nullable=False)


class RolPermissie(Base):
    __tablename__ = 'rol_permissie'

    id = Column(Integer, primary_key=True)
    rol_id = Column(ForeignKey('rol.id'), nullable=False)
    permissie_id = Column(ForeignKey('permissie.id'), nullable=False)

    permissie = relationship('Permissie')
    rol = relationship('Rol')


class Sessie(Base):
    __tablename__ = 'sessie'

    id = Column(Integer, primary_key=True)
    sessie_sleutel = Column(BINARY(32), nullable=False, index=True)
    medewerker_id = Column(ForeignKey('medewerker.id'), nullable=False)
    geldig_tot = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    medewerker = relationship('Medewerker')


class UitgifteCyclus(Base):
    __tablename__ = 'uitgifte_cyclus'
    __table_args__ = (
        Index('uitgifte', 'ophaaldag', 'locatie_id'),)

    id = Column(Integer, primary_key=True)
    omschrijving = Column(String(64), nullable=False)
    ophaaldag = Column(Integer, nullable=False)
    locatie_id = Column(ForeignKey('locatie.id'), nullable=False)
    actief = Column(Integer, nullable=False, server_default='1')
    kleur = Column(String(6), nullable=False)

    locatie = relationship('Locatie')
