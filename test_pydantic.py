import pydantic
from pydantic import BaseModel
from typing import Optional

print(f"Pydantic version: {pydantic.VERSION}")

class TestModel(BaseModel):
    name: Optional[str] = None

model = TestModel(name="test")

try:
    print(f"model.dict(): {model.dict()}")
except Exception as e:
    print(f"model.dict() failed: {e}")

try:
    print(f"model.model_dump(): {model.model_dump()}")
except Exception as e:
    print(f"model.model_dump() failed: {e}")
