from unicodedata import name
from app import db

from sqlalchemy import Column
from sqlalchemy import Integer, String, Text, Float


class Photo(db.Model):
    __tablename__ = 'Photo'
    key = Column(String(100), primary_key=True, index=True) # build index for photo name, speed up querying
    address = Column(Text)

    def __repr__(self):
        return "<Photo %r>" % self.key


class Cache(db.Model):
    __tablename__ = 'Cache'
    name = Column(String(10), default="local", primary_key=True)
    capacity = Column(Integer, default=30)
    policy = Column(String(10), default="lru")
    
    def __repr__(self):
        return "<Cache %r>" % self.capacity

class Statistics(db.Model):
    __tablename__ = 'Statistics'
    time = Column(String(100), primary_key=True)
    number = Column(Integer)
    size = Column(String(20))
    requests = Column(Integer)
    hitRate = Column(Float)
    missRate = Column(Float)

    def __repr__(self):
        return "<Statistics %r>" % self.time

class AutoScalingConfig(db.Model):
    __tablename__ = 'AutoScaling'
    name = Column(String(10), default="local", primary_key=True)
    mode = Column(String(10), default="manual")
    thresh_grow = Column(Integer)
    thresh_shrink = Column(Integer)
    ratio_expand = Column(Float)
    ratio_shrink = Column(Float)

    def __repr__(self): # how to print User
        return "<AutoScalingConfig %r>" % self.name

class MemNode(db.Model):
    __tablename__ = 'MemNode'
    ins_id = Column(String(100), primary_key=True)
    ins_ip = Column(String(100))

    def __repr__(self): # how to print User
        return "<MemNode %r>" % self.ins_id
