import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 비밀번호 인증
PASSWORD = "jelso0428"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if password == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()  # 최신버전 Streamlit
    else:
        st.stop()

# Google Sheets 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["GOOGLE_CREDENTIALS"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(dict(credentials_dict), scope)
gc = gspread.authorize(credentials)
sheet = gc.open("psych-scales").worksheet("Scales")

# 심리검사 목록 불러오기
data = sheet.get_all_records()
scales = {entry['name']: entry['url'] for entry in data}

st.title("🧠 심리검사 포털")

st.markdown("원하는 심리검사를 아래에서 선택하세요:")

selected_test = None
for name, url in scales.items():
    if st.button(f"🟢 {name}", key=f"start_button_{name}"):
        selected_test = name
        st.session_state.selected_url = url
        st.session_state.selected_name = name

# 선택 결과 표시
if "selected_url" in st.session_state and "selected_name" in st.session_state:
    st.success(f"선택된 검사: {st.session_state.selected_name}")
    st.markdown("---")
    st.page_link(st.session_state.selected_url, label=f"{st.session_state.selected_name} 바로가기", icon="🧪")

st.markdown("---")
st.subheader("🔧 심리검사 추가 또는 삭제")

# 검사 추가 UI
with st.form("add_form"):
    new_name = st.text_input("새 검사 이름")
    new_url = st.text_input("새 검사 URL")
    submitted = st.form_submit_button("검사 추가")
    if submitted:
        if new_name and new_url:
            if new_name not in scales:
                sheet.append_row([new_name, new_url])
                st.success(f"{new_name}이(가) 추가되었습니다.")
                st.rerun()
            else:
                st.warning("이미 존재하는 검사입니다.")
        else:
            st.error("검사 이름과 URL을 모두 입력하세요.")

# 검사 삭제 UI
with st.form("delete_form"):
    delete_name = st.selectbox("삭제할 검사 선택", options=list(scales.keys()))
    delete_submit = st.form_submit_button("검사 삭제")
    if delete_submit:
        cell = sheet.find(delete_name)
        if cell:
            sheet.delete_rows(cell.row)
            st.success(f"{delete_name}이(가) 삭제되었습니다.")
            st.rerun()
        else:
            st.error("해당 검사를 찾을 수 없습니다.")
