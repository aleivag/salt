
import sys
from pprint import pformat
import logging
from urlparse import urlparse
from datetime import datetime

from salt.utils.parsers import MasterOptionParser

from sqlalchemy import create_engine
from sqlalchemy import Column, Unicode, UnicodeText, Enum, DateTime

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SaltDBBase = declarative_base()

#Database Tables

log = logging.getLogger(__name__)


class Minions(SaltDBBase):
    __tablename__ = 'minions'

    minion = Column(Unicode(45), primary_key=True)
    minion_name = Column(Unicode(125))

    key = Column(UnicodeText, nullable=False)
    status = Column(Enum("acepted", "pre", "rejected"), nullable=False, default="pre", server_default="pre")

    created_on = Column(DateTime, nullable=False, default=datetime.now)
    modified_on = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


#This is just the DB Backend main class


class _SaltDB(MasterOptionParser):

    def __call__(self):
        return self

    def __init__(self):
        MasterOptionParser.__init__(self)
        self.parse_args()

        self.engine = None
        self.session = None

        engine_p = urlparse(self.config.get('pki_backend', ''))

        if engine_p.scheme != 'file':
            self.engine = create_engine(self.config['pki_backend'], echo=True)
            self.session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=self.engine))

    def create_database(self):
        SaltDBBase.metadata.create_all(self.engine)

    @property
    def Session(self):
        return self.session

SaltDB = _SaltDB()