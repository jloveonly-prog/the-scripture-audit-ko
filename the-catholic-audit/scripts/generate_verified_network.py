# -*- coding: utf-8 -*-
"""Generate conflict_network_v2.html from the 19 CVCAP-3.0-verified items
(05_COLLISION_CARDS/confirmed + combos), not the raw unfiltered
auto_conflict_results.csv that generate_graph.py visualizes.

If new COL-*/COMBO-* cards are confirmed later, add them to ITEMS below
and re-run.
"""
import json

# 19개 확정 항목 (04_DOCTRINE_DB / 05_COLLISION_CARDS 원문 및 07_REPORT/catholic_error_report_v2_ooda.md 기준,
# 2026-08-29 CVCAP 3.0 OODA 10라운드 정식 검증 완료)
ITEMS = [
    (1, "COL-001", "세례의 필수성 vs 무슬림 구원 가능성", "IMPLOSION",
     ["CCC-1257"], ["LG-16"]),
    (2, "COL-002", "은총·공로론 데드락", "IMPLOSION",
     ["CCC-1996"], ["TRENT-S06-C09"]),
    (3, "COL-003", "교황 무류성 vs 호노리우스 1세 이단 정죄", "IMPLOSION",
     ["VAT1-PASTOR-AETERNUS"], ["COUNCIL-CONST_III"]),
    (4, "COL-004", "교회 밖에 구원 없음 vs 교회 밖 구원 가능", "IMPLOSION",
     ["UNAM-SANCTAM", "COUNCIL-LATERAN_IV"], ["CCC-0847"]),
    (5, "COL-005", "사제 사죄 필수 vs 완전한 통회로 용서 가능", "PARTIAL",
     ["TRENT-S14-CONFESSION"], ["CCC-1452"]),
    (6, "COL-006", "연옥론 (정화 vs 면죄부 경감)", "IMPLOSION",
     ["CCC-1030"], ["CCC-1471"]),
    (7, "COL-007", "원죄의 보편성 vs 마리아 무염시태", "IMPLOSION",
     ["CCC-0402"], ["CCC-0491"]),
    (8, "COL-008", "Ex Cathedra 무류성의 순환 논리", "IMPLOSION",
     ["VAT1-PASTOR-AETERNUS"], ["논리학(순환논증)"]),
    (9, "COL-009", "교황 복종의 절대적 필요성 vs LG-16", "IMPLOSION",
     ["UNAM-SANCTAM"], ["LG-16"]),
    (10, "COL-010", "순교자도 예외 없는 지옥 vs 무지자의 구원 가능성", "IMPLOSION",
     ["COUNCIL-FLORENCE"], ["CCC-846_848"]),
    (11, "COL-011", "세례 필수 파문 조항(트렌트) vs LG-16", "IMPLOSION",
     ["TRENT-S07-C05"], ["LG-16"]),
    (12, "COL-012", "동성 커플 축복 권한 전무(2021) vs 사목적 축복 허용(2023)", "IMPLOSION",
     ["CDF-RESPONSUM"], ["FIDUCIA-SUPPLICANS"]),
    (13, "COL-013", "종교 자유 단죄(1864) vs 종교 자유 천부인권(1965)", "IMPLOSION",
     ["DENZINGER-SYLLABUS"], ["DIGNITATIS-HUMANAE"]),
    (14, "COL-014", "비가톨릭 성사 수여 허용(교회법 844) vs 교회 밖 구원 불가", "IMPLOSION",
     ["CANON-SACR"], ["COUNCIL-LATERAN_IV"]),
    (15, "COMBO-01", "마리아론 연쇄 붕괴 (무염시태·몽소승천 3단 콤보)", "IMPLOSION",
     ["MUNIFICENTISSIMUS-DEUS", "INEFFABILIS-DEUS"], ["TRENT-S05(원죄교령)", "교부 침묵(이레네오·터툴리아누스)"]),
    (16, "COMBO-02", "교황 무류성 연쇄 붕괴 (콤보)", "IMPLOSION",
     ["VAT1-PASTOR-AETERNUS"], ["COUNCIL-CONST_III", "COUNCIL-CONSTANCE", "DENZINGER-SYLLABUS"]),
    (17, "COMBO-03", "구원론 연쇄 붕괴 (콤보)", "IMPLOSION",
     ["UNAM-SANCTAM", "COUNCIL-FLORENCE", "TRENT-S06-C09"], ["LG-16", "JDDJ-1999"]),
    (18, "COMBO-04", "연옥·대사 경제 붕괴 (콤보)", "IMPLOSION",
     ["CCC-1996"], ["TRENT-S06-C32", "CCC-1471", "CCC-1452"]),
    (19, "COMBO-05", "도덕 교리 붕괴 (콤보 — 동성 축복)", "PARTIAL",
     ["CDF-RESPONSUM"], ["FIDUCIA-SUPPLICANS"]),
]

VERDICT_COLOR = {"IMPLOSION": "#e74c3c", "PARTIAL": "#f39c12"}

nodes = {}
edges = []


def add_node(doc_id, is_combo=False):
    if doc_id not in nodes:
        nodes[doc_id] = {
            "id": doc_id, "label": doc_id,
            "shape": "box" if is_combo else "dot",
            "size": 20,
            "color": {"border": "#8e44ad", "background": "#6c3483"} if is_combo else {"border": "#2980b9", "background": "#21618c"},
            "font": {"size": 13, "color": "#ecf0f1"},
        }


for idx, code, title, verdict, sides_a, sides_b in ITEMS:
    if code.startswith("COMBO") and (len(sides_a) > 1 or len(sides_b) > 1):
        combo_node = code
        add_node(combo_node, is_combo=True)
        for d in sides_a + sides_b:
            add_node(d)
            edges.append({
                "from": combo_node, "to": d,
                "color": {"color": VERDICT_COLOR[verdict]},
                "value": 3,
                "title": f"<b>[{idx}] {code}: {title}</b><br>판결: {verdict}<br>정식보고서 항목 {idx}번 참조",
            })
    else:
        for a in sides_a:
            add_node(a)
            for b in sides_b:
                add_node(b)
                edges.append({
                    "from": a, "to": b,
                    "color": {"color": VERDICT_COLOR[verdict]},
                    "value": 4,
                    "title": f"<b>[{idx}] {code}: {title}</b><br>판결: {verdict}<br>정식보고서 항목 {idx}번 참조",
                })

nodes_list = list(nodes.values())

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>가톨릭 교리 충돌 네트워크 v2 (CVCAP 3.0 정식 검증 19건)</title>
<script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; padding:0; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; background:#1a1a1a; }}
  #header {{ padding:15px 20px; background:#2c3e50; color:#fff; box-shadow:0 2px 5px rgba(0,0,0,.5); position:absolute; z-index:10; border-radius:5px; margin:20px; max-width:420px; }}
  #legend {{ padding:10px 15px; background:#2c3e50; color:#fff; position:absolute; z-index:10; bottom:20px; left:20px; border-radius:5px; font-size:.85rem; }}
  #mynetwork {{ width:100vw; height:100vh; position:absolute; top:0; left:0; }}
  h1 {{ margin:0 0 8px 0; font-size:1.15rem; }}
  p {{ margin:0; font-size:.85rem; color:#bdc3c7; line-height:1.4; }}
  .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }}
  .box {{ display:inline-block; width:10px; height:10px; margin-right:6px; }}
</style>
</head>
<body>
<div id="header">
  <h1>🛡️ The Catholic Audit — 교리 충돌 네트워크 v2</h1>
  <p>CVCAP 3.0 정식 문헌 법정(OODA 10라운드)으로 검증 완료된 <b>19개 항목</b>만 표시합니다 (구 버전의 미검증 자동탐지 2,154건 노이즈 없음).<br>
  원(●)은 개별 문헌, 사각형(■)은 콤보 카드입니다. 선에 마우스를 올리면 해당 항목과 판결이 표시됩니다.<br>
  전체 논증은 <code>catholic_error_report_v2_ooda.md</code> 참조.</p>
</div>
<div id="legend">
  <div><span class="dot" style="background:#e74c3c;"></span>💥 IMPLOSION (17건)</div>
  <div><span class="dot" style="background:#f39c12;"></span>⚠️ PARTIAL (2건)</div>
  <div><span class="dot" style="background:#21618c;"></span>개별 문헌</div>
  <div><span class="box" style="background:#6c3483;"></span>콤보 카드</div>
</div>
<div id="mynetwork"></div>
<script>
  var nodes = new vis.DataSet({json.dumps(nodes_list)});
  var edges = new vis.DataSet({json.dumps(edges)});
  var container = document.getElementById('mynetwork');
  var data = {{ nodes: nodes, edges: edges }};
  var options = {{
    nodes: {{ borderWidth:2 }},
    edges: {{ smooth: {{ type:'dynamic' }}, hoverWidth:2 }},
    interaction: {{ hover:true, tooltipDelay:150 }},
    physics: {{ stabilization:false, barnesHut: {{ gravitationalConstant:-25000, centralGravity:0.35, springLength:160 }} }}
  }};
  new vis.Network(container, data, options);
</script>
</body>
</html>
"""

out = r"D:\01.TheScriptureAudit_ko\the-catholic-audit\07_REPORT\conflict_network_v2.html"
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print("Wrote", out)
print("Nodes:", len(nodes_list), "Edges:", len(edges))
