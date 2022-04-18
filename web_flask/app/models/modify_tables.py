from unicodedata import name
from app import db

from app.models.create_tables import Photo
from app.models.create_tables import Cache
from app.models.create_tables import Statistics
from app.models.create_tables import MemNode

def add_photo(key, address):
    db_photo = Photo(key=key, address=address)
    db.session.add(db_photo)
    db.session.commit()

def change_photo(photo, address):
    photo.address = address
    db.session.commit()

def search_photo(photo_name):
    photo = Photo.query.filter_by(key = photo_name).first()
    if photo is not None:
        return photo.address
    else:
        return ""

def query_all(key_list):
    list = Photo.query.all()
    for photo in list:
        key_list.append(photo.key)
    return key_list

def config(capacity, policy):
    db_cache = Cache.query.filter_by(name = "local").first()

    if db_cache is not None:
        db_cache.capacity = capacity
        db_cache.policy = policy
    else:
        db_cache = Cache(capacity=capacity, policy=policy)
        db.session.add(db_cache)

    db.session.commit()

def query_stats():
    stats = Statistics.query.order_by(Statistics.time.desc()).limit(120)
    stats_list = [["time", "number", "size", "requests", "hitRate", "missRate"]]
    
    for data in stats:
        stats_list.append([data.time, data.number, data.size, data.requests, data.hitRate, data.missRate])

    return stats_list

def add_ins(id, ip):
    db_ins = MemNode(ins_id=id, ins_ip=ip)
    db.session.add(db_ins)
    db.session.commit()

def remove_ins(id, ip):
    db_ins = MemNode.query.filter_by(ins_id = id).delete()
    db.session.commit()