import graphviz

class GraphRenderer:
    def __init__(self):
        self.graph_attrs = {
            'rankdir': 'TB',  # Top to Bottom 레이아웃
            'bgcolor': 'white',
            'splines': 'ortho',  # 직각 형태의 엣지
            'nodesep': '0.5',  # 노드 간 수평 간격
            'ranksep': '0.5',  # 노드 간 수직 간격
            'concentrate': 'true',  # 엣지 정리
            'charset': 'UTF-8'  # UTF-8 인코딩 설정
        }
        self.node_attrs = {
            'shape': 'box',
            'style': 'rounded,filled',
            'fillcolor': '#E8F5E9',
            'fontname': 'NanumGothic',  # 나눔고딕 폰트 사용
            'width': '1.5',  # 노드 너비
            'height': '0.8',  # 노드 높이
            'fontsize': '10',  # 폰트 크기
            'fontencoding': 'UTF-8'  # 폰트 인코딩 설정
        }
        self.edge_attrs = {
            'fontname': 'NanumGothic',  # 나눔고딕 폰트 사용
            'fontsize': '8',
            'len': '1.5',  # 엣지 길이
            'fontencoding': 'UTF-8'  # 폰트 인코딩 설정
        }
    
    def render(self, graph_data):
        """JSON 형식의 그래프 데이터를 Graphviz DOT 형식으로 변환"""
        try:
            dot = graphviz.Digraph(encoding='utf-8')  # UTF-8 인코딩 설정
            
            # 그래프 속성 설정
            for key, value in self.graph_attrs.items():
                dot.attr(key=key, value=value)
                
            # 노드 속성 설정
            dot.attr('node', **self.node_attrs)
            
            # 엣지 속성 설정
            dot.attr('edge', **self.edge_attrs)
            
            # 노드 추가
            if 'nodes' in graph_data:
                for node in graph_data['nodes']:
                    if isinstance(node, dict) and 'id' in node and 'label' in node:
                        # 노드 ID와 라벨을 UTF-8로 인코딩
                        node_id = str(node['id'])
                        node_label = str(node['label'])
                        dot.node(node_id, node_label)
            
            # 엣지 추가
            if 'edges' in graph_data:
                for edge in graph_data['edges']:
                    if isinstance(edge, dict) and 'from' in edge and 'to' in edge and 'label' in edge:
                        # 엣지 라벨을 UTF-8로 인코딩
                        from_node = str(edge['from'])
                        to_node = str(edge['to'])
                        edge_label = str(edge['label'])
                        dot.edge(from_node, to_node, edge_label)
            
            return dot
        except Exception as e:
            # 오류 발생 시 기본 그래프 반환
            dot = graphviz.Digraph(encoding='utf-8')
            dot.attr(rankdir='LR')
            dot.node('error', f'그래프 생성 오류: {str(e)}')
            return dot 