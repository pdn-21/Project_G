from sqlalchemy import Column, String, Date, DECIMAL, Time, TIMESTAMP, Text
from .database import Base

class VisitList(Base):
    __tablename__ = "visit_list"
    
    vn = Column(String(15), primary_key=True)
    vstdate = Column(Date)
    hn = Column(String(15))
    name = Column(String(255))
    cid = Column(String(13))
    pttype = Column(String(10)) # เพิ่มตามโจทย์
    pttypename = Column(String(255))
    department = Column(String(255))
    auth_code = Column(String(50))
    close_visit = Column(String(1))
    close_seq = Column(String(50))
    close_staff = Column(String(255))
    income = Column(DECIMAL(10, 2))
    uc_money = Column(DECIMAL(10, 2))
    paid_money = Column(DECIMAL(10, 2))
    arrearage = Column(DECIMAL(10, 2))
    outdepcode = Column(String(255))
    vsttime = Column(Time)
    ovstost = Column(String(50))
    endpoint = Column(String(50))
    date = Column(String(8))