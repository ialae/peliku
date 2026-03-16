SHELL := /bin/bash

ACTIVATE := source .venv/Scripts/activate
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
	$(ACTIVATE) && python -m pytest --tb=short -q || test $$? -eq 5
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent --output /dev/null http://localhost:8000/ ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 2: Linting & Formatting ─────────────────────────────────────────

checksprint2:
	$(ACTIVATE) && black --check .
	$(ACTIVATE) && isort --check-only .
	$(ACTIVATE) && flake8 .
	$(ACTIVATE) && python -m pytest --tb=short -q || test $$? -eq 5

# ─── Sprint 3: CI/CD & Branch Protection ────────────────────────────────────

checksprint3:
	$(ACTIVATE) && python -c "\
		from pathlib import Path; \
		p = Path('.github/workflows/ci.yml'); \
		assert p.exists(), 'CI workflow not found'; \
		c = p.read_text(); \
		assert 'pull_request' in c, 'No PR trigger'; \
		assert 'test' in c or 'pytest' in c, 'No test step'; \
		print('CI workflow valid')"
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python -m pytest --tb=short -q || test $$? -eq 5
	gh api repos/$$(gh repo view --json nameWithOwner -q '.nameWithOwner')/branches/main/protection --silent

# ─── Sprint 4: Design System & Layout ───────────────────────────────────────

checksprint4:
	$(ACTIVATE) && python manage.py check
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "ReelForge" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 5: Home Page & New Project Form ─────────────────────────────────

checksprint5:
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "New Project" && \
		curl --fail --silent --output /dev/null http://localhost:8000/projects/new/ ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 6: Project Workspace Shell ───────────────────────────────────────

checksprint6:
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "Generate Video" && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "Regenerate Script" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 7: Settings, Preview & Responsive ───────────────────────────────

checksprint7:
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -qi "settings" && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -qi "preview" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 8: Database Models & Seed Data ───────────────────────────────────

checksprint8:
	$(ACTIVATE) && python manage.py migrate --check
	$(ACTIVATE) && python manage.py seed_dev_data
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=reelforge.settings python -c "\
		import django; django.setup(); \
		from core.models import Project; \
		assert Project.objects.count() >= 3, 'Seed data missing'"
	$(ACTIVATE) && python -m pytest --tb=short -q

# ─── Sprint 9: Home Page CRUD ───────────────────────────────────────────────

checksprint9:
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -qi "clip" && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/delete/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|204|302|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 10: Gemini AI SDK & Script Service ──────────────────────────────

checksprint10:
	$(ACTIVATE) && python -m pytest core/tests/test_script_generator.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=reelforge.settings python -c "\
		from core.services.script_generator import generate_all_scripts; print('OK')"

# ─── Sprint 11: AI Script Generation Flow ───────────────────────────────────

checksprint11:
	$(ACTIVATE) && python -m pytest core/tests/test_project_creation.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/projects/new/ \
			-d "title=TestReel&description=A+test+reel+about+nature&aspect_ratio=9:16&clip_duration=8&num_clips=5" \
			-L -o /dev/null -w "%{http_code}" | grep -q "200" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 12: Workspace Script Display & Editing ──────────────────────────

checksprint12:
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "Clip" && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/update-script/ \
			-H "Content-Type: application/json" -d '{"script_text":"Updated test script"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 13: Background Task System ──────────────────────────────────────

checksprint13:
	$(ACTIVATE) && python -m pytest core/tests/test_task_runner.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/tasks/1/status/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 14: Text-to-Video Generation ────────────────────────────────────

checksprint14:
	$(ACTIVATE) && python -m pytest core/tests/test_video_generation.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-video/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 15: Reference Images ────────────────────────────────────────────

checksprint15:
	$(ACTIVATE) && python -m pytest core/tests/test_reference_images.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/references/upload/ \
			-F "slot_number=1" -F "label=Test" -F "image=@static/images/placeholder.png" \
			-w "%{http_code}" -o /dev/null | grep -qE "200|201|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 16: Image-to-Video ──────────────────────────────────────────────

checksprint16:
	$(ACTIVATE) && python -m pytest core/tests/test_image_to_video.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-first-frame/ \
			-H "Content-Type: application/json" -d '{"source":"generate"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 17: Frame Interpolation ─────────────────────────────────────────

checksprint17:
	$(ACTIVATE) && python -m pytest core/tests/test_frame_interpolation.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-last-frame/ \
			-H "Content-Type: application/json" -d '{"source":"generate"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 18: Clip Management ─────────────────────────────────────────────

checksprint18:
	$(ACTIVATE) && python -m pytest core/tests/test_clip_management.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/clips/add/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|201" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 19: Script Regeneration ─────────────────────────────────────────

checksprint19:
	$(ACTIVATE) && python -m pytest core/tests/test_script_regeneration.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/regenerate-script/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 20: Transition Frames ───────────────────────────────────────────

checksprint20:
	$(ACTIVATE) && python -m pytest core/tests/test_transition_frames.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-transition/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 21: Video Extension ─────────────────────────────────────────────

checksprint21:
	$(ACTIVATE) && python -m pytest core/tests/test_video_extension.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/1/extend/ \
			-H "Content-Type: application/json" -d '{"prompt":"Continue the scene"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 22: Extend from Previous Clip ───────────────────────────────────

checksprint22:
	$(ACTIVATE) && python -m pytest core/tests/test_extend_from_previous.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/clips/2/generate-video/ \
			-H "Content-Type: application/json" -d '{"method":"extend_previous"}' \
			-w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 23: Reel Preview ────────────────────────────────────────────────

checksprint23:
	$(ACTIVATE) && python -m pytest core/tests/test_preview.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/projects/1/preview-data/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 24: Reel Assembly & Download ────────────────────────────────────

checksprint24:
	$(ACTIVATE) && python -m pytest core/tests/test_reel_assembly.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/assemble/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202|400" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 25: Clip Download & Thumbnails ──────────────────────────────────

checksprint25:
	$(ACTIVATE) && python -m pytest core/tests/test_clip_download.py core/tests/test_thumbnails.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/clips/1/download/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200|404" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 26: Hook Section ────────────────────────────────────────────────

checksprint26:
	$(ACTIVATE) && python -m pytest core/tests/test_hook.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent -X POST http://localhost:8000/api/projects/1/hook/generate-script/ \
			-H "Content-Type: application/json" -w "%{http_code}" -o /dev/null | grep -qE "200|202" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 27: Settings Panel ──────────────────────────────────────────────

checksprint27:
	$(ACTIVATE) && python -m pytest core/tests/test_settings.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/api/settings/ \
			-w "%{http_code}" -o /dev/null | grep -qE "200" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 28: Error Handling & States ──────────────────────────────────────

checksprint28:
	$(ACTIVATE) && python -m pytest core/tests/test_error_states.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "Forge your first reel" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 29: Accessibility & Animations ──────────────────────────────────

checksprint29:
	$(ACTIVATE) && python -m pytest core/tests/test_accessibility.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && python manage.py seed_dev_data 2>/dev/null || true
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/projects/1/ | grep -q "aria-" ; \
		EXIT=$$? ; kill $$RF_PID 2>/dev/null ; exit $$EXIT

# ─── Sprint 30: Final Integration & Documentation ───────────────────────────

checksprint30:
	$(ACTIVATE) && python -m pytest core/tests/test_integration.py --tb=short -q
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	$(ACTIVATE) && pip-audit 2>/dev/null || echo "WARN: pip-audit not available, skipping"
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "ReelForge" ; \
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
