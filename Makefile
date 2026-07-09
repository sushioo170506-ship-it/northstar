PYTHON ?= python3

.PHONY: help smoke-test full-run lint-skills

help:
	@echo "Available targets:"
	@echo "  make smoke-test   - Run workflow smoke test"
	@echo "  make full-run     - Generate GPT-5.6 full example report"
	@echo "  make lint-skills  - Check skills docs style consistency"

smoke-test:
	$(PYTHON) scripts/run_external_model_workflow_smoke_test.py

full-run:
	$(PYTHON) scripts/run_external_model_workflow_gpt56_full.py

lint-skills:
	$(PYTHON) scripts/check_external_model_skills_style.py
