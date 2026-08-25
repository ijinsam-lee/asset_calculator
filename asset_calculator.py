import streamlit as st
import pandas as pd
import altair as alt
import os
import urllib.request
from fpdf import FPDF

# 페이지 기본 설정
st.set_page_config(
    page_title="복리의 마법 & 미래 자산 계산기",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* 글로벌 배경화면 및 메인 톤 조정 */
.stApp {
    background-color: #f8fafc;
}

/* 헤더 및 타이틀 컴포넌트 커스텀 */
.main-header {
    text-align: center;
    padding: 10px 0 20px 0;
}
.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}
.main-caption {
    font-size: 0.95rem;
    color: #475569;
    line-height: 1.5;
}

/* 입력 컨트롤 패널 스타일 */
.control-panel {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    margin-bottom: 24px;
}

/* 프리셋 버튼 커스텀 스타일 */
.stButton>button {
    width: 100%;
    border-radius: 8px !important;
    font-weight: 700 !important;
    background-color: #f1f5f9 !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border-color: #1e293b !important;
}

/* Metric 카드 스타일링 */
[data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

def format_krw(val: float) -> str:
    """
    한국 원화 표기에 최적화된 억/만원 화폐 단위 변환 헬퍼 함수 (음수 지원)
    """
    sign = "-" if val < 0 else ""
    val = abs(val)
    if val == 0:
        return "0원"
    if val >= 100000000:
        eok = int(val // 100000000)
        man = int((val % 100000000) // 10000)
        if man > 0:
            return f"{sign}{eok}억 {man:,}만원"
        return f"{sign}{eok}억원"
    else:
        man = int(val // 10000)
        return f"{sign}{man:,}만원"

@st.cache_data
def generate_pdf_report(calc_init, calc_monthly, calc_expense, calc_years, calc_cagr, calc_inflation, tax_rate, last_rec, df_records):
    """
    한글 폰트를 지원하는 PDF 보고서 생성 함수
    """
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            pass

    pdf = FPDF()
    pdf.add_page()
    
    has_korean = os.path.exists(font_path)
    if has_korean:
        pdf.add_font("NanumGothic", "", font_path)
        pdf.set_font("NanumGothic", size=16)
    else:
        pdf.set_font("Helvetica", style="B", size=16)

    # 문서 제목
    pdf.cell(0, 12, "미래 자산 시뮬레이션 최종 성과 리포트", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    # 조건 요약
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=11)
    pdf.cell(0, 8, "[1] 주요 시뮬레이션 설정 조건", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=10)
    
    pdf.cell(0, 6, f" - 초기 투자금: {calc_init:,} 만원", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 매월 저축/적립금: {calc_monthly:,} 만원", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 매월 지출/생활비: {calc_expense:,} 만원", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 시뮬레이션 기간: {calc_years} 년", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 연 목표 수익률 (CAGR): {calc_cagr}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 연 예상 물가상승률: {calc_inflation}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 적용 세율: {tax_rate}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 최종 결과 요약
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=11)
    pdf.cell(0, 8, "[2] 최종 기대 성과 요약", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=10)

    pdf.cell(0, 6, f" - 총 순 원금 (저축-지출): {format_krw(last_rec['누적 납입원금'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 세후 최종 자산: {format_krw(last_rec['세후 수령예정액'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f" - 실질구매력 가치 (물가반영): {format_krw(last_rec['세후 실질가치 (물가반영)'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 연도별 세부 테이블
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=11)
    pdf.cell(0, 8, "[3] 연도별 세부 자산 성장 상세표", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("NanumGothic" if has_korean else "Helvetica", size=9)

    col_widths = [20, 42, 42, 42, 44]
    headers = ["년차", "누적 납입원금", "세전 일반복리", "세후 수령예정액", "실질가치(물가반영)"]
    
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 7, h, border=1, align="C")
    pdf.ln()

    for _, row in df_records.iterrows():
        pdf.cell(col_widths[0], 6, str(row["년차"]), border=1, align="C")
        pdf.cell(col_widths[1], 6, format_krw(row["누적 납입원금"]), border=1, align="R")
        pdf.cell(col_widths[2], 6, format_krw(row["세전 일반복리"]), border=1, align="R")
        pdf.cell(col_widths[3], 6, format_krw(row["세후 수령예정액"]), border=1, align="R")
        pdf.cell(col_widths[4], 6, format_krw(row["세후 실질가치 (물가반영)"]), border=1, align="R")
        pdf.ln()

    return bytes(pdf.output())

st.markdown("""
<div class="main-header">
    <div class="main-title">🧮 복리의 마법 & 미래 자산 계산기</div>
    <div class="main-caption">
        목표 연평균 수익률(CAGR), 적립식 저축액, 정기 생활비 지출, 인플레이션 및 과세 조건을 종합하여<br>
        실제 손에 쥐게 될 미래 자산과 실질 구매력을 정밀하게 예측해 드립니다.
    </div>
</div>
""", unsafe_allow_html=True)

# CAGR 프리셋 조절용 세션 스테이트 초기화
if "cagr_input" not in st.session_state:
    st.session_state.cagr_input = 38.7

st.markdown("##### ⚡ 동적 자산배분 주요 전략 실측 CAGR 퀵 프리셋")
col_pre1, col_pre2, col_pre3, col_pre4 = st.columns(4)

if col_pre1.button("🏆 혼합전략 (38.7%)"):
    st.session_state.cagr_input = 38.7
    st.rerun()
if col_pre2.button("🛡️ 안정형 (27.3%)"):
    st.session_state.cagr_input = 27.3
    st.rerun()
if col_pre3.button("⚡ 공격형 (36.4%)"):
    st.session_state.cagr_input = 36.4
    st.rerun()
if col_pre4.button("🔄 로테이션 (46.7%)"):
    st.session_state.cagr_input = 46.7
    st.rerun()

st.markdown("---")

col_inp1, col_inp2 = st.columns(2)

with col_inp1:
    calc_init = st.number_input("초기 투자금 (만원 ₩)", min_value=0, value=2000, step=100)
    calc_monthly = st.number_input("매월 저축/적립금 (만원 ₩)", min_value=0, value=100, step=10)
    calc_expense = st.number_input(
        "매월 지출/생활비 (만원 ₩)", 
        min_value=0, 
        value=0, 
        step=10, 
        help="투자 자산에서 매월 인출하여 정기 지출할 금액이 있다면 설정합니다."
    )
    calc_years = st.slider("시뮬레이션 투자 기간 (년)", min_value=1, max_value=40, value=15)

with col_inp2:
    calc_cagr = st.number_input("연 목표 수익률 CAGR (%)", min_value=0.0, max_value=100.0, key="cagr_input", step=0.1)
    calc_inflation = st.number_input("연 예상 물가상승률 (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.1)
    calc_expense_start = st.number_input(
        "지출 시작 시점 (년차)", 
        min_value=1, 
        max_value=max(1, calc_years), 
        value=1, 
        step=1, 
        help="생활비 지출을 몇 년차부터 적용할지 지정합니다."
    )
    calc_tax_opt = st.selectbox(
        "세율 설정", 
        ["일반과세 (15.4%)", "미국주식양도세 (22.0%)", "비과세 계좌 (0.0% / ISA 및 연금저축)", "사용자 정의"]
    )

if calc_tax_opt == "일반과세 (15.4%)":
    tax_rate = 15.4
elif calc_tax_opt == "미국주식양도세 (22.0%)":
    tax_rate = 22.0
elif calc_tax_opt == "비과세 계좌 (0.0% / ISA 및 연금저축)":
    tax_rate = 0.0
else:
    tax_rate = st.number_input("세율 직접 입력 (%)", min_value=0.0, max_value=50.0, value=15.4, step=0.1)

records = []
curr_nominal = calc_init * 10000
curr_contribution = calc_init * 10000
monthly_contrib = calc_monthly * 10000
base_expense = calc_expense * 10000
r_monthly = (1 + calc_cagr / 100) ** (1/12) - 1 if calc_cagr > 0 else 0.0

for y in range(1, calc_years + 1):
    # 년차별 생활비 인플레이션 반영
    current_year_monthly_expense = base_expense * ((1 + calc_inflation / 100) ** (y - 1)) if y >= calc_expense_start else 0.0
    
    # 12개월간 적립/지출 및 월 복리 계산
    for m in range(12):
        net_flow = monthly_contrib - current_year_monthly_expense
        curr_contribution += net_flow
        curr_nominal = (curr_nominal + net_flow) * (1 + r_monthly)
        
        if curr_nominal < 0:
            curr_nominal = 0.0

    # 과세 및 물가상승률 할인 계산
    effective_contribution = max(0.0, curr_contribution)
    profit = curr_nominal - effective_contribution
    tax_due = profit * (tax_rate / 100) if profit > 0 else 0.0
    curr_after_tax = curr_nominal - tax_due
    real_value = curr_after_tax / ((1 + calc_inflation / 100) ** y)
    
    records.append({
        "년차": f"{y}년차",
        "누적 납입원금": round(curr_contribution),
        "세전 일반복리": round(curr_nominal),
        "세후 수령예정액": round(curr_after_tax),
        "세후 실질가치 (물가반영)": round(real_value)
    })

df_calc = pd.DataFrame(records)
last_rec = records[-1]

st.markdown("### 🏆 시뮬레이션 최종 기대 성과 요약")

sum_col1, sum_col2, sum_col3 = st.columns(3)
sum_col1.metric("총 순 원금(저축-지출)", format_krw(last_rec["누적 납입원금"]))
sum_col2.metric("세후 최종 자산", format_krw(last_rec["세후 수령예정액"]))
sum_col3.metric("실질구매력 가치", format_krw(last_rec["세후 실질가치 (물가반영)"]))

# PDF 생성 및 다운로드 버튼
pdf_data = generate_pdf_report(
    calc_init, calc_monthly, calc_expense, calc_years, 
    calc_cagr, calc_inflation, tax_rate, last_rec, df_calc
)

st.download_button(
    label="📄 시뮬레이션 결과 PDF 리포트 다운로드",
    data=pdf_data,
    file_name=f"asset_simulation_report_{calc_years}years.pdf",
    mime="application/pdf",
    use_container_width=True
)

st.markdown("### 📈 미래 자산 성장 시뮬레이션")
df_melt = df_calc.melt(
    id_vars="년차", 
    value_vars=["누적 납입원금", "세전 일반복리", "세후 수령예정액", "세후 실질가치 (물가반영)"], 
    var_name="구분", 
    value_name="자산액"
)

try:
    line_chart = alt.Chart(df_melt).mark_line(point=True, size=2.5).encode(
        x=alt.X("년차:N", sort=None, title="년차"),
        y=alt.Y("자산액:Q", title="평가액 (₩)"),
        color=alt.Color("구분:N", scale=alt.Scale(range=["#94a3b8", "#ef4444", "#10b981", "#3b82f6"])),
        tooltip=[alt.Tooltip("년차"), alt.Tooltip("구분"), alt.Tooltip("자산액", format=",.0f")]
    ).properties(height=360)
    st.altair_chart(line_chart, use_container_width=True)
except Exception:
    st.line_chart(df_calc.set_index("년차"))

# 세부 연도별 자산 성장 데이터표 출력
st.markdown("### 📊 연도별 세부 자산 성장 상세표")
df_display = df_calc.copy()
for col in ["누적 납입원금", "세전 일반복리", "세후 수령예정액", "세후 실질가치 (물가반영)"]:
    df_display[col] = df_display[col].apply(format_krw)

st.dataframe(df_display, use_container_width=True, hide_index=True)
