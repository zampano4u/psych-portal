import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 비밀번호 설정
PASSWORD = "jelso0428"

if "login" not in st.session_state:
    st.session_state.login = False

# 비밀번호 입력 UI
if not st.session_state.login:
    st.title("🔐 심리검사 포털 로그인")
    user_input = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        if user_input == PASSWORD:
            st.session_state.login = True
            st.success("로그인 성공!")
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
else:
    st.title("📝 심리검사 포털")

    # Google Sheets 연동
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open("psych-scales").worksheet("Scales")

    data = sheet.get_all_records()

    # 검사 선택 UI 개선 (눈에 잘 띄도록 st.container + Markdown 사용)
    with st.container(border=True):
        st.markdown("### 📌 **심리검사 선택**")
        for entry in data:
            name = entry['name']
            url = entry['url']
            if st.button(f"🟢 {name}", key=f"start_button_{name}"):
                st.session_state.selected_url = url

    # 선택한 검사로 이동하는 링크
    if "selected_url" in st.session_state:
        st.link_button("🚀 선택한 심리검사 바로가기", st.session_state.selected_url)

    st.divider()

    # 검사 추가/삭제 UI 하단 배치
    st.markdown("## 🛠️ 검사 관리 (추가/삭제)")

    # 신규 검사 추가
    with st.expander("➕ 신규 검사 추가하기"):
        new_name = st.text_input("새로운 검사 이름 입력")
        new_url = st.text_input("새로운 검사 URL 입력")
        if st.button("추가하기"):
            if new_name and new_url:
                sheet.append_row([new_name, new_url])
                st.success(f"{new_name}이(가) 추가되었습니다.")
                st.rerun()
            else:
                st.warning("모든 필드를 입력해주세요.")

    # 기존 검사 삭제
    with st.expander("🗑️ 기존 검사 삭제하기"):
        names = [entry['name'] for entry in data]
        delete_name = st.selectbox("삭제할 검사 선택", names)
        if st.button("삭제하기"):
            if delete_name:
                cell = sheet.find(delete_name)
                sheet.delete_rows(cell.row)
                st.success(f"{delete_name}이(가) 삭제되었습니다.")
                st.rerun()
            else:
                st.warning("삭제할 검사를 선택해주세요.")
