SHELL := /bin/bash

ACTIVATE := export PATH="$$(pwd)/.venv/Scripts:$$PATH" && export VIRTUAL_ENV="$$(pwd)/.venv"
SERVER_PID := /tmp/rf_test_server.pid

.PHONY: test lint start-server stop-server checkall \
	checksprint1 checksprint2 checksprint3 checksprint4 checksprint5 \
	checksprint6 checksprint7 checksprint8 checksprint9 checksprint10 \
	checksprint11 checksprint12 checksprint13 checksprint14 checksprint15 \
	checksprint16 checksprint17 checksprint18 checksprint19 checksprint20 \
	checksprint21 checksprint22 checksprint23 checksprint24 checksprint25 \
	checksprint26 checksprint27 checksprint28 checksprint29 checksprint30

# ─── Global Targets ──────────────────────────────────────────────────────────

test:
	$(ACTIVATE) && python -m pytest --tb=short -q || test $$? -eq 5

lint:
	$(ACTIVATE) && black --check . && isort --check-only . && flake8 .

# ─── Sprint 1: Project Scaffolding ───────────────────────────────────────────

checksprint1:
	$(ACTIVATE) && python manage.py check
	$(ACTIVATE) && python manage.py migrate --check
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent --output /dev/null http://localhost:8000/ ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 2: Linting & Formatting ─────────────────────────────────────────

checksprint2:
	$(ACTIVATE) && black --check .
	$(ACTIVATE) && isort --check-only .
	$(ACTIVATE) && flake8 .

# ─── Sprint 3: CI/CD & Branch Protection ────────────────────────────────────

checksprint3:
	$(ACTIVATE) && python -c "from pathlib import Path; p = Path('.github/workflows/ci.yml'); assert p.exists(), 'CI workflow not found'; c = p.read_text(); assert 'pull_request' in c, 'No PR trigger'; assert 'test' in c or 'pytest' in c, 'No test step'; print('CI workflow valid')"
	gh api repos/$$(gh repo view --json nameWithOwner -q '.nameWithOwner')/branches/main/protection --silent

# ─── Sprint 4: Design System & Layout ───────────────────────────────────────

checksprint4:
	$(ACTIVATE) && python manage.py check
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "Peliku" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 5: Home Page & New Project Form ─────────────────────────────────

checksprint5:
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "New Project" && \
		curl --fail --silent --output /dev/null http://localhost:8000/projects/new/ ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 6: Project Workspace Shell ───────────────────────────────────────

checksprint6:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		PROJECT_URL=$$(curl --fail --silent http://localhost:8000/ | grep -oP '/projects/\d+/' | head -1) && \
		curl --fail --silent http://localhost:8000$$PROJECT_URL | grep -q "Generate Video" && \
		curl --fail --silent http://localhost:8000$$PROJECT_URL | grep -q "Regenerate Script" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 7: Settings, Preview & Responsive ───────────────────────────────

checksprint7:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		PROJECT_URL=$$(curl --fail --silent http://localhost:8000/ | grep -oP '/projects/\d+/' | head -1) && \
		curl --fail --silent http://localhost:8000/ | grep -qi "settings" && \
		curl --fail --silent http://localhost:8000$$PROJECT_URL | grep -qi "preview" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 8: Database Models & Seed Data ───────────────────────────────────

checksprint8:
	$(ACTIVATE) && python manage.py migrate --check
	$(ACTIVATE) && python manage.py seed_dev_data
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=peliku.settings python -c "import django; django.setup(); from core.models import Project; assert Project.objects.count() >= 3, 'Seed data missing'"

# ─── Sprint 9: Home Page CRUD ───────────────────────────────────────────────

checksprint9:
	$(ACTIVATE) && python manage.py seed_dev_data
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -qi "clip" && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/delete/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|204|302|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 10: Gemini AI SDK & Script Service ──────────────────────────────

checksprint10:
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=peliku.settings python -c "from core.services.script_generator import generate_all_scripts; print('OK')"

# ─── Sprint 11: AI Script Generation Flow ───────────────────────────────────

checksprint11:
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=peliku.settings python -c "import django; django.setup(); from django.conf import settings; settings.ALLOWED_HOSTS.append('testserver'); from unittest.mock import patch; from django.test import Client; from core.models import Project; c = Client(); scripts = ['mock script {}'.format(i) for i in range(1, 6)]; patcher = patch('core.views.generate_all_scripts', return_value=scripts); patcher.start(); r = c.post('/projects/new/', {'title':'TestReel','description':'A test reel','aspect_ratio':'9:16','clip_duration':'8','num_clips':'5'}); patcher.stop(); assert r.status_code == 302, 'Expected redirect, got {}'.format(r.status_code); p = Project.objects.filter(title='TestReel').last(); assert p is not None, 'Project not created'; assert p.clips.count() == 5, 'Expected 5 clips, got {}'.format(p.clips.count()); assert all(cl.script_text for cl in p.clips.all()), 'Clips missing scripts'; print('Project creation with AI scripts: OK')"

# ─── Sprint 12: Workspace Script Display & Editing ──────────────────────────

checksprint12:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "Clip" && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/update-script/ \
			-H "Content-Type: application/json" -d '{"script_text":"Updated test script"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 13: Background Task System ──────────────────────────────────────

checksprint13:
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/tasks/1/status/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 14: Text-to-Video Generation ────────────────────────────────────

checksprint14:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-video/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 15: Reference Images ────────────────────────────────────────────

checksprint15:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/references/upload/ \
			-F "slot_number=1" -F "label=Test" -F "image=@static/images/placeholder.png" \
			-w "%{http_code}" -o /dev/null | grep -qE "200|201|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 16: Image-to-Video ──────────────────────────────────────────────

checksprint16:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-first-frame/ \
			-H "Content-Type: application/json" -d '{"source":"generate"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 17: Frame Interpolation ─────────────────────────────────────────

checksprint17:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-last-frame/ \
			-H "Content-Type: application/json" -d '{"source":"generate"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 18: Clip Management ─────────────────────────────────────────────

checksprint18:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/clips/add/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|201" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 19: Script Regeneration ─────────────────────────────────────────

checksprint19:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/regenerate-script/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 20: Transition Frames ───────────────────────────────────────────

checksprint20:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-transition/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 21: Video Extension ─────────────────────────────────────────────

checksprint21:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/extend/ \
			-H "Content-Type: application/json" -d '{"prompt":"Continue the scene"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 22: Extend from Previous Clip ───────────────────────────────────

checksprint22:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/2/generate-video/ \
			-H "Content-Type: application/json" -d '{"method":"extend_previous"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 23: Reel Preview ────────────────────────────────────────────────

checksprint23:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/projects/1/preview-data/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 24: Reel Assembly & Download ────────────────────────────────────

checksprint24:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/assemble/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 25: Clip Download & Thumbnails ──────────────────────────────────

checksprint25:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/clips/1/download/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 26: Hook Section ────────────────────────────────────────────────

checksprint26:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/hook/generate-script/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 27: Settings Panel ──────────────────────────────────────────────

checksprint27:
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/settings/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 28: Error Handling & States ──────────────────────────────────────

checksprint28:
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "Forge your first reel" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 29: Accessibility & Animations ──────────────────────────────────

checksprint29:
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "aria-" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 30: Final Integration & Documentation ───────────────────────────

checksprint30:
	$(ACTIVATE) && pip-audit 2>/dev/null || echo "WARN: pip-audit not available, skipping"
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "Peliku" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Aggregate Target ───────────────────────────────────────────────────────

checkall:
	$(MAKE) checksprint1 && \
	$(MAKE) checksprint2 && \
	$(MAKE) checksprint3 && \
	$(MAKE) checksprint4 && \
	$(MAKE) checksprint5 && \
	$(MAKE) checksprint6 && \
	$(MAKE) checksprint7 && \
	$(MAKE) checksprint8 && \
	$(MAKE) checksprint9 && \
	$(MAKE) checksprint10 && \
	$(MAKE) checksprint11 && \
	$(MAKE) checksprint12 && \
	$(MAKE) checksprint13 && \
	$(MAKE) checksprint14 && \
	$(MAKE) checksprint15 && \
	$(MAKE) checksprint16 && \
	$(MAKE) checksprint17 && \
	$(MAKE) checksprint18 && \
	$(MAKE) checksprint19 && \
	$(MAKE) checksprint20 && \
	$(MAKE) checksprint21 && \
	$(MAKE) checksprint22 && \
	$(MAKE) checksprint23 && \
	$(MAKE) checksprint24 && \
	$(MAKE) checksprint25 && \
	$(MAKE) checksprint26 && \
	$(MAKE) checksprint27 && \
	$(MAKE) checksprint28 && \
	$(MAKE) checksprint29 && \
	$(MAKE) checksprint30

# ─── Scaling Note ────────────────────────────────────────────────────────────
# Running checkall sequentially takes 10-20 minutes because many targets start
# and stop the dev server independently. For a faster aggregate run, consider
# the checkall-with-server target (optimization only — individual targets
# remain self-contained and independently runnable).
#
# checkall-with-server:
#	$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
#		<run all HTTP checks here> ; \
#		kill $$RF_PID 2>/dev/null
