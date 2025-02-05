import streamlit as st
from utils.api_handler import APIHandler
from utils.graph_renderer import GraphRenderer
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(
    page_title="AI 지식 그래프 생성기",
    page_icon="🧠",
    layout="wide"
)

def initialize_session_state():
    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {
            'openai': '',
            'gemini': '',
            'claude': '',
            'deepseek': ''
        }

def main():
    initialize_session_state()
    
    # 그래프 데이터와 이미지를 저장할 session_state 추가
    if 'graph_images' not in st.session_state:
        st.session_state.graph_images = {}
    
    # 사이드바 설정
    with st.sidebar:
        st.title("🔑 API 키 설정")
        
        # API 키 입력
        st.session_state.api_keys['openai'] = st.text_input("OpenAI API 키", type="password", value=st.session_state.api_keys['openai'])
        st.session_state.api_keys['gemini'] = st.text_input("Gemini API 키", type="password", value=st.session_state.api_keys['gemini'])
        st.session_state.api_keys['claude'] = st.text_input("Claude API 키", type="password", value=st.session_state.api_keys['claude'])
        st.session_state.api_keys['deepseek'] = st.text_input("DeepSeek API 키", type="password", value=st.session_state.api_keys['deepseek'])
        
        # 사용 가능한 모델 체크박스
        st.subheader("🤖 사용할 모델 선택")
        available_models = {
            name: key for name, key in st.session_state.api_keys.items() if key.strip()
        }
        
        selected_models = {}
        for model_name in available_models:
            selected_models[model_name] = st.checkbox(f"{model_name.title()} 사용", value=True)
        
        if not available_models:
            st.warning("최소 하나의 API 키를 입력해주세요.")

    # 메인 화면
    st.title("🧠 AI 지식 그래프 생성기")
    
    # 텍스트 입력
    user_input = st.text_area("텍스트를 입력하세요", height=200)
    
    if st.button("지식 그래프 생성"):
        if not user_input.strip():
            st.error("텍스트를 입력해주세요.")
            return
            
        if not available_models:
            st.error("최소 하나의 API 키를 입력해주세요.")
            return
            
        api_handler = APIHandler(st.session_state.api_keys)
        graph_renderer = GraphRenderer()
        
        # 선택된 모델별로 그래프 생성
        selected_count = sum(1 for m in selected_models.values() if m)
        if selected_count == 0:
            st.error("최소 하나의 모델을 선택해주세요.")
            return
            
        cols = st.columns(selected_count)
        col_idx = 0
        
        # 그래프 데이터 초기화
        st.session_state.graph_images = {}
        
        for model_name, is_selected in selected_models.items():
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