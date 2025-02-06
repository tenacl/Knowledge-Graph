import streamlit as st
from utils.api_handler import APIHandler
from utils.graph_renderer import GraphRenderer
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 지식 그래프 생성기",
    page_icon="🧠",
    layout="wide"
)

def get_gemini_api_keys():
    """Gemini API 키 목록을 가져옴 (Streamlit Secrets 또는 로컬 환경변수)"""
    # Streamlit Cloud의 경우
    if hasattr(st.secrets, 'gemini_keys'):
        return st.secrets.gemini_keys
        
    # 로컬 환경의 경우
    return [
        os.getenv(f'GEMINI_API_KEY_{i}')
        for i in range(1, 11)
        if os.getenv(f'GEMINI_API_KEY_{i}')
    ]

def initialize_session_state():
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {
            'openai': '',
            'gemini': get_gemini_api_keys(),  # 환경 변수에서 API 키 목록 가져오기
            'claude': '',
            'deepseek': ''  # DeepSeek는 사용자 입력으로 받음
        }
        # 모델 선택 상태 초기화
        st.session_state.selected_models = {
            'gemini': True,  # Gemini는 기본적으로 체크
            'deepseek': False  # DeepSeek는 기본적으로 체크 해제
        }

def main():
    initialize_session_state()
    
    # 그래프 데이터와 이미지를 저장할 session_state 추가
    if 'graph_images' not in st.session_state:
        st.session_state.graph_images = {}
    
    # 사이드바 설정
    with st.sidebar:
        st.title("🔑 API 키 설정")
        
        # 사용 가능한 모델 체크박스
        st.subheader("🤖 사용할 모델 선택")
        
        # 선택된 모델 상태 관리
        selected_models = {}
        
        # Gemini 모델 설정 (항상 표시)
        selected_models['gemini'] = st.checkbox(
            "Gemini",
            value=st.session_state.selected_models.get('gemini', True)
        )
        
        # API 키 입력 필드들
        st.session_state.api_keys['deepseek'] = st.text_input(
            "DeepSeek API 키",
            type="password",
            value=st.session_state.api_keys['deepseek']
        )
        
        st.session_state.api_keys['openai'] = st.text_input(
            "OpenAI API 키",
            type="password",
            value=st.session_state.api_keys['openai']
        )
        
        st.session_state.api_keys['claude'] = st.text_input(
            "Claude API 키",
            type="password",
            value=st.session_state.api_keys['claude']
        )
        
        # API 키가 입력된 경우에만 체크박스 표시
        if st.session_state.api_keys['deepseek'].strip():
            selected_models['deepseek'] = st.checkbox(
                "DeepSeek",
                value=st.session_state.selected_models.get('deepseek', True)
            )
        else:
            selected_models['deepseek'] = False
            
        if st.session_state.api_keys['openai'].strip():
            selected_models['openai'] = st.checkbox(
                "OpenAI",
                value=st.session_state.selected_models.get('openai', True)
            )
        else:
            selected_models['openai'] = False
            
        if st.session_state.api_keys['claude'].strip():
            selected_models['claude'] = st.checkbox(
                "Claude",
                value=st.session_state.selected_models.get('claude', True)
            )
        else:
            selected_models['claude'] = False
        
        # 선택 상태 업데이트
        st.session_state.selected_models.update(selected_models)

    # 메인 화면
    st.title("🧠 AI 지식 그래프 생성기")
    
    # 텍스트 입력
    user_input = st.text_area("텍스트를 입력하세요", height=200)
    
    if st.button("지식 그래프 생성"):
        if not user_input.strip():
            st.error("텍스트를 입력해주세요.")
            return
            
        # 선택된 모델이 있는지 확인
        if not any(st.session_state.selected_models.values()):
            st.error("최소 하나의 모델을 선택해주세요.")
            return
            
        api_handler = APIHandler(st.session_state.api_keys)
        graph_renderer = GraphRenderer()
        
        # 선택된 모델별로 그래프 생성
        selected_count = sum(1 for m in st.session_state.selected_models.values() if m)
        cols = st.columns(selected_count)
        col_idx = 0
        
        # 그래프 데이터 초기화
        st.session_state.graph_images = {}
        
        for model_name, is_selected in st.session_state.selected_models.items():
            if is_selected:
                with cols[col_idx]:
                    st.subheader(f"{model_name.title()} 모델 결과")
                    with st.spinner("그래프 생성 중..."):
                        try:
                            graph_data = api_handler.generate_graph_data(model_name, user_input)
                            graph_image = graph_renderer.render(graph_data)
                            
                            # 그래프 이미지를 session_state에 저장
                            st.session_state.graph_images[model_name] = graph_image
                            
                            # 그래프 표시
                            st.graphviz_chart(graph_image)
                            
                            # PNG 형식으로 다운로드 버튼 추가
                            png_data = graph_image.pipe(format='png')
                            st.download_button(
                                label="PNG 다운로드",
                                data=png_data,
                                file_name=f"knowledge_graph_{model_name}.png",
                                mime="image/png"
                            )
                            
                            # SVG 형식으로 다운로드 버튼 추가
                            svg_data = graph_image.pipe(format='svg').decode('utf-8')
                            st.download_button(
                                label="SVG 다운로드",
                                data=svg_data,
                                file_name=f"knowledge_graph_{model_name}.svg",
                                mime="image/svg+xml"
                            )
                            
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")
                col_idx += 1
    
    # 이전에 생성된 그래프가 있다면 표시
    elif st.session_state.graph_images:
        selected_count = len(st.session_state.graph_images)
        cols = st.columns(selected_count)
        
        for idx, (model_name, graph_image) in enumerate(st.session_state.graph_images.items()):
            with cols[idx]:
                st.subheader(f"{model_name.title()} 모델 결과")
                st.graphviz_chart(graph_image)
                
                # PNG 형식으로 다운로드 버튼 추가
                png_data = graph_image.pipe(format='png')
                st.download_button(
                    label="PNG 다운로드",
                    data=png_data,
                    file_name=f"knowledge_graph_{model_name}.png",
                    mime="image/png"
                )
                
                # SVG 형식으로 다운로드 버튼 추가
                svg_data = graph_image.pipe(format='svg').decode('utf-8')
                st.download_button(
                    label="SVG 다운로드",
                    data=svg_data,
                    file_name=f"knowledge_graph_{model_name}.svg",
                    mime="image/svg+xml"
                )

if __name__ == "__main__":
    main() 