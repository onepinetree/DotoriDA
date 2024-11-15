import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def sort_dates(date_list):
    # 문자열 날짜 리스트를 datetime 객체 리스트로 변환 후 정렬
    sorted_dates = sorted(date_list, key=lambda date: datetime.strptime(date, '%Y-%m-%d'))
    return sorted_dates


if not firebase_admin._apps:
    # cred = credentials.Certificate("retention_analysis/dotori-fd1b0-firebase-adminsdk-zzxxd-fb0e07e05e.json")
    cred = credentials.Certificate('/etc/secrets/dotori-fd1b0-firebase-adminsdk-zzxxd-fb0e07e05e.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
retention_doc_ref = db.collection('staffOnly').document('retentionData')



def getUserData()->dict:
    '''user_data의 형식에 맞게 data를 return 하는 함수'''

    user_data = {}
    for user_uid, active_date_dict in retention_doc_ref.get().to_dict().items():
        if user_uid == 'dummy':
            continue
        user_active_date = []
        for date_key in active_date_dict:
            user_active_date.append(date_key)

        user_data[user_uid] = sort_dates(date_list=user_active_date)
    
    return user_data




