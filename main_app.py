import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 🔐 비밀번호 보호 기능
def check_password():
    def password_entered():
        if st.session_state["password"] == "jelso0428":  # 비밀번호 설정
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.warning("비밀번호가 틀렸습니다.")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.text_input("접근을 위해 비밀번호를 입력하세요:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# ✅ Streamlit 기본 설정
st.set_page_config(page_title="심리검사 포털", layout="centered")
st.title("🧠 심리검사 선택 포털")

# ✅ Google Sheets 인증 (secrets 사용)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

# ✅ 시트 열기 (파일 제목 & 탭 이름 확인)
sheet = gc.open("psych-scales").worksheet("Scales")
data = sheet.get_all_records()

# ✅ 검사 목록 버튼 출력
st.subheader("📝 사용할 평가 도구를 선택하세요:")
for entry in data:
    name = entry['name']
    url = entry['url']
    if st.button(f"{name} 시작하기"):
        st.markdown(f"[👉 {name}로 이동하기]({url})", unsafe_allow_html=True)

# ✅ 평가도구 추가 기능
with st.expander("➕ 새로운 평가 도구 추가"):
    new_name = st.text_input("검사 이름")
    new_url = st.text_input("검사 URL")
    if st.button("추가하기"):
        if new_name and new_url:
            sheet.append_row([new_name, new_url])
            st.success("새 검사 도구가 추가되었습니다! 페이지를 새로고침해 주세요.")
        else:
            st.warning("검사 이름과 URL을 모두 입력해 주세요.")

