# -*- coding: utf-8 -*-
"""Generate conflict_network_v2.html from the 24 CVCAP-verified items
(05_COLLISION_CARDS/confirmed + combos), with v10 reclassified verdicts.

v10 (2026-09-02): 판정 5분류 반영 — IMPLOSION/LOOP/DEFENDED/WITHDRAWN/OUT_OF_SCOPE.
새 COL-*/COMBO-* 카드가 확정되면 ITEMS에 추가하고 재실행.
판정 근거: 07_REPORT/catholic_error_report_v10_final.md (헤더·목차·PART 5).
"""
import json

# 24개 항목 — (보고서 항목#, 카드, 제목, v10 판정, A측 문헌, B측 문헌)
ITEMS = [
    (1, "COL-001", "세례의 필수성 vs 무슬림 구원 가능성", "DEFENDED",
     ["CCC-1257"], ["LG-16"]),
    (2, "COL-002", "은총·공로론 데드락", "WITHDRAWN",
     ["CCC-1996"], ["TRENT-S06-C09"]),
    (3, "COL-003", "교황 무류성 vs 호노리우스 1세 정죄", "WITHDRAWN",
     ["VAT1-PASTOR-AETERNUS"], ["COUNCIL-CONST_III"]),
    (4, "COL-004", "교회 밖에 구원 없음 vs 교회 밖 구원 가능", "DEFENDED",
     ["UNAM-SANCTAM", "COUNCIL-LATERAN_IV"], ["CCC-0847"]),
    (5, "COL-005", "사제 사죄 필수 vs 완전한 통회로 용서 가능", "DEFENDED",
     ["TRENT-S14-CONFESSION"], ["CCC-1452"]),
    (6, "COL-006", "연옥의 필요성 vs 전대사", "DEFENDED",
     ["CCC-1030"], ["CCC-1471"]),
    (7, "COL-007", "원죄의 보편성 vs 마리아 무염시태", "DEFENDED",
     ["CCC-0402"], ["CCC-0491"]),
    (8, "COL-008", "Ex Cathedra 무류성의 순환 논리", "OUT_OF_SCOPE",
     ["VAT1-PASTOR-AETERNUS"], ["논리학(순환논증)"]),
    (9, "COL-009", "교황 복종의 절대적 필요성 vs LG-16", "WITHDRAWN",
     ["UNAM-SANCTAM"], ["LG-16"]),
    (10, "COL-010", "피렌체의 무조건 배제 vs 무지자의 구원", "LOOP",
     ["COUNCIL-FLORENCE"], ["CCC-846_848"]),
    (11, "COL-011", "세례 필수 파문 조항(트렌트) vs LG-16", "DEFENDED",
     ["TRENT-S07-C05"], ["LG-16"]),
    (12, "COL-012", "동성 커플 축복 — 2021 금지 vs 2023 허용", "LOOP",
     ["CDF-RESPONSUM"], ["FIDUCIA-SUPPLICANS"]),
    (13, "COL-013", "종교 자유 — Syllabus 78 vs DH 3", "IMPLOSION",
     ["DENZINGER-SYLLABUS"], ["DIGNITATIS-HUMANAE"]),
    (14, "COL-014", "교회법 844 예외 vs 라테란4 배타성", "DEFENDED",
     ["CANON-SACR"], ["COUNCIL-LATERAN_IV"]),
    (15, "COMBO-01", "마리아론 연쇄 (콤보)", "WITHDRAWN",
     ["MUNIFICENTISSIMUS-DEUS", "INEFFABILIS-DEUS"], ["TRENT-S05(원죄교령)", "교부 문헌(코퍼스 외)"]),
    (16, "COMBO-02", "교황 무류성 연쇄 (콤보)", "WITHDRAWN",
     ["VAT1-PASTOR-AETERNUS"], ["COUNCIL-CONST_III", "COUNCIL-CONSTANCE", "DENZINGER-SYLLABUS"]),
    (17, "COMBO-03", "구원론 연쇄 (콤보)", "WITHDRAWN",
     ["UNAM-SANCTAM", "COUNCIL-FLORENCE", "TRENT-S06-C09"], ["LG-16", "JDDJ-1999"]),
    (18, "COMBO-04", "연옥·대사 경제 (콤보)", "WITHDRAWN",
     ["CCC-1996"], ["TRENT-S06-C32", "CCC-1471", "CCC-1452"]),
    (19, "COMBO-05", "도덕 교리 — 본질적 악과 사목적 식별 (콤보)", "LOOP",
     ["CDF-RESPONSUM"], ["FIDUCIA-SUPPLICANS"]),
    (20, "COL-015", "믿음의 구원 필수성 vs 무지 중 구원", "DEFENDED",
     ["CCC-161_165"], ["LG-16"]),
    (21, "COL-016", "교회법 915조 vs Amoris Laetitia 8장", "LOOP",
     ["교회법-915"], ["AMORIS-LAETITIA-CH8"]),
    (22, "COL-017", "유아 세례의 필요성 vs 세례 없이 죽은 유아", "DEFENDED",
     ["CCC-1250", "CCC-1257"], ["CCC-1261", "ITC-LIMBO-2007"]),
    (23, "COL-018", "로마 수위권의 기원 서사 (325→1215)", "LOOP",
     ["COUNCIL-LATERAN_IV-C5"], ["COUNCIL-NICAEA-C6"]),
    (24, "COL-019", "공의회 우위론 vs 교황 무류·수위권", "LOOP",
     ["COUNCIL-CONSTANCE-HAEC_SANCTA"], ["VAT1-PASTOR-AETERNUS"]),
]

VERDICT_COLOR = {
    "IMPLOSION": "#e74c3c",     # 빨강 — 미해소 모순 확정
    "LOOP": "#f39c12",          # 주황 — 논쟁 지속
    "DEFENDED": "#27ae60",      # 초록 — 방어 성립
    "WITHDRAWN": "#7f8c8d",     # 회색 — 기소 철회 (우리 측 근거 결함)
    "OUT_OF_SCOPE": "#34495e",  # 짙은 회청 — 관할 밖
}
VERDICT_KR = {
    "IMPLOSION": "💥 미해소 모순", "LOOP": "🔄 논쟁 지속",
    "DEFENDED": "🛡️ 방어 성립", "WITHDRAWN": "❌ 기소 철회", "OUT_OF_SCOPE": "⛔ 관할 밖",
}

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
    tip = f"<b>[{idx}] {code}: {title}</b><br>판정(v10): {VERDICT_KR[verdict]}<br>정식보고서 v10 항목 {idx}번 참조"
    if code.startswith("COMBO") and (len(sides_a) > 1 or len(sides_b) > 1):
        combo_node = code
        add_node(combo_node, is_combo=True)
        for d in sides_a + sides_b:
            add_node(d)
            edges.append({"from": combo_node, "to": d,
                          "color": {"color": VERDICT_COLOR[verdict]}, "value": 3, "title": tip})
    else:
        for a in sides_a:
            add_node(a)
            for b in sides_b:
                add_node(b)
                edges.append({"from": a, "to": b,
                              "color": {"color": VERDICT_COLOR[verdict]}, "value": 4, "title": tip})

nodes_list = list(nodes.values())
from collections import Counter
tally = Counter(v for _, _, _, v, _, _ in ITEMS)

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>가톨릭 문헌 정합성 네트워크 v2 (CVCAP 3.0 · v10 판정 24건)</title>
<script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; padding:0; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; background:#1a1a1a; }}
  #header {{ padding:15px 20px; background:#2c3e50; color:#fff; box-shadow:0 2px 5px rgba(0,0,0,.5); position:absolute; z-index:10; border-radius:5px; margin:20px; max-width:440px; }}
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
  <h1>🛡️ The Catholic Audit — 문헌 정합성 네트워크 v2</h1>
  <p>CVCAP 3.0 정식 절차(OODA 10라운드 + 적대 재심리 2회)를 완주한 <b>24개 항목</b>을 v10 재분류 판정으로 표시합니다.<br>
  원(●)은 개별 문헌, 사각형(■)은 콤보 카드. 선 색이 판정입니다 — 마우스를 올리면 상세가 표시됩니다.<br>
  전체 논증·판결문은 <code>catholic_error_report_v10_final.md</code> 참조.</p>
</div>
<div id="legend">
  <div><span class="dot" style="background:#e74c3c;"></span>💥 미해소 모순 ({tally['IMPLOSION']}건)</div>
  <div><span class="dot" style="background:#f39c12;"></span>🔄 논쟁 지속 ({tally['LOOP']}건)</div>
  <div><span class="dot" style="background:#27ae60;"></span>🛡️ 방어 성립 ({tally['DEFENDED']}건)</div>
  <div><span class="dot" style="background:#7f8c8d;"></span>❌ 기소 철회 ({tally['WITHDRAWN']}건)</div>
  <div><span class="dot" style="background:#34495e;"></span>⛔ 관할 밖 ({tally['OUT_OF_SCOPE']}건)</div>
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
print("Nodes:", len(nodes_list), "Edges:", len(edges), "| Tally:", dict(tally))
