import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 비밀번호 설정
PASSWORD = "jelso0428"

# 비밀번호 입력
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.header("🔒 로그인")
    pwd = st.text_input("비밀번호를 입력하세요:", type='password')
    if st.button("로그인"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# Google Sheets 연동
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

sheet = gc.open("psych-scales").worksheet("Scales")

# 검사 목록 가져오기
data = sheet.get_all_records()

# 타이틀
st.title("📝 심리검사 포털")

# 검사 선택 및 실행
st.subheader("검사 목록")
for entry in data:
    name, url = entry['name'], entry['url']
    if st.button(f"🔹 {name}", key=f"start_{name}"):
        st.session_state.selected_url = url

# 선택된 검사 바로가기 (강조된 큰 버튼)
if 'selected_url' in st.session_state:
    st.divider()
    st.markdown(f"### ✅ 선택한 검사로 이동하기")
    st.link_button("👉 검사를 시작하려면 여기를 클릭하세요", st.session_state.selected_url, use_container_width=True)

# 기존 검사 삭제 기능
st.divider()
st.subheader("🔧 기존 검사 삭제하기")
delete_name = st.selectbox("삭제할 검사 선택", [entry['name'] for entry in data])
if st.button("선택한 검사 삭제"):
    cell = sheet.find(delete_name)
    sheet.delete_row(cell.row)
    st.success(f"'{delete_name}' 검사가 삭제되었습니다.")
    st.experimental_rerun()

# 새로운 검사 추가 기능
st.subheader("➕ 새 검사 추가하기")
new_name = st.text_input("검사 이름")
new_url = st.text_input("검사 URL")

if st.button("새 검사 추가"):
    if new_name and new_url:
        sheet.append_row([new_name, new_url])
        st.success(f"'{new_name}' 검사가 추가되었습니다.")
        st.experimental_rerun()
    else:
        st.error("검사 이름과 URL을 모두 입력해 주세요.")
