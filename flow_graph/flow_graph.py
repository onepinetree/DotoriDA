import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt
import platform
import matplotlib as mpl



if not firebase_admin._apps:
    cred = credentials.Certificate("retention_anlaysis/dotori-fd1b0-firebase-adminsdk-zzxxd-fb0e07e05e.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Set the font family globally to 'AppleGothic' or 'NanumGothic'
plt.rcParams['font.family'] = 'AppleGothic'  # or 'NanumGothic' if you prefer

# Fix negative sign display issues on macOS
if platform.system() == 'Darwin':
    mpl.rcParams['axes.unicode_minus'] = False

def check_info_documents():
    # Collections to exclude
    excluded_collections = ['staffOnly', 'userInfo', '문의하기']
    results = {}
    
    # Retrieve all collections
    collections = db.collections()
    for collection in collections:
        collection_name = collection.id
        if collection_name in excluded_collections:
            continue  # Skip excluded collections
            
        # Access the 'info' document in the current collection
        info_doc_ref = collection.document('info')
        info_doc = info_doc_ref.get()
        
        if info_doc.exists:
            fields = info_doc.to_dict()
            name_value = fields.get('name', '')
            nickname_value = fields.get('nickname', '')
            
            # Ensure the values are strings and strip whitespace
            has_name = bool(str(name_value).strip())
            has_nickname = bool(str(nickname_value).strip())
            
            if not has_name and not has_nickname:
                result = 1  # Both 'name' and 'nickname' are empty
            elif has_name and not has_nickname:
                result = 2  # Only 'name' has a value
            elif has_name and has_nickname:
                # Both 'name' and 'nickname' have values
                # Now check for 'chat' and 'notes' documents
                chat_doc_ref = collection.document('chat')
                notes_doc_ref = collection.document('notes')
                
                chat_doc = chat_doc_ref.get()
                notes_doc = notes_doc_ref.get()
                
                chat_exists = chat_doc.exists
                notes_exists = notes_doc.exists
                
                if not chat_exists and not notes_exists:
                    result = 3  # Neither 'chat' nor 'notes' exist
                elif chat_exists and not notes_exists:
                    result = 4  # 'chat' exists but 'notes' does not
                elif chat_exists and notes_exists:
                    result = 5  # Both 'chat' and 'notes' exist
                else:
                    # If 'notes' exists but 'chat' does not
                    result = 3
            else:
                result = 1  # Fallback to 1 if neither has value
        else:
            result = 1  # 'info' document does not exist
            
        # Store the result for the current collection
        results[collection_name] = result
        
    # Print the results in the specified format
    # for collection_name, status in results.items():
    #     print(f"Collection '{collection_name}': {status}")
        
    return results


def visualize_activation_funnel(results):
    import matplotlib.pyplot as plt

    total_users = len(results)
    
    # 단계별 사용자 수 초기화
    stage_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    # 각 단계에서의 사용자 수 계산
    for status in results.values():
        for stage in range(1, status + 1):
            if stage in stage_counts:
                stage_counts[stage] += 1
    
    # 각 단계에서의 사용자 비율 계산
    stages = sorted(stage_counts.keys())
    percentages = [(stage_counts[stage] / total_users) * 100 for stage in stages]
    
    # 각 활성화 단계에 대한 커스텀 라벨 정의
    stage_labels = [
        '이메일, 비밀번호 입력 스크린',
        '이름, 생년월일, 성별 입력 스크린',
        '토리 첫 대면 단계(닉네임 시간 설정)',
        '첫 대화',
        '첫 저장'
    ]
    
    # 활성화 퍼널 그래프 생성
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(stages, percentages, color='skyblue')
    ax.set_title(f'Activation Funnel Through Percentage of {total_users} Users', fontsize=14)
    ax.set_xlabel('활성화 단계', fontsize=12)
    ax.set_ylabel('유저 비율 (%)', fontsize=12)
    ax.set_xticks(stages)
    ax.set_xticklabels(stage_labels, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(0, 100)
    ax.grid(axis='y')
    plt.tight_layout()  # 레이블이 잘리지 않도록 레이아웃 조정
    plt.close(fig)  # 메모리 누수 방지를 위해 그래프 닫기
    return fig  # Figure 객체 반환

    # 각 단계의 비율 출력 (선택 사항)
    # for stage, percentage, label in zip(stages, percentages, stage_labels):
    #     print(f"Stage {stage} ({label}): {percentage:.2f}% users passed")

