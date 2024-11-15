import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


def plot_average_retention_with_plateau(df):
    # 'Average' 행 추출
    average_row = df.loc['Average']
    
    # 'cohort_num' 가져오기
    total_cohort_num = average_row['cohort_num']
    
    # 'cohort_num'을 제외한 유지율 데이터 추출
    retention_rates = average_row.drop('cohort_num')
    
    # '%' 기호 제거 및 실수형 변환
    retention_rates = retention_rates.str.rstrip('%').astype(float)
    
    # x축 라벨 생성
    x_labels = retention_rates.index.tolist()
    x_values = np.arange(len(x_labels))
    
    # 유지율 변화 계산
    changes = retention_rates.diff().abs()
    # 변화율이 threshold 이하인 지점 찾기
    threshold = 0.5  # 0.5% 이하의 변화
    plateau_start = None
    for i in range(1, len(changes)):
        if changes.iloc[i] <= threshold:
            plateau_start = i
            break
    
    # 그래프 객체 생성
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x_values, retention_rates, color='black', marker='o')
    
    # Plateau 영역 강조
    if plateau_start is not None:
        ax.axvspan(x_values[plateau_start], x_values[-1], color='lightgrey', alpha=0.5, label='Retention Plateau')
    
    # 배경색 설정
    ax.set_facecolor('skyblue')
    
    # 각 포인트에 퍼센트 값 표시
    for i, value in enumerate(retention_rates):
        ax.text(x_values[i], retention_rates.iloc[i] + 1, f'{value:.2f}%', ha='center', va='bottom', color='black')
    
    # x축 라벨 설정
    ax.set_xticks(x_values)
    ax.set_xticklabels(x_labels)
    
    # y축 라벨 설정
    ax.set_ylabel('Retention Rate (%)')
    
    # 제목 설정
    ax.set_title(f'Retention Curve of {int(total_cohort_num)} Users')
    
    # 범례 추가
    if plateau_start is not None:
        ax.legend()
    
    # 그리드 추가
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.close(fig)  # 그래프를 닫아 메모리 누수 방지
    return fig  # Figure 객체 반환
