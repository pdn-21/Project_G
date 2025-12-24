from ..database import get_source_connection, get_local_session
from ..models import VisitList
from sqlalchemy import text
from datetime import datetime

def sync_data_from_hosxp(date_from: str, date_to: str):
    source_conn = get_source_connection()
    local_db = get_local_session()

    try:
        with source_conn.cursor() as cursor:
            # [cite_start]SQL แปลงจาก 1.txt [cite: 2, 3, 4]
            # ใช้ Raw SQL เพราะ HOSxP มี structure ซับซ้อน
            sql = f"""
                SELECT 
                    (SELECT IF(vn IS NOT NULL, 'Y', 'N') FROM nhso_confirm_privilege WHERE vn = v.vn LIMIT 1) AS close_visit,
                    v.vn, v.vstdate, v.hn, CONCAT(pt.pname, pt.fname, '  ', pt.lname) AS name, pt.cid,
                    v.income, p.name AS pttypename, v.pttype, k.department, vp.auth_code,
                    (SELECT nhso_seq FROM nhso_confirm_privilege WHERE vn = v.vn LIMIT 1) AS close_seq,
                    (SELECT d.name FROM nhso_confirm_privilege x LEFT JOIN doctor d ON d.code = x.confirm_staff WHERE x.vn = v.vn LIMIT 1) AS close_staff,
                    o.vsttime, o.ovstost
                FROM vn_stat v
                LEFT JOIN patient pt ON pt.cid = v.cid
                LEFT JOIN ovst o ON o.vn = v.vn
                LEFT JOIN pttype p ON p.pttype = v.pttype
                LEFT JOIN kskdepartment k ON k.depcode = o.main_dep
                LEFT JOIN visit_pttype vp ON vp.vn = v.vn
                WHERE v.vstdate BETWEEN '{date_from}' AND '{date_to}'
                ORDER BY v.vn ASC
            """
            cursor.execute(sql)
            # [cite_start]
            results = cursor.fetchall() # [cite: 5]

            for row in results:
                vn = row['vn']

                # [cite_start]Logic ดึง uc_money (Sub-query logic from 1.txt) [cite: 6, 7]    
                cursor.execute(f"""
                        SELECT 
                            SUM(IF(paidst = '02', sum_price, 0)) AS uc_money,
                            SUM(IF(paidst IN ('01', '03'), sum_price, 0)) AS paid_money,
                            SUM(IF(paidst = '00', sum_price, 0)) AS arrearage
                        FROM opitemrece WHERE vn = '{vn}'
                    """)
                money = cursor.fetchone()

                # [cite_start]Logic ดึง ptdepart [cite: 8, 9]
                cursor.execute(f"""
                    SELECT k.department FROM ptdepart p 
                    LEFT JOIN kskdepartment k ON k.depcode = p.outdepcode
                    WHERE p.vn = '{vn}' ORDER BY p.outtime DESC LIMIT 1
                """)
                dept = cursor.fetchone()
                outdep = dept['department'] if dept else None

                # [cite_start]Calculate Thai Date [cite: 15]
                vstdate = row['vstdate']
                thai_year = vstdate.year + 543
                thai_date = f"{thai_year}{vstdate.strftime('%m%d')}"

                # [cite_start]Upsert Logic [cite: 9, 10, 11]
                existing = local_db.query(VisitList).filter(VisitList.vn == vn).first()
                if not existing:
                    existing = VisitList(vn=vn)
                    local_db.add(existing)

                existing.vstdate = row['vstdate']
                existing.hn = row['hn']
                existing.name = row['name']
                existing.cid = row['cid']
                existing.pttype = row['pttype']
                existing.pttypename = row['pttypename']
                existing.department = row['department']
                existing.auth_code = row['auth_code']
                existing.close_visit = row['close_visit']
                existing.close_seq = row['close_seq']
                existing.close_staff = row['close_staff']
                existing.income = row['income']
                existing.uc_money = money['uc_money'] or 0
                existing.paid_money = money['paid_money'] or 0
                existing.arrearage = money['arrearage'] or 0
                existing.outdepcode = outdep
                existing.vsttime = row['vsttime']
                existing.ovstost = row['ovstost']
                existing.date = thai_date

                local_db.commit()

    except Exception as e:
        local_db.rollback()
        raise e
    finally:
        source_conn.close()
        local_db.close()

    return {
        "status": "success",
        "count": len(results)
    }

            