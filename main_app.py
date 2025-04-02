import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# Google Sheets 설정
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Streamlit secrets에서 credentials 정보 로드
credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

# Google Sheet 열기 (정확한 제목을 확인하여 입력)
sheet = gc.open("psych-scales").worksheet("Scales")

def load_data():
    return sheet.get_all_records()

def add_scale(name, url):
    sheet.append_row([name, url])

def delete_scale(name):
    cell = sheet.find(name)
    if cell:
        sheet.delete_rows(cell.row)

# 앱 제목
st.title("🧠 심리검사 포털")

# 비밀번호 기반 접근 제어
def check_password():
    def password_entered():
        if st.session_state["password"] == "jelso0428":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.error("비밀번호가 잘못되었습니다.")

    if "password_correct" not in st.session_state:
        st.text_input("비밀번호를 입력하세요:", type="password", on_change=password_entered, key="password")
        return False
    return True

if check_password():
    data = load_data()

    # 심리검사 목록 표시
    st.write("### 📚 심리검사 목록")
    for i, entry in enumerate(data):
        name = entry['name']
        url = entry['url']
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{name}**")

        with col2:
            if st.button(f"{name} 시작하기", key=f"start_button_{i}"):
                st.switch_page(url)

    st.divider()

    # 신규 검사 추가 폼
    with st.form("new_scale_form"):
        st.write("### ➕ 새로운 심리검사 추가")
        new_name = st.text_input("검사 이름")
        new_url = st.text_input("검사 URL (Streamlit 앱 주소)")
        submitted = st.form_submit_button("추가하기")

        if submitted:
            if new_name and new_url:
                add_scale(new_name, new_url)
                st.success(f"'{new_name}' 검사가 추가되었습니다. 새로고침 하세요.")
            else:
                st.error("모든 정보를 입력해주세요.")

    # 기존 검사 삭제 UI
    st.write("### ❌ 기존 심리검사 삭제")
    del_names = [entry['name'] for entry in data]
    selected_name = st.selectbox("삭제할 검사를 선택하세요:", ["선택하세요"] + del_names)

    if st.button("선택한 검사 삭제"):
        if selected_name != "선택하세요":
            delete_scale(selected_name)
            st.success(f"'{selected_name}' 검사가 삭제되었습니다. 새로고침 하세요.")
        else:
            st.error("삭제할 검사를 선택해주세요.")
