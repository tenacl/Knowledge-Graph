import openai
import google.generativeai as genai
from anthropic import Anthropic
import requests
import json
import streamlit as st

class APIHandler:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self._initialize_clients()
    
    def _initialize_clients(self):
        """API 클라이언트 초기화"""
        if self.api_keys['openai']:
            openai.api_key = self.api_keys['openai']
        if self.api_keys['gemini']:
            genai.configure(api_key=self.api_keys['gemini'])
        if self.api_keys['claude']:
            self.claude_client = Anthropic(api_key=self.api_keys['claude'])
    
    def _get_graph_prompt(self, text):
        """지식 그래프 생성을 위한 프롬프트 생성"""
        return f"""다음 텍스트를 분석하여 지식 그래프로 표현해주세요.
        
        규칙:
        1. 응답은 반드시 아래 JSON 형식으로만 작성해주세요.
        2. 다른 설명이나 부가 텍스트는 포함하지 마세요.
        3. 각 노드의 label은 5단어 이내로 짧고 명확하게 작성해주세요.
        4. 관계(edge)도 1-2단어로 간단히 표현해주세요.
        5. 전체 노드 개수는 10개 이내로 제한해주세요.
        6. JSON 형식은 다음과 같아야 합니다:
        {{
            "nodes": [
                {{"id": "개념1", "label": "핵심 개념 (3단어 이내)"}},
                {{"id": "개념2", "label": "간단한 설명"}}
            ],
            "edges": [
                {{"from": "개념1", "to": "개념2", "label": "관계"}}
            ]
        }}

        분석할 텍스트:
        {text}

        위 텍스트를 분석하여 JSON 형식으로만 응답해주세요.
        """

    def generate_graph_data(self, model_name, text):
        """선택된 모델을 사용하여 그래프 데이터 생성"""
        prompt = self._get_graph_prompt(text)
        
        if model_name == 'openai':
            return self._generate_with_openai(prompt)
        elif model_name == 'gemini':
            return self._generate_with_gemini(prompt)
        elif model_name == 'claude':
            return self._generate_with_claude(prompt)
        elif model_name == 'deepseek':
            return self._generate_with_deepseek(prompt)
        else:
            raise ValueError(f"지원하지 않는 모델: {model_name}")

    def _generate_with_openai(self, prompt):
        """OpenAI API를 사용하여 그래프 데이터 생성"""
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        return json.loads(response.choices[0].message.content)

    def _generate_with_gemini(self, prompt):
        """Gemini API를 사용하여 그래프 데이터 생성"""
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        try:
            response_text = response.text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            raise ValueError("유효한 JSON 응답을 찾을 수 없습니다")
        except Exception as e:
            st.error(f"Gemini 응답 처리 중 오류 발생: {str(e)}")
            return {
                "nodes": [
                    {"id": "error", "label": "응답 처리 오류"}
                ],
                "edges": []
            }

    def _generate_with_claude(self, prompt):
        """Claude API를 사용하여 그래프 데이터 생성"""
        response = self.claude_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(response.content[0].text)
        except:
            return json.loads(response.content)

    def _generate_with_deepseek(self, prompt):
        """DeepSeek API를 사용하여 그래프 데이터 생성"""
        headers = {
            "Authorization": f"Bearer {self.api_keys['deepseek']}",
            "Content-Type": "application/json"
        }
        
        try:
            session = requests.Session()
            session.mount('https://', requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=10,
                pool_maxsize=10
            ))
            
            response = session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Generate knowledge graph in JSON format"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "timeout": 60
                },
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                raise ValueError(f"API 호출 실패: {response.status_code}")
                
            response_json = response.json()
            content = response_json['choices'][0]['message']['content'].strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    return json.loads(content[start_idx:end_idx])
                raise ValueError("유효한 JSON을 찾을 수 없습니다")
                
        except requests.exceptions.Timeout:
            st.error("DeepSeek API 타임아웃 발생")
            return {
                "nodes": [
                    {"id": "timeout", "label": "API 타임아웃"},
                    {"id": "suggestion", "label": "다른 모델을 사용해보세요"}
                ],
                "edges": [
                    {"from": "timeout", "to": "suggestion", "label": "해결방안"}
                ]
            }
        except Exception as e:
            st.error(f"DeepSeek 처리 중 오류: {str(e)}")
            return {
                "nodes": [
                    {"id": "error", "label": "API 오류 발생"},
                    {"id": "details", "label": str(e)[:50]}
                ],
                "edges": [
                    {"from": "error", "to": "details", "label": "원인"}
                ]
            } 