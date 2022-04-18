from unicodedata import name
from app import db

from app.models.create_tables import AutoScalingConfig
from app.models.create_tables import Cache
from app.models.create_tables import Photo
from app.models.create_tables import MemNode

def config_cache(capacity, policy):
    db_cache = Cache.query.filter_by(name = "local").first()

    if db_cache is not None:
        db_cache.capacity = capacity
        db_cache.policy = policy
    else:
        db_cache = Cache(capacity=capacity, policy=policy)
        db.session.add(db_cache)

    db.session.commit()

def clear_photo():
    db.session.query(Photo).delete()
    db.session.commit()

def config_scaler(maxThresh, minThresh, exRatio, shRatio):
    db_cache = AutoScalingConfig.query.filter_by(name = "local").first()

    if db_cache is not None:
        db_cache.mode = "auto"
        db_cache.thresh_grow = maxThresh
        db_cache.thresh_shrink = minThresh
        db_cache.ratio_expand = exRatio
        db_cache.ratio_shrink = shRatio
    else:
        db_cache = AutoScalingConfig(mode="auto", thresh_grow=maxThresh, thresh_shrink=minThresh, ratio_expand=exRatio, ratio_shrink=shRatio)
        db.session.add(db_cache)

    db.session.commit()

def switch_mode():
    db_cache = AutoScalingConfig.query.filter_by(name = "local").first()

    if db_cache is not None:
        db_cache.mode = "manual"
        
    db.session.commit()

def get_ip():
    ip_list = []
    db_ins = MemNode.query.all()
    for ins in db_ins:
        ip_list.append(ins.ins_ip)
    return ip_list