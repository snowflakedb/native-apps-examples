import streamlit as st
import spcs_helpers
from utils import basic_setup

st.set_page_config(layout="wide")


pages = {
    "Steps": [
        st.Page(
            "pages/0-welcome.py", title="Welcome ", icon=":material/arrow_forward:"
        ),
        st.Page(
            "pages/1-compute_pool.py", title="Compute Pool", icon=":material/computer:"
        ),
        st.Page(
            "pages/2-service_code.py", title="Service Code", icon=":material/code:"
        ),
        st.Page(
            "pages/3-web_endpoint_and_udf.py",
            title="Web Endpoint and Functions",
            icon=":material/public:",
        ),
        st.Page(
            "pages/4-final_review.py",
            title="Final Review",
            icon=":material/check_circle:",
        ),
    ],
    "Dashboard": [
        st.Page("list_services.py", title="Running Services", icon=":material/rocket:"),
        st.Page("list_udfs.py", title="Functions", icon=":material/functions:"),
    ],
}

basic_setup()

st.sidebar.markdown(open("logo").read(), unsafe_allow_html=True)
st.sidebar.write("### SPCS Easy Run Mode App")


pg = st.navigation(pages)
pg.run()
