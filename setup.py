# setup.py
from setuptools import setup, find_packages

setup(
  name="my_assistant",
  version="0.1.0",
  package_dir={"": "src"},
  packages=find_packages(where="src"),
  install_requires=[
    "streamlit",
    "google-auth-oauthlib",
    "google-api-python-client",
    "langchain",
    "openai",
  ],
)
