import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def plot_heatmap(df):
    # 'cohort_num' 열 제외하고 복사본 생성
    df_numeric = df.drop(columns=['cohort_num']).copy()
    
    # 퍼센트 문자열을 숫자(float)로 변환
    for col in df_numeric.columns:
        df_numeric[col] = df_numeric[col].astype(str).map(
            lambda x: float(x.rstrip('%')) if '%' in x else np.nan
        )
    
    # 히트맵에서 'Average'가 가장 위에 오고, 나머지는 날짜의 빠른 순으로 정렬되도록 인덱스 재정렬
    date_indices = [idx for idx in df_numeric.index if idx != 'Average']
    date_indices_sorted = sorted(date_indices, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    new_index_order = ['Average'] + date_indices_sorted
    df_numeric = df_numeric.loc[new_index_order]
    
    # 그래프 객체 생성
    nrows, ncols = df_numeric.shape
    cell_size = 0.8
    fig, ax = plt.subplots(figsize=(ncols * cell_size, nrows * cell_size))
    
    # 값을 퍼센트 형식으로 표시
    annot_data = df_numeric.applymap(lambda x: f'{x:.1f}%' if not pd.isna(x) else '')
    
    sns.heatmap(
        df_numeric, 
        cmap='Blues', 
        annot=annot_data,
        fmt="", 
        linewidths=.5, 
        cbar_kws={'orientation':'vertical'},
        ax=ax  # ax 인자 추가
    )
    
    # 컬럼 이름을 히트맵 상단에 표시
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    
    # 레이블 설정
    ax.set_title('Retention Rate Heatmap')
    ax.set_ylabel('Cohort')
    
    plt.tight_layout()
    plt.close(fig)  # 그래프를 닫아 메모리 누수 방지
    return fig  # Figure 객체 반환
