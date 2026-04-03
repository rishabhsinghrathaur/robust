PYTHON ?= python3

.PHONY: backend ai dashboard check

backend:
	cd backend && uvicorn src.main:app --reload --port 8000

ai:
	cd ai && uvicorn app.main:app --reload --port 8100

dashboard:
	cd dashboard && npm run dev

check:
	$(PYTHON) -m py_compile backend/src/main.py ai/app/main.py

