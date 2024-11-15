import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from retention_analysis.firebase_info_fetcher import getUserData


user_data = getUserData()


# 날짜 리스트를 이진 리스트로 변환하는 기존 함수
def dates_to_binary_list(date_list: list):
    """주어진 날짜 리스트를 이진 리스트로 변환합니다."""
    date_format = '%Y-%m-%d'
    try:
        # 문자열을 datetime 객체로 변환
        date_list = [datetime.strptime(date_str, date_format) for date_str in date_list]
    except ValueError as e:
        print(f"날짜 형식이 잘못되었습니다: {e}")
        return []
    date_set = set(date_list)
    start_date = min(date_list)
    end_date = max(date_list)
    delta_days = (end_date - start_date).days + 1

    binary_list = []
    for i in range(delta_days):
        current_date = start_date + timedelta(days=i)
        if current_date in date_set:
            binary_list.append(1)
        else:
            binary_list.append(0)
    return binary_list

# 수정된 함수
def modified_dates_to_binary_list(date_list: list):
    """날짜 리스트에 오늘 날짜를 추가하고 마지막 1을 제거하여 이진 리스트로 변환합니다."""
    date_format = '%Y-%m-%d'
    today = datetime.now().strftime(date_format)
    try:
        # 문자열을 datetime 객체로 변환
        date_list_dt = [datetime.strptime(date_str, date_format) for date_str in date_list]
        today_dt = datetime.strptime(today, date_format)
    except ValueError as e:
        print(f"날짜 형식이 잘못되었습니다: {e}")
        return []

    # 마지막 날짜가 오늘 날짜가 아닌 경우
    if date_list_dt[-1] != today_dt:
        date_list.append(today)
        binary_list = dates_to_binary_list(date_list)
        # 마지막 1 제거
        for i in range(len(binary_list)-1, -1, -1):
            if binary_list[i] == 1:
                binary_list[i] = 0
                break
        return binary_list
    else:
        # 오늘 날짜가 이미 포함된 경우 그대로 실행
        return dates_to_binary_list(date_list)

# #사용 예시
# date_list = ['2024-9-26', '2024-9-29', '2024-9-30', '2024-10-7']
# print(dates_to_binary_list(date_list))
# print(modified_dates_to_binary_list(date_list))


def modifyIntoBracket(lst : list, bracket : int) -> list:
    '''양의 정수의 bracket을 넣으면 binary_list를 bracket_retention 측정에 맞게 변형해주는 함수'''
    return [
        1 if any(lst[i:i + bracket]) else 0 
        for i in range(0, len(lst) - len(lst) % bracket, bracket)
    ]


def combine_binary_lists_to_average_list(binary_lists):
    '''리텐션에 대한 바이너리 리스트들을 담고 있는 리스트의 평균을 구합니다'''
 
    max_length = max(len(lst) for lst in binary_lists)
    padded_lists = [lst + [np.nan]*(max_length - len(lst)) for lst in binary_lists]
    df = pd.DataFrame(padded_lists)
    
    # 각 컬럼의 평균을 계산하여 백분율로 변환합니다.
    averages = df.mean(skipna=True) * 100
    
    # 평균 값의 소수점을 조절하고 백분율 기호를 추가합니다.
    averages = averages.round(2).astype(str) + '%'
    
    # 리스트로 변환하여 반환합니다.
    return averages.tolist()

# binary_lists = [
#     [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#     [1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
#     [1, 0, 0, 0, 0, 0, 0, 0, 1]

# print(combine_binary_lists_with_average_list(binary_lists))




def create_date_list(start_date, end_date):
    '''시작 날짜와 끝 날짜를 넣으면 사이 날짜를 채운 리스트를 return 하는 함수'''
    date_list = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_date <= end_date_obj:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list

# print(create_date_list('2024-12-30', '2025-1-14'))


def dict_to_dataframe(cohort_data):
    # 각 리스트의 최대 길이를 구합니다.
    max_length = max(len(info['cohort_retention_rate']) for info in cohort_data.values())
    
    # 열 이름을 'cohort_num', 'Day_0', 'Day_1', ... 형식으로 만듭니다.
    column_names = ['cohort_num'] + [f'Day_{i}' for i in range(max_length)]
    
    # 데이터를 변환하여 데이터프레임을 생성합니다.
    data = {}
    for key, value in cohort_data.items():
        # cohort_num 저장
        cohort_num = value['cohort_num']
        
        # 리스트가 짧은 경우 NaN으로 채워줍니다.
        padded_list = value['cohort_retention_rate'] + [np.nan] * (max_length - len(value['cohort_retention_rate']))
        
        # 첫 번째 열로 cohort_num을 넣어줍니다.
        data[key] = [cohort_num] + padded_list
    
    # 데이터프레임 생성
    df = pd.DataFrame.from_dict(data, orient='index', columns=column_names)
    
    # 'Average' 행 계산 및 추가
    retention_columns = df.columns[1:]  # 'cohort_num' 제외한 나머지 열
    total_cohort_num = df['cohort_num'].sum()
    weighted_averages = []
    
    for col in retention_columns:
        valid_rows = df[col].notna()
        if valid_rows.any():
            weights = df.loc[valid_rows, 'cohort_num']
            # 퍼센트 문자열을 실수로 변환
            values = df.loc[valid_rows, col].str.rstrip('%').astype(float)
            weighted_avg = np.sum(values * weights) / np.sum(weights)
            weighted_averages.append(f'{weighted_avg:.2f}%')
        else:
            weighted_averages.append(np.nan)
    
    df.loc['Average'] = [total_cohort_num] + weighted_averages
    
    # 인덱스 재정렬: 'Average'를 가장 위로, 나머지는 날짜 순으로 정렬
    date_indices = [idx for idx in df.index if idx != 'Average']
    # 날짜 문자열을 datetime 객체로 변환하여 정렬
    date_indices_sorted = sorted(date_indices, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    # 새로운 인덱스 순서로 재정렬
    df = df.reindex(['Average'] + date_indices_sorted)
    
    return df





# 사용자 데이터에서 시작 날짜와 종료 날짜를 동적으로 설정
date_format = '%Y-%m-%d'
all_dates = []
for dates in user_data.values():
    date_objs = [datetime.strptime(date_str, date_format) for date_str in dates]
    all_dates.extend(date_objs)

start_date = min(all_dates).strftime(date_format)
end_date = max(all_dates).strftime(date_format)


def buildCohortData(start_date: str, end_date: str, bracket: int):
    '''코호트 데이터를 생성해서 return 하는 함수'''
    cohort_data = {}
    for date in create_date_list(start_date=start_date, end_date=end_date):
        #같은 코호트끼리의 핵심이벤트 수행 리스트를 모은 리스트
        cohortUserKeyEventDates = []
        for user, userKeyEventDates in user_data.items(): 
            if userKeyEventDates[0] == date:
                binary_list = modified_dates_to_binary_list(userKeyEventDates)
                binary_list = modifyIntoBracket(lst=binary_list, bracket=bracket)
                if binary_list:                                                                                                                                                                                                                                                                                                                                                                                                                                
                    cohortUserKeyEventDates.append(binary_list)
        if len(cohortUserKeyEventDates) > 0:
            #같은 길이의 list들을 average하게 됨
            averages = combine_binary_lists_to_average_list(cohortUserKeyEventDates)
            # 백분율 형식으로 변환
            averages = [f"{avg}%" for avg in averages]
            cohort_data[date] = {
                'cohort_num': len(cohortUserKeyEventDates),
                'cohort_retention_rate': averages
            }
    return cohort_data






#bracket을 설정해주세요
cohort_data = buildCohortData(start_date=start_date, end_date=end_date, bracket=1)


