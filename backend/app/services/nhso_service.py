import requests
from ..database import get_local_session
from ..models import VisitList
from ..config import load_config
from datetime import datetime

def check_nhso_authen():
    db = get_local_session()
    conf = load_config()

    visits = db.query(VisitList).filter(VisitList.endpoint == None).limit(50).all()

    updated_count = 0

    for v in visits:
        try:
            url = conf.get('api_endpoint', 'https://authenucws.nhso.go.th/authencodestatus/api/check-authen-status')
            token = conf.get('api_token', '')
            header_name = conf.get('api_header', 'Authorization')

            headers = {
                header_name: token,
                'Accept': 'application/json'
            }
            params = {
                'personalId': v.cid,
                'serviceDate': v.vstdate.strftime('%y-%m-%d')
            }

            resp = requests.get(url=url, headers=headers, params=params, timeout=5)

            # [cite_start]3. ตรวจสอบและอัปเดต [cite: 24, 25]
            if resp.status_code == 200:
                data = resp.json()
                claim_code = None
                if 'serviceHistories' in data and len(data['serviceHistories']) > 0:
                    claim_code = data['serviceHistories'][0].get('claimCode')
                
                if claim_code:
                    v.endpoint = claim_code # [cite: 26]
                    updated_count += 1
        except Exception as e:
            print(f"Error checking VN {v.vn}: {e}")

    db.commit()
    db.close()
    return {"status": "success", "updated": updated_count}