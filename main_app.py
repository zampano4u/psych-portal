import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 인증정보 불러오기
credentials_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 구글 인증
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

# Google Sheets 로드
sheet = gc.open("psych-scales").worksheet("Scales")  # 정확한 시트명과 워크시트명 확인 필수

# 데이터 불러오기 함수
def load_data():
    return sheet.get_all_records()

# 데이터 저장 함수
def save_data(scales_data):
    sheet.clear()
    sheet.append_row(["name", "url"])
    for entry in scales_data:
        sheet.append_row([entry["name"], entry["url"]])

# 최초 데이터 로드
data = load_data()

st.title("🔖 심리검사 포털")

# 각 검사를 선택할 수 있는 버튼 생성 (중복 방지)
for entry in data:
    name = entry["name"]
    url = entry["url"]
    if st.button(f"{name} 시작하기", key=f"start_{name}"):
        st.link_button(f"{name} 열기", url)

st.divider()

# 검사 추가 및 삭제 섹션
st.header("⚙️ 검사 관리하기")

# 신규 검사 추가
with st.form("add_scale_form"):
    new_scale_name = st.text_input("추가할 검사 이름")
    new_scale_url = st.text_input("추가할 검사 URL")
    submit_add = st.form_submit_button("검사 추가")

    if submit_add:
        if new_scale_name and new_scale_url:
            data.append({"name": new_scale_name, "url": new_scale_url})
            save_data(data)
            st.success(f"{new_scale_name} 검사가 추가되었습니다.")
            st.rerun()
        else:
            st.error("검사 이름과 URL을 모두 입력해주세요.")

# 기존 검사 삭제
with st.form("delete_scale_form"):
    scale_names = [entry["name"] for entry in data]
    delete_scale_name = st.selectbox("삭제할 검사를 선택하세요", scale_names)
    submit_delete = st.form_submit_button("검사 삭제")

    if submit_delete:
        data = [entry for entry in data if entry["name"] != delete_scale_name]
        save_data(data)
        st.success(f"{delete_scale_name} 검사가 삭제되었습니다.")
        st.rerun()
