PYTHON ?= python3

.PHONY: help smoke-test full-run lint-skills skill skill-interactive

help:
	@echo "Available targets:"
	@echo "  make smoke-test   - Run workflow smoke test"
	@echo "  make full-run     - Generate GPT-5.6 full example report"
	@echo "  make lint-skills  - Check skills docs style consistency"
	@echo "  make skill        - Call workflow with slash-style command"
	@echo "  make skill-interactive - Interactive slash command mode"

smoke-test:
	$(PYTHON) scripts/run_external_model_workflow_smoke_test.py

full-run:
	$(PYTHON) scripts/run_external_model_workflow_gpt56_full.py

lint-skills:
	$(PYTHON) scripts/check_external_model_skills_style.py

CMD ?= /model-report GPT-5.6

skill:
	$(PYTHON) scripts/call_external_model_skill.py '$(CMD)'

skill-interactive:
	$(PYTHON) scripts/call_external_model_skill.py --interactive
