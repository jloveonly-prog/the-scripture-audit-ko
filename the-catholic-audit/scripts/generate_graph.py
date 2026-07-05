import csv
import json
import os

CSV_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\auto_conflict_results.csv"
HTML_FILE = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\08_REPORT\conflict_network.html"

def generate_html():
    if not os.path.exists(CSV_FILE):
        print("Error: CSV file not found.")
        return

    nodes_dict = {}
    edges = []

    # Read CSV
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            score = float(row['Score'])
            # 0.25 이상의 유의미한 충돌만 시각화 (가독성 목적)
            if score < 0.25: 
                continue
                
            source = row['Card_A_Claiming']
            target = row['Card_B_Negating']
            
            nodes_dict[source] = True
            nodes_dict[target] = True
            
            edges.append({
                "from": source,
                "to": target,
                "value": score * 10, # 선의 굵기
                "title": f"<div style='max-width:400px;'><b>[A의 주장]</b><br>{row['Claim_Text']}<br><br><b>[B의 부정]</b><br>{row['Negate_Text']}</div>"
            })

    nodes = [{"id": n, "label": n} for n in nodes_dict.keys()]

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>가톨릭 교리 충돌 네트워크 시각화 (The Catholic Audit)</title>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            body {{ margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; }}
            #header {{ padding: 15px 20px; background-color: #2c3e50; color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.5); position: absolute; z-index: 10; border-radius: 5px; margin: 20px; }}
            #mynetwork {{ width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; }}
            h1 {{ margin: 0 0 10px 0; font-size: 1.2rem; }}
            p {{ margin: 0; font-size: 0.9rem; color: #bdc3c7; }}
        </style>
    </head>
    <body>
        <div id="header">
            <h1>🛡️ The Catholic Audit - 교리 충돌 네트워크</h1>
            <p>점(Node)은 교리 문헌을, 선(Edge)은 상호 논리적 모순(A Not A)을 의미합니다.<br>노드에 마우스를 올리면 충돌하는 텍스트 원문을 볼 수 있습니다.</p>
        </div>
        <div id="mynetwork"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({json.dumps(nodes)});
            var edges = new vis.DataSet({json.dumps(edges)});
            var container = document.getElementById('mynetwork');
            var data = {{ nodes: nodes, edges: edges }};
            var options = {{
                nodes: {{
                    shape: 'dot', size: 25, 
                    font: {{ size: 14, color: '#ecf0f1', face: 'arial' }},
                    borderWidth: 2, 
                    color: {{ border: '#e74c3c', background: '#c0392b', highlight: {{ border: '#f1c40f', background: '#e67e22' }} }}
                }},
                edges: {{
                    color: {{ color: '#34495e', highlight: '#f1c40f', hover: '#e74c3c' }},
                    smooth: {{ type: 'dynamic' }}
                }},
                interaction: {{ hover: true, tooltipDelay: 200 }},
                physics: {{ 
                    stabilization: false, 
                    barnesHut: {{ gravitationalConstant: -30000, centralGravity: 0.3, springLength: 150 }} 
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Generated Network Graph HTML: {HTML_FILE}")

if __name__ == '__main__':
    generate_html()
