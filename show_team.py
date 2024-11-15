import streamlit as st
from retention_analysis.main import cohort_data, dict_to_dataframe
from retention_analysis.plot_heatmap import plot_heatmap
from retention_analysis.plot_retention_graph import plot_average_retention_with_plateau
from flow_graph.flow_graph import check_info_documents, visualize_activation_funnel

st.title('토리숲 Growth Analysis')
st.write('')



# 세션 상태 초기화
if 'show_retention' not in st.session_state:
    st.session_state['show_retention'] = False
if 'show_activation' not in st.session_state:
    st.session_state['show_activation'] = False

# 다섯 개의 동일한 비율의 열 생성
col1, col2, col3, col4, col5 = st.columns(5)

# 두 번째 열에 'Retention' 버튼 배치
with col2:
    if st.button('Retention'):
        st.session_state['show_retention'] = True
        st.session_state['show_activation'] = False  # 다른 콘텐츠 숨기기

# 네 번째 열에 'Activation' 버튼 배치
with col4:
    if st.button('Activation'):
        st.session_state['show_activation'] = True
        st.session_state['show_retention'] = False  # 다른 콘텐츠 숨기기

# Retention 콘텐츠 표시 (전체 너비)
if st.session_state['show_retention']:
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    st.subheader('코호트 데이터프레임')
    df = dict_to_dataframe(cohort_data)
    st.write(df)

    # 히트맵 그리기
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    st.subheader('코호트 리텐션 히트맵')
    fig_heatmap = plot_heatmap(df)
    st.pyplot(fig_heatmap)

    # 평균 유지율 그래프 그리기
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    st.subheader('리텐션 그래프')
    fig_retention = plot_average_retention_with_plateau(df)
    st.pyplot(fig_retention)

# Activation 콘텐츠 표시 (전체 너비)
if st.session_state['show_activation']:
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    st.subheader('activation 통과율')
    results = check_info_documents()
    # 활성화 퍼널 그래프 생성
    fig = visualize_activation_funnel(results)

    # 그래프를 Streamlit에 표시
    st.pyplot(fig)
















