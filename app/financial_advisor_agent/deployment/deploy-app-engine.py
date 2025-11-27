import os
import random
import time
import vertexai
from vertexai import agent_engines

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")

if not PROJECT_ID:
    raise ValueError("⚠️ Please set google cloud project id in the environment variable GOOGLE_CLOUD_PROJECT")

print(f"✅ Project ID set to: {PROJECT_ID}")

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)
