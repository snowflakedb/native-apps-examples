from streamlit.testing.v1 import AppTest

at = AppTest.from_file("ui.py")
at.run_streamlit()

assert not at.exception
