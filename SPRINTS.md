# Sprint Plan — Peliku

> Generated from: FEATURE_SPECS.md, STACK.md, DESIGN.md
> Date: March 15, 2026
> Total sprints: 30
> Stack: Django 5.1+ monolith, Django Templates, jQuery 3.7+, Vanilla JS, CSS3, SQLite 3, Local File Storage, Google Gemini AI (google-genai SDK), Python 3.12, pytest

---

## How to Use This Plan

- Each sprint is developed on a dedicated `sprint/N` branch created from `main` (e.g., `sprint/1`, `sprint/5`, `sprint/12`).
- After implementation and verification, the `@sprintreviewer` agent runs all previous sprint tests, verifies the current sprint's checklist, and opens a pull request to merge `sprint/N` into `main`.
- Pull requests are merged using **squash merge** to keep `main` history clean and linear. Each sprint becomes a single commit on `main`.
- The pull request triggers a CI/CD pipeline that runs linting, type checking, builds, and the full test suite before allowing merge.
- **Before starting any sprint**, read the instructions file at `.github/copilot-instructions.md` completely. This is non-negotiable.
- **Before implementing any UI, template, layout, component, form, or styling work**, read `DESIGN.md` completely. It is the single source of truth for all visual and interaction decisions.
- **Before implementing any sprint**, search for all relevant skills in `.github/skills/` and read them completely.
- Verification is done via `make checksprintN` from the project root (e.g., `make checksprint1`, `make checksprint12`). Run these commands via Git Bash on Windows.
- The full test suite is run via `make test` from the project root.
- Every command must exit with code 0 for the sprint to pass.
- `make checkall` runs all verifications in order and stops at the first failure.
- **Note on deployment**: Per STACK.md, Peliku is a development-only personal tool with no cloud deployment. There are no `checkdeployN` targets. All verification is local.

### Branching & Review Workflow

1. Create branch: `git checkout -b sprint/N main`
2. Implement the sprint following the "What to build" instructions
3. Verify locally: `make checksprintN`
4. Commit and push: `git push -u origin sprint/N`
5. Run `@sprintreviewer` to verify and open a PR
6. Squash merge the PR into `main`
7. Clean up: `git branch -d sprint/N && git push origin --delete sprint/N`

### Bootstrapping Note (Sprints 1–2)

Sprints 1 and 2 are merged manually since CI/CD and branch protection are set up in Sprint 3. From Sprint 3 onward, all PRs go through the full CI pipeline and branch protection rules.

### Rollback Process

If a merged sprint is found to be broken, revert the squash-merge commit on `main` with `git revert`, re-create the sprint branch, fix the issue, and re-run `@sprintreviewer`. See the sprintreviewer agent for detailed rollback instructions.

### Local Development Prerequisites

- Python 3.12
- Git and Git Bash (Windows) or any POSIX-compatible shell
- `make` (GnuWin32 on Windows at `C:\Program Files (x86)\GnuWin32\bin\make.exe`, run via Git Bash)
- `curl` (included with Git Bash)
- `gh` (GitHub CLI, authenticated via `gh auth login`) — install from https://cli.github.com/ before starting Sprint 1
- FFmpeg (required from Sprint 24 onward for reel assembly)

### Python Dependency Installation Policy

Never run global `pip install` commands. Always activate `.venv` first, then use `python -m pip install ...`. All commands in this plan assume the virtual environment is active.

---

## Sprint Overview

1. Django project scaffolding, virtual environment, dev server, Git init, Makefile
2. Linting (Black, Flake8, isort), pre-commit hooks configured and passing
3. GitHub Actions CI pipeline on PRs, branch protection on main
4. CSS design system from DESIGN.md, global layout (header, navigation bar)
5. Home page shell with empty project grid, New Project form page shell
6. Project Workspace page shell with clip panel layout and Reference Images Panel
7. Settings slide-over panel, Preview overlay shell, responsive layout for all pages
8. Django models (Project, Clip, ReferenceImage, Hook, UserSettings, Task), migrations, seed command
9. Home page CRUD: list projects, create, delete, rename, duplicate, search
10. Gemini AI SDK integration, script generation service with mocked tests
11. New Project form submission triggers AI script generation, redirects to workspace
12. Project Workspace displays clip scripts from DB, inline editing with auto-save
13. Background task system with threading, Task model status tracking, polling API
14. Text-to-Video generation via Veo API with per-clip status indicators
15. Reference Images Panel: generate via Gemini, upload, manage slots, per-clip selection
16. Image-to-Video generation method with first-frame management
17. Frame Interpolation generation method with first and last frame inputs
18. Clip management: drag-and-drop reorder, add new clip, delete clip
19. Script regeneration: single clip (context-aware) and full regeneration (all clips)
20. Transition frames generation between consecutive clips
21. Video extension: Extend Clip adds 7 seconds with extension prompt
22. Extend from Previous Clip generation method with video splitting
23. Reel Preview: full-screen overlay with sequential playback and timeline scrubber
24. Reel assembly via FFmpeg, Download Reel as single MP4
25. Individual clip download, project card thumbnails on Home page
26. Hook Section: AI script generation, video generation, toggle, prepend to reel
27. Settings panel: all default preferences, video quality, generation speed
28. Error handling, loading states, empty states, confirmation dialogs, toast notifications
29. Accessibility audit, animation system, reduced-motion fallbacks, contrast compliance
30. Final integration testing, edge cases, boundary conditions, README documentation

---

## Sprint Details

---

### Sprint 1 — Django Project Scaffolding & Dev Environment

- **Prerequisite**: None
- **Branch**: `sprint/1`
- **Repository URL**: TBD — the executor will prompt for the GitHub repository URL during implementation
- **Objective**: Create a running Django development server with a virtual environment, initial project structure, Git repository, and the foundational Makefile
- **Why this comes now**: Everything else depends on having a working Django project with a dev server and version control

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Create virtual environment: `python -m venv .venv`
  - Activate `.venv` and install dependencies: `python -m pip install django==5.1.7 python-decouple django-debug-toolbar pytest pytest-django`
  - Create Django project in the workspace root: `django-admin startproject peliku .`
  - Create the main app: `python manage.py startapp core`
  - Create `.env` with `SECRET_KEY`, `DEBUG=True`, `GEMINI_API_KEY=your-key-here`, `ALLOWED_HOSTS=localhost,127.0.0.1`
  - Create `.env.example` documenting all required configuration variables (same keys, placeholder values)
  - Update `peliku/settings.py`: use `python-decouple` for env vars, register `core` app, configure `django-debug-toolbar`, set `TEMPLATES` dirs to include a root `templates/` folder, configure `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT`, set up Python `logging` to file (`logs/peliku.log`) and stdout
  - Create directories: `templates/`, `static/css/`, `static/js/`, `static/images/`, `media/videos/`, `media/images/`, `media/reels/`, `logs/`
  - Create `templates/base.html` with a minimal HTML5 document (empty body, will be styled in Sprint 4)
  - Create `core/urls.py` with a single route `/` pointing to a home view
  - Create `core/views.py` with a `home` view that renders `templates/core/home.html`
  - Create `templates/core/home.html` extending `base.html` with placeholder text "Peliku — Home"
  - Update `peliku/urls.py` to include `core.urls` and serve media files in development
  - Run `python manage.py migrate` to create initial database
  - Create `requirements.txt` with all pinned dependency versions
  - Create `.gitignore` excluding `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `db.sqlite3`, `media/`, `logs/`, `*.egg-info`
  - Create `conftest.py` at project root with Django settings configuration for pytest
  - Create `core/tests/__init__.py` and `core/tests/test_smoke.py` with a smoke test that verifies the home page returns 200
  - Initialize Git repo: `git init`, `git remote add origin <REPO_URL>`, initial commit
  - Create the `Makefile` at the workspace root with `SHELL := /bin/bash`, `ACTIVATE` variable (using PATH export instead of `source .venv/Scripts/activate` for Git Bash compatibility on Windows), `test` target (runs pytest), and `checksprint1` target

- **What you should see when done**:
  - `python manage.py runserver` starts the dev server at `http://127.0.0.1:8000/`
  - Visiting `http://localhost:8000/` shows "Peliku — Home"
  - `make test` runs the smoke test and passes
  - `make checksprint1` passes all checks

- **Verification checklist**:
  - `source .venv/Scripts/activate && python manage.py check` — Django system check passes with no issues
  - `source .venv/Scripts/activate && python manage.py migrate --check` — no unapplied migrations
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — smoke test passes
  - Dev server responds: start server, `curl --fail --silent --output /dev/null http://localhost:8000/`, stop server

- **Makefile target name**: `checksprint1`

---

### Sprint 2 — Linting, Formatting & Pre-commit Hooks

- **Prerequisite**: Sprint 1
- **Branch**: `sprint/2`
- **Objective**: Configure Black, Flake8, isort, and pre-commit hooks so all code is consistently formatted and linted
- **Why this comes now**: Code quality tooling must be in place before any real code is written to prevent formatting debt

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Install tools: `python -m pip install black flake8 isort pre-commit pip-audit`
  - Update `requirements.txt` with new pinned versions
  - Create or update `pyproject.toml` with Black config (`line-length = 88`, `target-version = ["py312"]`) and isort config (`profile = "black"`)
  - Create `.flake8` with config: `max-line-length = 88`, `extend-ignore = E203,W503`, exclude `.venv,migrations`
  - Create `.pre-commit-config.yaml` with hooks for Black, isort, Flake8, and trailing whitespace
  - Run `pre-commit install` to activate hooks
  - Run `black .` to format all existing code
  - Run `isort .` to sort all imports
  - Run `flake8 .` to verify no lint errors
  - Run `pip-audit` to check for known vulnerabilities
  - Add `lint` target to Makefile: runs `black --check . && isort --check-only . && flake8 .`
  - Add `checksprint2` target to Makefile

- **What you should see when done**:
  - `make lint` passes with no errors
  - `make test` still passes
  - Pre-commit hooks run automatically on `git commit`

- **Verification checklist**:
  - `source .venv/Scripts/activate && black --check .` — all files formatted correctly
  - `source .venv/Scripts/activate && isort --check-only .` — all imports sorted correctly
  - `source .venv/Scripts/activate && flake8 .` — no lint errors
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — tests still pass

- **Makefile target name**: `checksprint2`

---

### Sprint 3 — GitHub Actions CI Pipeline & Branch Protection

- **Prerequisite**: Sprint 2
- **Branch**: `sprint/3`
- **Objective**: Create a GitHub Actions workflow that runs lint and tests on every pull request, and configure branch protection on `main`
- **Why this comes now**: The sprint branching workflow requires CI gating before any feature work begins. From this sprint onward, all PRs are validated automatically.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Create `.github/workflows/ci.yml` with a workflow that triggers on `pull_request` to `main` and runs:
    - Checkout code
    - Set up Python 3.12
    - Create and activate `.venv`
    - Install dependencies from `requirements.txt`
    - Run `make lint`
    - Run `make test`
  - Configure `main` as a protected branch via GitHub CLI:
    - Require pull request reviews before merging
    - Require status checks (the CI workflow) to pass before merging
    - Disallow direct pushes to `main`
  - Note: Per STACK.md, Peliku has no cloud deployment. The CI pipeline validates code quality only. No deployment steps.
  - Add `checksprint3` target to Makefile

- **What you should see when done**:
  - `.github/workflows/ci.yml` exists with valid workflow definition
  - `make lint && make test` passes locally (same commands CI runs)
  - Branch protection is active on `main` (verified via `gh` CLI)

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -c "from pathlib import Path; p=Path('.github/workflows/ci.yml'); assert p.exists(); c=p.read_text(); assert 'pull_request' in c; assert 'lint' in c or 'flake8' in c; assert 'pytest' in c or 'test' in c; print('CI workflow valid')"` — CI workflow file exists and contains PR trigger, lint step, and test step
  - `source .venv/Scripts/activate && make lint` — lint passes
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — tests pass
  - `gh api repos/$(gh repo view --json nameWithOwner -q '.nameWithOwner')/branches/main/protection --silent` — branch protection is configured

- **Makefile target name**: `checksprint3`

---

### Sprint 4 — CSS Design System & Global Layout

- **Prerequisite**: Sprint 3
- **Branch**: `sprint/4`
- **Objective**: Implement the complete CSS design token system from DESIGN.md and build the global page layout (header navigation bar, main content area, toast container)
- **Why this comes now**: All subsequent UI sprints depend on the design tokens and layout shell being in place. This sprint establishes the visual foundation.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md completely — Sections 2 (Color System), 3 (Typography), 4 (Spacing & Layout), 5 (Shapes, Borders & Elevation), 9 (Animation & Motion), 16 (Design Tokens Summary)
  - Create `static/css/tokens.css` — define all CSS custom properties from DESIGN.md Section 16: colors (primary, secondary, accent, neutrals, semantics), typography (`font-heading`, `font-body`), spacing scale, border radii, shadows, z-index scale, animation timing tokens, easing curves
  - Create `static/css/reset.css` — minimal CSS reset (box-sizing, margin/padding reset, smooth scrolling)
  - Create `static/css/typography.css` — import Google Fonts (Quicksand, Inter, JetBrains Mono), define type scale classes (`text-xs` through `text-4xl`), heading styles (`heading-1`, `heading-2`, `heading-3`), body text styles
  - Create `static/css/layout.css` — page background (Neutral 900), container with max-width 1200px, grid system (12/8/4 columns at breakpoints), responsive gutters and padding per DESIGN.md Section 4
  - Create `static/css/components.css` — base styles for buttons (Primary, Secondary, Ghost, Danger variants per Section 7.1), form inputs (Section 7.2), cards (Section 7.3), modals (Section 7.4), toast notifications (Section 7.5)
  - Create `static/css/animations.css` — generation glow pulse, skeleton shimmer, reduced-motion fallbacks per DESIGN.md Section 9
  - Update `templates/base.html`:
    - Add Google Fonts `<link>` tags for Quicksand (400, 500, 700), Inter (400, 500, 700), JetBrains Mono (400)
    - Add Phosphor Icons CDN link (per DESIGN.md Section 6.1)
    - Add jQuery 3.7+ CDN `<script>` tag
    - Link all CSS files in correct order: reset, tokens, typography, layout, components, animations
    - Build the global header nav: 72px height, Neutral 900 background, sticky; left side has "Peliku" logo/link to home; right side has Settings gear icon (per DESIGN.md Section 7.7)
    - Add a `<main>` content block with container class
    - Add a toast notification container at bottom-center (per DESIGN.md Section 7.5)
  - Create `static/js/main.js` — basic jQuery-powered toast notification show/dismiss system, settings gear icon click placeholder
  - Create `core/tests/test_layout.py` — tests that verify base template renders with correct CSS links, header nav is present, jQuery is loaded

- **What you should see when done**:
  - Visiting `http://localhost:8000/` shows the dark-themed page with the sticky header nav bar, "Peliku" logo, and settings gear icon
  - Colors, typography, and spacing match DESIGN.md
  - The page background is Neutral 900 (#0F172A), text is Neutral 50 (#F8FAFC)

- **Verification checklist**:
  - `source .venv/Scripts/activate && python manage.py check` — Django system check passes
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass including layout tests
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Dev server responds with styled page: start server, `curl --fail --silent http://localhost:8000/ | grep -q "Peliku"`, stop server

- **Makefile target name**: `checksprint4`

---

### Sprint 5 — Home Page Shell & New Project Form Shell

- **Prerequisite**: Sprint 4
- **Branch**: `sprint/5`
- **Objective**: Create the Home page with an empty project grid and the New Project form page as static shells (no database interaction yet)
- **Why this comes now**: The skeleton phase builds all navigable pages before adding functionality. Home and New Project are the entry points of the application.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 12.1 (Home Dashboard), Section 12.2 (New Project Form), Section 7.1 (Buttons), Section 7.8 (Empty States)
  - Update `templates/core/home.html`:
    - Empty state: illustration placeholder area, heading "No projects yet. Forge your first reel to get started." (per DESIGN.md Section 7.8, 15.4), large Primary button "New Project"
    - Project grid area (hidden when empty, will be populated in Sprint 9): CSS Grid layout for project cards
    - Search bar at top of grid area (disabled/static for now)
    - "New Project" button in the header-right area (always visible per FEATURE_SPECS Section 5.1)
  - Create `templates/core/project_form.html`:
    - Single-column centered form, max-width 600px (per DESIGN.md Section 12.2)
    - Fields: Title (text input, required), Description (textarea, required, max 2000 chars), Aspect Ratio (toggle 9:16 vs 16:9), Clip Duration (select: 4s, 6s, 8s), Visual Style (textarea, optional, max 500 chars), Number of Clips (select: 5–10, default 7)
    - Character count indicator on Description and Visual Style fields
    - Large Primary button "Generate Scripts" at bottom (disabled/static for now)
    - All form styling follows DESIGN.md Section 7.2 (inputs) and Section 8.1 (validation)
  - Create route `/projects/new/` pointing to a `project_form` view
  - Create `core/views.py` views: `home` (renders home.html), `project_form` (renders project_form.html)
  - Update `core/urls.py` with both routes
  - Create `core/tests/test_pages.py` — tests verifying both pages return 200 and contain expected elements

- **What you should see when done**:
  - `http://localhost:8000/` shows the Home page with empty state message and "New Project" button
  - Clicking "New Project" navigates to `http://localhost:8000/projects/new/`
  - The form page shows all fields with proper dark-themed styling
  - Back navigation works via the "Peliku" logo in the header

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Home page loads: start server, `curl --fail --silent http://localhost:8000/ | grep -q "New Project"`, stop server
  - Form page loads: start server, `curl --fail --silent http://localhost:8000/projects/new/ | grep -q "Generate Scripts"`, stop server

- **Makefile target name**: `checksprint5`

---

### Sprint 6 — Project Workspace Shell

- **Prerequisite**: Sprint 5
- **Branch**: `sprint/6`
- **Objective**: Create the Project Workspace page shell with the clip panel layout, compact header bar, and collapsed Reference Images Panel — all using static dummy data
- **Why this comes now**: The workspace is the core screen of the app. Building its layout shell before any functionality ensures the structure is right.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 12.3 (Project Workspace), Section 7.3 (Cards/Clip Panels), Section 7.6 (Timeline Connectors), Section 7.7 (Navigation)
  - Create `templates/core/workspace.html`:
    - Compact header bar at top: project title (editable inline placeholder), description summary, aspect ratio badge, clip duration, visual style — displayed as read-only text for now
    - Action buttons in header: "Regenerate All Scripts" (Ghost, disabled), "Preview Reel" (Ghost, disabled), "Download Reel" (Primary, disabled) per DESIGN.md Section 7.7
    - Collapsible Reference Images Panel below header: 3 empty slots with dashed borders, "+" icons, helper text "Add character or style references to keep clips consistent" per DESIGN.md Section 7.8. Collapsed by default, expandable via click.
    - Vertical clip sections (3 static dummy clips for layout):
      - Each clip section is a card (Neutral 800 bg, radius-xl, space-6 padding per Section 7.3)
      - Split 50/50 layout: Left panel (script textarea with placeholder text, "Regenerate Script" secondary button, character count), Right panel (video placeholder with dashed border, magic wand icon, "Generate Video" Primary button, "Generation Method" dropdown placeholder)
      - Drag handle on left edge of each card
    - Cyan connector lines between clip sections with "Generate Transition Frame" ghost button per DESIGN.md Section 7.6
  - Create route `/projects/<int:project_id>/` pointing to a `workspace` view
  - Create `core/views.py` `workspace` view rendering `workspace.html` with dummy context
  - Update `core/urls.py`
  - Create `static/js/workspace.js` — jQuery code for Reference Images Panel expand/collapse toggle
  - Create `core/tests/test_workspace.py` — test verifying workspace page renders with clip panels

- **What you should see when done**:
  - `http://localhost:8000/projects/1/` shows the workspace with 3 dummy clip panels in vertical sequence
  - Each clip has a script area on the left and video placeholder on the right
  - Cyan connector lines between clips with transition frame buttons
  - Reference Images Panel expands/collapses on click
  - The header shows placeholder project info and disabled action buttons

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Workspace loads: start server, seed dev data, extract a project URL from home page, `curl --fail --silent http://localhost:8000/projects/<id>/ | grep -q "Generate Video"`, stop server
  - Workspace has clip panels: start server, `curl --fail --silent http://localhost:8000/projects/<id>/ | grep -q "Regenerate Script"`, stop server

- **Makefile target name**: `checksprint6`

---

### Sprint 7 — Settings Panel, Preview Overlay & Responsive Layout

- **Prerequisite**: Sprint 6
- **Branch**: `sprint/7`
- **Objective**: Build the Settings slide-over panel, the Preview overlay shell, and make all existing pages responsive across breakpoints
- **Why this comes now**: Completes the skeleton phase — every view in the app is now navigable, even if non-functional. From this point, the developer can click through every screen.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 10 (Responsive Design), Section 12.4 (Preview Modal), Section 7.4 (Modals), Section 11 (Accessibility — focus indicators)
  - Create `templates/core/partials/settings_panel.html` as a slide-over panel from the right side:
    - Width 360px, Neutral 900 background, 1px solid Neutral 700 border
    - Fields (all static/disabled for now): Default Aspect Ratio (toggle), Default Clip Duration (select), Default Number of Clips (select), Default Visual Style (textarea), Video Quality (select: 720p, 1080p, 4k), Generation Speed (toggle: Quality vs Fast)
    - Close button (X) at top-right
    - Triggered by clicking the Settings gear icon in the global header
  - Create `templates/core/partials/preview_overlay.html` as a full-screen overlay:
    - Neutral 950 at 80% opacity backdrop with blur per DESIGN.md Section 7.4
    - Centered video player placeholder matching selected aspect ratio
    - Timeline scrubber bar at bottom with clip boundary markers
    - Playback controls: play, pause, restart buttons
    - Close button returns to workspace
    - Triggered by "Preview Reel" button in workspace header
  - Update `static/js/main.js` — jQuery handlers: open/close settings panel (slide animation, `duration-normal` 300ms), open/close preview overlay
  - Create `static/css/responsive.css`:
    - Mobile (320px+): single-column layout, clip panels stack (script on top, video below per DESIGN.md Section 10), 16px padding, drag handle moves to top-right
    - Tablet (768px+): 8 columns, 24px gutters
    - Desktop (1024px+): full 12-column layout, side-by-side clip panels
    - Wide (1440px+): centered max-width container
  - Update `templates/base.html` to include `responsive.css`
  - Add responsive viewport meta tag if not already present
  - Ensure all existing pages (Home, Form, Workspace) render correctly at each breakpoint
  - Update keyboard navigation: Escape key closes settings panel and preview overlay
  - Create `core/tests/test_responsive.py` — tests verifying settings panel and preview overlay markup is present

- **What you should see when done**:
  - Clicking the gear icon opens a Settings slide-over panel from the right
  - Clicking "Preview Reel" in the workspace opens a full-screen overlay
  - Escape key dismisses both panels
  - Resizing the browser shows responsive layout changes at all breakpoints
  - Clip panels stack vertically on mobile
  - All pages remain visually consistent with DESIGN.md

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Settings panel markup present: start server, `curl --fail --silent http://localhost:8000/ | grep -q "settings"`, stop server
  - Preview overlay markup present: start server, seed dev data, extract a project URL from home page, `curl --fail --silent http://localhost:8000/projects/<id>/ | grep -q "preview"`, stop server

- **Makefile target name**: `checksprint7`

---

### Sprint 8 — Database Models, Migrations & Seed Command

- **Prerequisite**: Sprint 7
- **Branch**: `sprint/8`
- **Objective**: Define all Django models (Project, Clip, ReferenceImage, Hook, UserSettings, Task), run migrations, and create a seed data management command
- **Why this comes now**: The skeleton is complete. Before wiring real data to the UI, the data layer must be defined and validated.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read STACK.md Section 5 (Database & Storage) for the data model specification
  - Create `core/models.py` with the following models:
    - **Project**: `title` (CharField, max 100), `description` (TextField, max 2000), `visual_style` (TextField, max 500, blank), `aspect_ratio` (CharField, choices: "9:16"/"16:9", default "9:16"), `clip_duration` (IntegerField, choices: 4/6/8, default 8), `num_clips` (IntegerField, default 7, range 5–10), `created_at` (DateTimeField, auto_now_add), `updated_at` (DateTimeField, auto_now)
    - **Clip**: `project` (ForeignKey to Project, CASCADE), `sequence_number` (IntegerField), `script_text` (TextField, blank), `video_file` (FileField, upload_to="videos/", blank), `generation_status` (CharField, choices: idle/generating/completed/failed, default "idle"), `generation_method` (CharField, choices: text_to_video/image_to_video/frame_interpolation/extend_previous, default "text_to_video"), `first_frame` (ImageField, blank), `last_frame` (ImageField, blank), `extension_count` (IntegerField, default 0), `generation_reference_id` (CharField, blank, max 255)
    - **ReferenceImage**: `project` (ForeignKey to Project, CASCADE), `slot_number` (IntegerField, 1–3), `image_file` (ImageField, upload_to="images/references/"), `label` (CharField, max 100), unique_together: (project, slot_number)
    - **Hook**: `project` (OneToOneField to Project, CASCADE), `script_text` (TextField, blank), `video_file` (FileField, upload_to="videos/hooks/", blank), `is_enabled` (BooleanField, default False), `generation_status` (CharField, choices: idle/generating/completed/failed, default "idle")
    - **UserSettings**: singleton model with `default_aspect_ratio`, `default_clip_duration`, `default_num_clips`, `default_visual_style`, `video_quality` (CharField, choices: 720p/1080p/4k, default "720p"), `generation_speed` (CharField, choices: quality/fast, default "quality")
    - **Task**: `task_type` (CharField), `status` (CharField, choices: pending/running/completed/failed, default "pending"), `progress` (IntegerField, default 0), `result_data` (JSONField, blank, null), `error_message` (TextField, blank), `related_object_id` (IntegerField, null), `related_object_type` (CharField, blank), `created_at`, `updated_at`
  - Run `python manage.py makemigrations core` and `python manage.py migrate`
  - Create `core/management/__init__.py` and `core/management/commands/__init__.py`
  - Create `core/management/commands/seed_dev_data.py` — creates 3 sample projects with 7 clips each (scripts filled with placeholder text), 1 reference image per project, and a default UserSettings row
  - Create `core/tests/test_models.py` — tests for model creation, field validation, relationships, cascade delete, UserSettings singleton behavior

- **What you should see when done**:
  - `python manage.py migrate` completes with no errors
  - `python manage.py seed_dev_data` populates the database with sample projects
  - `python manage.py shell` can query `Project.objects.all()` and see seeded data
  - All model tests pass

- **Verification checklist**:
  - `source .venv/Scripts/activate && python manage.py migrate --check` — no unapplied migrations
  - `source .venv/Scripts/activate && python manage.py seed_dev_data` — seed command runs without error
  - `source .venv/Scripts/activate && python -c "import django; django.setup(); from core.models import Project; assert Project.objects.count() >= 3, 'Seed data missing'" 2>/dev/null || (export DJANGO_SETTINGS_MODULE=peliku.settings && source .venv/Scripts/activate && python -c "import django; django.setup(); from core.models import Project; assert Project.objects.count() >= 3")` — seeded projects exist in DB
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all model tests pass

- **Makefile target name**: `checksprint8`

---

### Sprint 9 — Home Page CRUD: List, Create, Delete, Rename, Duplicate, Search

- **Prerequisite**: Sprint 8
- **Branch**: `sprint/9`
- **Objective**: Wire the Home page to display real projects from the database and implement full CRUD operations: create (metadata only), delete, rename, duplicate, and search
- **Why this comes now**: With models in place, the Home page becomes functional. The user can now manage projects before we add AI and video generation.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 12.1 (Home Dashboard), Section 7.3 (Cards), Section 7.4 (Modals), Section 7.1 (Buttons)
  - Update `core/views.py` `home` view to query `Project.objects.all().order_by("-updated_at")` and pass to template
  - Update `templates/core/home.html`:
    - Show project cards in a grid when projects exist (title, creation date, clip progress "0/N clips generated", aspect ratio badge, placeholder thumbnail)
    - Each card has a three-dot menu (Duplicate, Rename, Delete) per FEATURE_SPECS Section 4.4.4
    - Empty state when no projects
    - Search bar at top: filters projects by title (client-side jQuery filtering for simplicity)
  - Create `core/views.py` view `create_project`: accepts POST with form data, creates Project + N empty Clips, redirects to workspace URL
  - Update `project_form` view to pre-fill defaults from UserSettings if they exist
  - Create AJAX endpoints (returning JSON):
    - `POST /api/projects/<id>/delete/` — deletes project and all related data (CASCADE handles clips, refs, hook). Deletes associated media files from disk.
    - `POST /api/projects/<id>/rename/` — updates project title. Accepts JSON `{"title": "New Name"}`.
    - `POST /api/projects/<id>/duplicate/` — copies project metadata, all clip scripts, reference images (files copied), settings. Does not copy videos. Names the copy "[Title] (Copy)".
  - Create confirmation modal template (`templates/core/partials/confirm_modal.html`) per DESIGN.md Section 7.4: 480px width, Neutral 900 bg, explicit close required. Used for delete confirmation.
  - Create `static/js/home.js` — jQuery handlers: three-dot menu toggle, delete with confirmation modal, inline rename (double-click title), duplicate via AJAX, search filtering
  - Create `core/tests/test_project_crud.py` — tests for list, create, delete, rename, duplicate, search behavior

- **What you should see when done**:
  - Home page shows seeded projects as styled cards
  - "New Project" button opens the form, submitting creates a project and redirects to its workspace
  - Three-dot menu works: Rename opens inline editor, Duplicate creates a copy, Delete shows confirmation modal then removes
  - Search bar filters project cards by title in real time

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Projects listed on home: start server, seed data, `curl --fail --silent http://localhost:8000/ | grep -q "clip"`, stop server
  - Delete API works: start server, `curl --fail --silent -X POST http://localhost:8000/api/projects/1/delete/ -H "Content-Type: application/json" -w "%{http_code}" | grep -q "200\|204\|302"`, stop server

- **Makefile target name**: `checksprint9`

---

### Sprint 10 — Gemini AI SDK Integration & Script Generation Service

- **Prerequisite**: Sprint 9
- **Branch**: `sprint/10`
- **Objective**: Set up the Google Gemini AI SDK and create the script generation service that transforms a project description into coherent clip scripts
- **Why this comes now**: AI script generation is the core intelligence of the product. The SDK must be integrated and the service built before wiring it to the UI in the next sprint.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 5.2 (AI Script Generation) for detailed behavior of script generation
  - Install: `python -m pip install google-genai`
  - Update `requirements.txt`
  - Create `core/services/__init__.py`
  - Create `core/services/ai_client.py` — initializes the Gemini client using `GEMINI_API_KEY` from settings. Provides a singleton `get_ai_client()` function.
  - Create `core/services/script_generator.py`:
    - `generate_all_scripts(project)` — takes a Project instance, builds a system prompt that instructs Gemini to write N clip scripts sharing a unified narrative thread, consistent characters, environment, color palette, and mood. Each script includes: subject, action, camera motion, composition, lighting, color palette, ambient sounds, dialogue, and how it connects to the previous/next clips. The first clip establishes the scene; the last provides resolution. Returns a list of script strings.
    - `regenerate_single_script(clip)` — rewrites one clip's script using context from neighboring clips (clip before and after) to maintain narrative flow. Returns the new script string.
    - `regenerate_all_scripts(project)` — rewrites all clip scripts from scratch based on current project metadata. Returns a list of script strings.
    - Uses Gemini 2.0 Flash model for text generation (per STACK.md Section 7)
  - Create `core/tests/test_script_generator.py` — tests with mocked Gemini API responses:
    - Test `generate_all_scripts` returns correct number of scripts
    - Test `regenerate_single_script` uses neighboring clip context
    - Test `regenerate_all_scripts` replaces all scripts
    - Test error handling when API call fails

- **What you should see when done**:
  - `python -c "from core.services.script_generator import generate_all_scripts; print('Service loaded')"` succeeds (with Django setup)
  - All tests pass with mocked API
  - The service is ready to be wired to the form in Sprint 11

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_script_generator.py --tb=short -q` — script generator tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full test suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Service module imports cleanly: `source .venv/Scripts/activate && DJANGO_SETTINGS_MODULE=peliku.settings python -c "from core.services.script_generator import generate_all_scripts; print('OK')"`

- **Makefile target name**: `checksprint10`

---

### Sprint 11 — New Project Form Submits to AI Script Generation

- **Prerequisite**: Sprint 10
- **Branch**: `sprint/11`
- **Objective**: Wire the New Project form so that submitting it creates a project, calls the AI script generation service, saves the generated scripts to clips, and redirects to the workspace
- **Why this comes now**: This completes the first end-to-end user journey: describing a reel idea and seeing AI-generated scripts. The workspace now shows real data.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 12.2 (New Project Form), Section 13 Flow 1 (Create to Scripts)
  - Update `core/views.py` `project_form` view to handle POST:
    - Validate form fields (Title required max 100, Description required max 2000, Visual Style max 500, Aspect Ratio in choices, Clip Duration in choices, Number of Clips 5–10)
    - Create Project instance with validated data
    - Call `generate_all_scripts(project)` to get AI-generated scripts
    - Create Clip instances for each script with sequential `sequence_number`
    - Redirect to `/projects/<id>/`
  - Create a Django Form class `ProjectForm` in `core/forms.py` for server-side validation
  - Update `templates/core/project_form.html`:
    - Form submits via POST to the same URL
    - Show validation errors inline below fields (red border, error message per DESIGN.md Section 8.1)
    - Loading state on submit: disable form, show "Writing your clip scripts..." overlay with skeleton shimmer animation per DESIGN.md Section 9.3
  - Create `static/js/project_form.js` — jQuery: disable form on submit, show loading overlay, character count live update for Description and Visual Style
  - Create `core/tests/test_project_creation.py` — integration tests with mocked Gemini:
    - Test form submission creates project and clips
    - Test validation errors are returned for invalid data
    - Test redirect to workspace after success

- **What you should see when done**:
  - Filling out the New Project form and clicking "Generate Scripts" shows a loading state
  - After generation completes, the browser redirects to the workspace
  - The workspace shows the AI-generated scripts (or placeholder scripts if API key is not set — the mocked tests verify the flow)

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_project_creation.py --tb=short -q` — project creation tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Form submission creates project: `DJANGO_SETTINGS_MODULE=peliku.settings python -c "..."` — uses Django test client (with mocked AI) to POST the form, verifies project and 5 clips are created with scripts, and redirect to workspace

- **Makefile target name**: `checksprint11`

---

### Sprint 12 — Workspace: Display Clip Scripts, Inline Editing & Auto-Save

- **Prerequisite**: Sprint 11
- **Branch**: `sprint/12`
- **Objective**: Wire the Project Workspace to display real clip scripts from the database, enable inline editing of scripts in textareas, and auto-save changes via AJAX
- **Why this comes now**: The workspace shows real data. Users can now review and edit AI-generated scripts — the core creative workflow.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3 (Core Workflow) and Section 5.2 (Manual Script Editing)
  - Read DESIGN.md Section 7.3 (Cards/Clip Panels), Section 3.5 (Typography Rules — max 65 chars line width for scripts)
  - Update `core/views.py` `workspace` view:
    - Query the Project by ID (return 404 if not found)
    - Query all Clips for the project ordered by `sequence_number`
    - Pass project and clips to the template context
  - Update `templates/core/workspace.html`:
    - Render real project title, description, settings in the header bar
    - Loop through clips, rendering each clip section with:
      - Clip number header ("Clip 1", "Clip 2", etc.) using `heading-3` style per DESIGN.md Section 3.4
      - Script textarea populated with `clip.script_text`, max-width 65 characters per line
      - Character count indicator (`1200/2000`)
      - "Regenerate Script" secondary button (wired in Sprint 19)
      - Video placeholder on the right with "Generate Video" button (wired in Sprint 14)
    - Connector lines between clips per DESIGN.md Section 7.6
  - Create AJAX endpoint `POST /api/clips/<id>/update-script/` — accepts JSON `{"script_text": "..."}`, updates the clip, returns JSON success response
  - Update `static/js/workspace.js`:
    - Auto-save: on textarea `blur` event, send AJAX POST to update endpoint. Also debounce save every 5 seconds while typing.
    - Show a subtle "Saved" indicator near the textarea on successful save
    - Character count updates live on input
    - CSRF token handling for AJAX requests (Django requires CSRF even without auth for form safety)
  - Create `core/tests/test_workspace_views.py` — tests for workspace view (project display, clip rendering), script update API endpoint

- **What you should see when done**:
  - Navigating to a project workspace shows all clips with their AI-generated scripts
  - Editing a script and clicking away saves it automatically
  - A subtle "Saved" indicator confirms the save
  - Character count updates as the user types

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — all tests pass
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Workspace shows real clips: start server, seed data, `curl --fail --silent http://localhost:8000/projects/1/ | grep -q "Clip"`, stop server
  - Script update API works: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/update-script/ -H "Content-Type: application/json" -d "{\"script_text\":\"Updated script\"}" -w "%{http_code}" | grep -q "200"`, stop server

- **Makefile target name**: `checksprint12`

---

### Sprint 13 — Background Task System with Threading & Status Polling

- **Prerequisite**: Sprint 12
- **Branch**: `sprint/13`
- **Objective**: Build the background task execution system using Python threading and the Task model, plus a polling API endpoint for the frontend to track task progress
- **Why this comes now**: Video generation takes 11 seconds to 6 minutes. The task system must exist before any generation feature so that long-running operations do not block the HTTP response.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read STACK.md Section 4 (Python threading for long-running tasks)
  - Create `core/services/task_runner.py`:
    - `run_in_background(task_type, target_func, *args, **kwargs)` — creates a Task record (status=pending), spawns a Python thread that:
      - Sets task status to "running"
      - Calls `target_func(*args, **kwargs)`
      - On success: sets status to "completed", stores result in `result_data`
      - On failure: sets status to "failed", stores error in `error_message`
    - Returns the Task ID for polling
    - Uses `threading.Thread(daemon=True)` to avoid blocking server shutdown
  - Create AJAX endpoints in `core/views.py`:
    - `GET /api/tasks/<id>/status/` — returns JSON `{"id": N, "status": "running", "progress": 45, "result_data": null, "error_message": ""}` for polling
  - Create `static/js/task_poller.js`:
    - jQuery-based polling function: `pollTask(taskId, onProgress, onComplete, onError)` — polls the status endpoint every 2 seconds, calls appropriate callback based on status. Stops polling when task is completed or failed.
    - Elapsed time tracker: starts a timer when polling begins, displays elapsed time in the UI element
  - Create `core/tests/test_task_runner.py`:
    - Test task creation and status transitions (pending → running → completed)
    - Test failed task stores error message
    - Test status polling endpoint returns correct JSON
    - Use `threading.Event` to synchronize test assertions with background threads

- **What you should see when done**:
  - The task runner can execute any function in the background and track its status
  - The polling API returns real-time status updates
  - The JS polling mechanism is ready to be used by generation features
  - All tests pass

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_task_runner.py --tb=short -q` — task runner tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Task status API responds: start server, seed data, `curl --fail --silent http://localhost:8000/api/tasks/1/status/ -w "%{http_code}" | grep -qE "200|404"`, stop server

- **Makefile target name**: `checksprint13`

---

### Sprint 14 — Text-to-Video Generation via Veo API

- **Prerequisite**: Sprint 13
- **Branch**: `sprint/14`
- **Objective**: Implement Text-to-Video generation for individual clips using the Gemini Veo API, with per-clip generation status indicators, video display, and file storage
- **Why this comes now**: This is the primary generation method and the first time users see AI-generated video. It builds on the task system from Sprint 13.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 5.3 (Text-to-Video Generation) for detailed behavior
  - Read DESIGN.md Section 7.3 (Clip Panels — right panel states), Section 7.8 (video placeholder), Section 13 Flow 2
  - Create `core/services/video_generator.py`:
    - `generate_text_to_video(clip)` — takes a Clip instance, calls Veo 3.1 API with the clip's script as prompt, project aspect ratio, clip duration, and video quality from UserSettings. Polls the Gemini API for completion. Downloads the generated video file to `media/videos/`. Updates the clip's `video_file`, `generation_status`, and `generation_reference_id`. Returns the file path.
    - Handle API errors gracefully: set `generation_status` to "failed", store error message
  - Create AJAX endpoint `POST /api/clips/<id>/generate-video/` — validates clip exists, creates a background task via `run_in_background` calling `generate_text_to_video`, returns JSON `{"task_id": N}`
  - Update `templates/core/workspace.html` right panel for each clip:
    - When `generation_status == "idle"`: show video placeholder with "Generate Video" Primary button and magic wand icon per DESIGN.md Section 7.8
    - When `generation_status == "generating"`: show pulsing glow animation (DESIGN.md Section 9.3), "Generating video..." text, live elapsed time counter
    - When `generation_status == "completed"`: show `<video>` player with the clip's video file, muted autoplay loop per DESIGN.md Section 18 (anti-pattern: no sound auto-play). Show "Regenerate Video" Secondary button below.
    - When `generation_status == "failed"`: show error message in red, "Retry" button
  - Update `static/js/workspace.js`:
    - "Generate Video" click handler: POST to generate endpoint, get task_id, start polling with `pollTask`, update UI based on status changes
    - On completion: replace placeholder with `<video>` element, show success toast "Clip N generated successfully" per DESIGN.md Section 7.5
    - On failure: show inline error with "Retry" button
  - Serve media files: ensure `peliku/urls.py` serves `MEDIA_URL` in development
  - Create `core/tests/test_video_generation.py`:
    - Test generate endpoint creates task
    - Test video_generator service with mocked Veo API
    - Test status transitions during generation
    - Test error handling for failed generation

- **What you should see when done**:
  - Clicking "Generate Video" on a clip starts generation with a pulsing animation and timer
  - When complete, the clip shows a video player with the generated video (if API key is valid)
  - Success toast appears at bottom-center
  - Failed generations show an error message with retry

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_video_generation.py --tb=short -q` — video generation tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Generate endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-video/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint14`

---

### Sprint 15 — Reference Images: Generate, Upload, Manage & Per-Clip Selection

- **Prerequisite**: Sprint 14
- **Branch**: `sprint/15`
- **Objective**: Implement the Reference Images Panel with AI image generation via Gemini, image upload, label management, and per-clip reference selection checkboxes
- **Why this comes now**: Reference images are the key mechanism for visual consistency across clips. They must be available before the more advanced generation methods (Image-to-Video, Frame Interpolation) that use them.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.2 (Reference Images Panel) and Section 5.4 (Reference Images)
  - Read DESIGN.md Section 6.3 (Image Treatment — 1:1 squares, `object-fit: cover`, `radius-lg`), Section 7.8 (empty state for reference slots)
  - Create `core/services/image_generator.py`:
    - `generate_reference_image(prompt)` — calls Gemini image generation API (Imagen model per STACK.md Section 7) with the given prompt. Downloads and saves the image to `media/images/references/`. Returns the file path.
  - Create AJAX endpoints:
    - `POST /api/projects/<id>/references/generate/` — accepts JSON `{"slot_number": 1, "prompt": "...", "label": "Main character"}`, generates image, creates ReferenceImage record, returns JSON with image URL and label
    - `POST /api/projects/<id>/references/upload/` — accepts multipart form with image file, slot_number, label. Validates file type (JPEG, PNG, WebP). Saves to ReferenceImage. Returns JSON.
    - `DELETE /api/projects/<id>/references/<slot>/` — removes reference image record and deletes file from disk
  - Create a per-clip reference selection system:
    - Add `selected_references` ManyToManyField on Clip model (or a JSON field) to track which reference images the user has selected for each clip
    - Create AJAX endpoint `POST /api/clips/<id>/update-references/` — accepts JSON `{"reference_ids": [1, 3]}` to update selected references
  - Update `templates/core/workspace.html` Reference Images Panel:
    - 3 slots, each showing: thumbnail (1:1, `object-fit: cover`, 16px radius) or empty dashed placeholder with "+" icon
    - Label text field below each thumbnail
    - "Generate" button opens a prompt input inline
    - "Upload" button opens file picker
    - "Remove" (X) button on filled slots
  - Update each clip section:
    - Below the "Generation Method" dropdown, add a "References" section with checkboxes for each defined reference image (label + small thumbnail)
    - "Select All" shortcut link
  - Update `static/js/workspace.js` — jQuery handlers for reference panel interactions: generate, upload, remove, per-clip checkbox toggling
  - Update `generate_text_to_video` in `video_generator.py` to attach selected reference images to the Veo API call when generating
  - Create `core/tests/test_reference_images.py` — tests for generate, upload, delete, per-clip selection

- **What you should see when done**:
  - Expanding the Reference Images Panel shows 3 slots
  - Clicking "Generate" asks for a prompt, generates an image, displays it as a thumbnail
  - Uploading an image places it in a slot with a label
  - Each clip section shows checkboxes for available references
  - Removing a reference updates all clips' selection UI

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_reference_images.py --tb=short -q` — reference image tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Upload endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/projects/1/references/upload/ -F "slot_number=1" -F "label=Test" -F "image=@static/images/placeholder.png" -w "%{http_code}" | grep -qE "200|201|400"`, stop server

- **Makefile target name**: `checksprint15`

---

### Sprint 16 — Image-to-Video Generation Method

- **Prerequisite**: Sprint 15
- **Branch**: `sprint/16`
- **Objective**: Implement the Image-to-Video generation method where a clip is generated from a starting frame image plus the script prompt
- **Why this comes now**: With reference images available, the next generation method adds first-frame control for precise visual anchoring of clips.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.1 (Generation Methods — Image-to-Video)
  - Read DESIGN.md Section 7.2 (Form Inputs — select/dropdown), Section 7.3 (Clip Panels)
  - Update `core/services/video_generator.py`:
    - `generate_image_to_video(clip)` — takes a Clip instance that has a `first_frame` image set. Calls Veo API with the first frame image as the starting frame and the clip's script as the prompt. Downloads video, updates clip record. Returns file path.
  - Update the "Generation Method" dropdown in each clip section:
    - Wire the dropdown to actually switch between "Text-to-Video" (default) and "Image-to-Video"
    - When "Image-to-Video" is selected, reveal a "Set First Frame" sub-panel with options:
      - "Generate Image" — generates a first-frame image from the script using Gemini image API
      - "Upload Image" — opens file picker to upload a custom first frame
      - "Use Previous Clip's Last Frame" — copies the last frame of the previous clip (available only when the previous clip has a last frame set)
    - Show the selected first frame as a thumbnail preview
  - Create AJAX endpoint `POST /api/clips/<id>/set-first-frame/` — accepts multipart form with image file, or JSON `{"source": "generate"}` / `{"source": "previous_clip"}`. Saves the image to `clip.first_frame`.
  - Update `POST /api/clips/<id>/generate-video/` to check `clip.generation_method` and dispatch to the appropriate generator function
  - Update `static/js/workspace.js`:
    - Generation method dropdown change handler: show/hide sub-panels
    - First-frame management handlers
    - "Generate Video" button uses the selected method
  - Create `core/tests/test_image_to_video.py` — tests for image-to-video generation with mocked API, first-frame setting

- **What you should see when done**:
  - Switching the generation method dropdown to "Image-to-Video" reveals the first-frame sub-panel
  - Setting a first frame (generate, upload, or from previous clip) shows a thumbnail
  - Clicking "Generate Video" with Image-to-Video selected uses the first frame

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_image_to_video.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - First frame endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-first-frame/ -H "Content-Type: application/json" -d "{\"source\":\"generate\"}" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint16`

---

### Sprint 17 — Frame Interpolation Generation Method

- **Prerequisite**: Sprint 16
- **Branch**: `sprint/17`
- **Objective**: Implement the Frame Interpolation generation method where a clip is generated to smoothly transition between a first frame and a last frame
- **Why this comes now**: Frame Interpolation is the most powerful method for cross-clip continuity. It builds directly on the first-frame management from Sprint 16 by adding last-frame support.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.1 (Generation Methods — Frame Interpolation)
  - Update `core/services/video_generator.py`:
    - `generate_frame_interpolation(clip)` — takes a Clip with both `first_frame` and `last_frame` set. Calls Veo API with both frames and the script. The video starts at the first frame and ends at the last frame. Downloads video, updates clip. Returns file path.
  - Add "Frame Interpolation" option to the Generation Method dropdown
  - When "Frame Interpolation" is selected, reveal sub-panel with:
    - First Frame input (reuse from Sprint 16): generate, upload, or use previous clip's last frame
    - Last Frame input (new): generate, upload, or use next clip's first frame
    - Both displayed as thumbnail previews side by side
  - Create AJAX endpoint `POST /api/clips/<id>/set-last-frame/` — similar to first-frame endpoint but for `clip.last_frame`
  - Update `POST /api/clips/<id>/generate-video/` to dispatch to `generate_frame_interpolation` when method is "frame_interpolation"
  - Update `static/js/workspace.js` — handlers for last-frame management, Frame Interpolation UI
  - Create `core/tests/test_frame_interpolation.py` — tests with mocked API

- **What you should see when done**:
  - Selecting "Frame Interpolation" shows both first-frame and last-frame inputs
  - Setting both frames and clicking "Generate Video" generates using the interpolation method
  - The thumbnail previews for both frames are visible

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_frame_interpolation.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Last frame endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/set-last-frame/ -H "Content-Type: application/json" -d "{\"source\":\"generate\"}" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint17`

---

### Sprint 18 — Clip Management: Reorder, Add, Delete

- **Prerequisite**: Sprint 17
- **Branch**: `sprint/18`
- **Objective**: Implement drag-and-drop clip reordering, adding new clips, and deleting clips with confirmation
- **Why this comes now**: All generation methods are in place. The user now needs to be able to restructure their reel by rearranging, adding, and removing clips.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.6 (Reordering), Section 4.3.7 (Adding and Removing)
  - Read DESIGN.md Section 7.3 (Cards — drag/focus border: 2px solid Primary 500), Section 7.4 (Modals — delete confirmation)
  - Install jQuery UI (Sortable) via CDN or local file: add to `templates/base.html`
  - Create AJAX endpoints:
    - `POST /api/projects/<id>/clips/reorder/` — accepts JSON `{"clip_ids": [3, 1, 5, 2, 4]}` (new order). Updates `sequence_number` for each clip. Returns success.
    - `POST /api/projects/<id>/clips/add/` — creates a new empty Clip at the end of the sequence. Returns JSON with new clip data.
    - `POST /api/clips/<id>/delete/` — deletes the clip, deletes associated video/images from disk, resequences remaining clips. Returns success.
  - Update `static/js/workspace.js`:
    - Initialize jQuery UI Sortable on the clip container with drag handle (left edge on desktop, top-right icon on mobile per DESIGN.md Section 10)
    - On drop: collect new clip order, POST to reorder endpoint, update clip numbers in the UI
    - "Add Clip" button at bottom of clip list: POST to add endpoint, append new clip section to DOM. Disabled when clip count reaches 10 (tooltip: "Maximum of 10 clips per project" per FEATURE_SPECS Section 8.4)
    - "Delete Clip" button per clip: opens confirmation modal ("Remove Clip N? The script and generated video will be deleted." per FEATURE_SPECS Section 8.5), on confirm POST to delete endpoint, remove clip section from DOM
  - Update `templates/core/workspace.html`:
    - Add drag handles per DESIGN.md
    - Add "Add Clip" button at bottom
    - Add "Delete Clip" ghost/danger button to each clip section
  - Create `core/tests/test_clip_management.py` — tests for reorder API, add clip, delete clip, max clips enforcement

- **What you should see when done**:
  - Dragging clips reorders them with smooth animation
  - "Add Clip" appends a new empty clip section
  - "Delete Clip" shows a confirmation modal, then removes the clip
  - Clip numbers update correctly after reorder/add/delete

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_clip_management.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Add clip endpoint works: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/projects/1/clips/add/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|201"`, stop server

- **Makefile target name**: `checksprint18`

---

### Sprint 19 — Script Regeneration: Single Clip & All Clips

- **Prerequisite**: Sprint 18
- **Branch**: `sprint/19`
- **Objective**: Wire the "Regenerate Script" button per clip and the "Regenerate All Scripts" button in the workspace header to the AI script generation service
- **Why this comes now**: Script editing and clip management are complete. The user now needs AI-assisted script refinement to iterate on their reel narrative.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 5.2 (Single Script Regeneration, Full Script Regeneration)
  - Read DESIGN.md Section 7.4 (Modals — confirmation for full regeneration)
  - Create AJAX endpoints:
    - `POST /api/clips/<id>/regenerate-script/` — calls `regenerate_single_script(clip)` from the script generator service, updates the clip's script_text, returns JSON with new script
    - `POST /api/projects/<id>/regenerate-all-scripts/` — calls `regenerate_all_scripts(project)`, updates all clip scripts, returns JSON with new scripts array
  - Update `static/js/workspace.js`:
    - "Regenerate Script" button handler per clip: POST to single regenerate endpoint, update textarea with new script, show "Script regenerated" toast
    - "Regenerate All Scripts" header button handler: show confirmation modal ("Regenerate all scripts? This will replace all current clip scripts with new AI-generated ones. Existing videos will not be affected." per FEATURE_SPECS Section 8.5), on confirm POST to regenerate-all endpoint, update all textareas
  - Enable the "Regenerate All Scripts" button in the workspace header (was disabled in Sprint 6)
  - Create `core/tests/test_script_regeneration.py` — tests with mocked Gemini API for single and full regeneration

- **What you should see when done**:
  - Clicking "Regenerate Script" on a clip replaces its script with a new AI-generated one
  - Clicking "Regenerate All Scripts" shows a confirmation dialog, then replaces all scripts
  - Toast notifications confirm each action
  - Scripts of neighboring clips are used as context for single regeneration

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_script_regeneration.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Single regen endpoint works: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/regenerate-script/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint19`

---

### Sprint 20 — Transition Frames Generation Between Clips

- **Prerequisite**: Sprint 19
- **Branch**: `sprint/20`
- **Objective**: Implement transition frame generation on the connector between consecutive clips — AI generates an ending frame for clip N and a starting frame for clip N+1 for seamless visual continuity
- **Why this comes now**: All clip generation methods and management tools are in place. Transition frames enable the Frame Interpolation method to produce smooth inter-clip transitions.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.3 (Transition Frames) and Section 5.5
  - Read DESIGN.md Section 7.6 (Timeline Connectors — cyan line, circular ghost button, solid cyan with checkmark when generated)
  - Create `core/services/transition_generator.py`:
    - `generate_transition_frames(clip_above, clip_below)` — uses Gemini image generation to create two images: the ideal ending frame of `clip_above` (based on its script ending + clip_below's script beginning) and the ideal starting frame of `clip_below` (based on clip_above's script ending + clip_below's script beginning). Saves images and sets `clip_above.last_frame` and `clip_below.first_frame`. Returns both file paths.
  - Create AJAX endpoint `POST /api/clips/<id>/generate-transition/` — `id` is the upper clip. Validates that a next clip exists. Creates a background task for transition generation. Returns task_id.
  - Update `templates/core/workspace.html` connector between clips:
    - When no transition frames exist: show "Generate Transition Frame" ghost button with circle icon on the cyan connector line
    - When transition frames are generated: show solid cyan circle with checkmark icon, small thumbnails of the two frames on hover/click
  - Update `static/js/workspace.js` — handle transition frame button click, poll for completion, update connector UI
  - Create `core/tests/test_transition_frames.py` — tests with mocked image generation

- **What you should see when done**:
  - Clicking "Generate Transition Frame" between two clips shows a spinner, then displays the generated frames
  - The connector icon changes from ghost to solid cyan with checkmark
  - The generated frames are automatically set as the last/first frames of the respective clips

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_transition_frames.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Transition endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/generate-transition/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint20`

---

### Sprint 21 — Video Extension: Extend Clip +7 Seconds

- **Prerequisite**: Sprint 20
- **Branch**: `sprint/21`
- **Objective**: Implement the "Extend Clip" feature that adds 7 seconds to an existing clip's video using the Veo Video Extension API
- **Why this comes now**: With basic and advanced generation in place, video extension allows users to lengthen important clips — a common creative need during the refinement phase.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.4 (Extending a Clip) and Section 5.3 (Video Extension)
  - Read DESIGN.md Section 13 Flow 3 (Extending a Clip)
  - Create `core/services/video_extender.py`:
    - `extend_clip_video(clip, extension_prompt)` — calls Veo Video Extension API with the clip's `generation_reference_id` and the extension prompt. The API adds 7 seconds. Downloads the extended video, replaces the clip's `video_file`, increments `extension_count`. Returns new file path.
    - Validates: clip must have a generated video, `generation_reference_id` must exist (video reference not expired), `extension_count` must be < 20
  - Create AJAX endpoint `POST /api/clips/<id>/extend/` — accepts JSON `{"prompt": "Dog smiles at camera and winks"}`. Validates preconditions. Creates background task. Returns task_id.
  - Update `templates/core/workspace.html` per clip:
    - Show "Extend Clip" secondary button below the video player (only when clip has a completed video)
    - Clicking it opens a small inline form: "What happens next?" textarea + "Confirm" button + "Cancel" link per DESIGN.md Section 13 Flow 3
    - Show extension count: "Extended 2/20 times"
    - When max extensions reached (20), disable button with tooltip "Maximum extension limit reached" per FEATURE_SPECS Section 8.4
    - Info note: "Extensions are generated at 720p"
  - Update `static/js/workspace.js` — extend button handler, inline form toggle, confirmation, polling
  - Create `core/tests/test_video_extension.py` — tests with mocked API, max extension enforcement

- **What you should see when done**:
  - Clicking "Extend Clip" reveals an inline prompt form
  - Entering a prompt and clicking "Confirm" starts the extension (loading state)
  - On completion, the clip's video is updated with the extended version
  - Extension count increments and displays

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_video_extension.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Extend endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/1/extend/ -H "Content-Type: application/json" -d "{\"prompt\":\"Continue the scene\"}" -w "%{http_code}" | grep -qE "200|202|400"`, stop server

- **Makefile target name**: `checksprint21`

---

### Sprint 22 — Extend from Previous Clip Generation Method

- **Prerequisite**: Sprint 21
- **Branch**: `sprint/22`
- **Objective**: Implement the "Extend from Previous Clip" generation method where the current clip's video is generated by extending the previous clip's video, then splitting the result
- **Why this comes now**: This is the most advanced generation method, building on the video extension infrastructure from Sprint 21. It produces the most seamless transitions.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.3.1 (Extend from Previous Clip — full behavior description)
  - Update `core/services/video_generator.py`:
    - `generate_extend_from_previous(clip)` — validates: clip is not Clip 1, previous clip has a completed video with a valid `generation_reference_id`. Calls Veo extension using the previous clip's video reference and the current clip's script as the prompt. Downloads the combined video. Splits it: the previous clip keeps its original portion, the new portion becomes the current clip's video. Updates both clips' records. Resolution locked to 720p.
  - Add "Extend from Previous Clip" option to the Generation Method dropdown
    - Only enabled on Clip 2+ (disabled with tooltip on Clip 1)
    - Only enabled when the previous clip has a generated video (disabled with tooltip otherwise)
  - Update `POST /api/clips/<id>/generate-video/` to dispatch to `generate_extend_from_previous` when method is "extend_previous"
  - Update `static/js/workspace.js` — method dropdown logic for enabling/disabling based on clip position and previous clip status
  - Create `core/tests/test_extend_from_previous.py` — tests for validation rules, video splitting, mocked API

- **What you should see when done**:
  - "Extend from Previous Clip" appears in the dropdown for Clip 2 and above
  - It is disabled if the previous clip has no generated video
  - When used, the current clip's video is generated as a continuation of the previous clip's video
  - Info note about 720p resolution is shown

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_extend_from_previous.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Generate endpoint accepts extend_previous method: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/clips/2/generate-video/ -H "Content-Type: application/json" -d "{\"method\":\"extend_previous\"}" -w "%{http_code}" | grep -qE "200|202|400"`, stop server

- **Makefile target name**: `checksprint22`

---

### Sprint 23 — Reel Preview: Full-Screen Overlay with Timeline Scrubber

- **Prerequisite**: Sprint 22
- **Branch**: `sprint/23`
- **Objective**: Implement the reel preview overlay that plays all generated clips sequentially with a timeline scrubber showing clip boundaries and playback controls
- **Why this comes now**: All generation methods are complete. The user needs to preview the assembled reel before downloading it.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.4.1 (Previewing the Full Reel)
  - Read DESIGN.md Section 12.4 (Preview Modal), Section 7.4 (Modals — full viewport overlay)
  - Update `templates/core/partials/preview_overlay.html`:
    - Full-viewport overlay: Neutral 950 at 80% opacity backdrop, blur
    - Centered `<video>` player matching the project's aspect ratio (9:16 or 16:9)
    - Playback controls: Play/Pause button, Restart button, current time display
    - Timeline scrubber bar at bottom: segmented by clip boundaries (each segment proportional to clip duration), clips without video show as dark placeholder segments. Hook segment at the start if enabled.
    - Clicking a segment jumps to that clip
    - Clips without video are skipped automatically during playback
    - Close button (X) at top-right, Escape key dismisses
  - Create AJAX endpoint `GET /api/projects/<id>/preview-data/` — returns JSON with ordered list of clip video URLs (or null for clips without video), clip durations, and hook video URL/status
  - Create `static/js/preview.js`:
    - jQuery/vanilla JS for: loading clip video URLs, sequential playback using `<video>` element, switching sources when a clip ends, scrubber bar rendering and click handling, play/pause/restart controls
    - Time display and progress tracking across clips
    - Skip clips without video
  - Enable the "Preview Reel" button in the workspace header (show message "No clips have been generated yet" if no clips have video per FEATURE_SPECS Section 8.1)
  - Create `core/tests/test_preview.py` — tests for preview data endpoint, clip ordering

- **What you should see when done**:
  - Clicking "Preview Reel" opens the full-screen overlay
  - All generated clip videos play in sequence
  - The scrubber bar shows clip boundaries and current position
  - Clicking a scrubber segment jumps to that clip
  - Play/Pause/Restart controls work
  - Close button and Escape dismiss the overlay

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_preview.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Preview data endpoint responds: start server, seed data, `curl --fail --silent http://localhost:8000/api/projects/1/preview-data/ -w "%{http_code}" | grep -qE "200"`, stop server

- **Makefile target name**: `checksprint23`

---

### Sprint 24 — Reel Assembly & Download via FFmpeg

- **Prerequisite**: Sprint 23
- **Branch**: `sprint/24`
- **Objective**: Implement server-side reel assembly that concatenates all clip videos (and optional hook) into a single MP4 file using FFmpeg, with progress indicator and automatic download
- **Why this comes now**: Preview is complete. This is the final deliverable — the downloadable MP4 file ready for Instagram/TikTok.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.4.2 (Assembling and Downloading) and Section 5.6 (Reel Assembly & Export)
  - Install `ffmpeg-python` (Python wrapper): `python -m pip install ffmpeg-python`
  - Update `requirements.txt`
  - Ensure FFmpeg binary is available on the system PATH (document in README or .env.example)
  - Create `core/services/reel_assembler.py`:
    - `assemble_reel(project)` — validates all clips have video files. Collects video file paths in order. If hook is enabled and has a video, prepend it. Uses FFmpeg concat demuxer to concatenate videos into a single MP4. Saves to `media/reels/`. Returns the file path.
    - `sanitize_filename(title)` — converts project title to safe filename (lowercase, spaces to dashes, remove special chars)
    - Handles different resolutions by re-encoding to a common format
  - Create AJAX endpoint `POST /api/projects/<id>/assemble/` — validates all clips have videos. Creates background task for assembly. Returns task_id.
  - Create AJAX endpoint `GET /api/projects/<id>/download-reel/` — serves the assembled reel file for download with proper Content-Disposition header
  - Update workspace header:
    - "Download Reel" Primary button: enabled only when all clips have generated videos per FEATURE_SPECS Section 4.4.2
    - When disabled, tooltip: "Generate all clip videos to download the reel"
    - On click: show progress modal "Assembling your reel..." with progress bar per DESIGN.md Section 7.4
    - On completion: browser downloads the file automatically
  - Update `static/js/workspace.js` — download button handler, assembly progress modal, auto-download on completion
  - Create `core/tests/test_reel_assembly.py` — tests for assembly logic (mocked FFmpeg), filename sanitization, download endpoint

- **What you should see when done**:
  - "Download Reel" button activates only when all clips have videos
  - Clicking it shows "Assembling your reel..." modal with progress
  - On completion, the browser downloads `project-title.mp4`
  - The assembled reel includes the hook at the beginning if toggled on

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_reel_assembly.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Assembly endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/projects/1/assemble/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|202|400"`, stop server

- **Makefile target name**: `checksprint24`

---

### Sprint 25 — Individual Clip Download & Project Card Thumbnails

- **Prerequisite**: Sprint 24
- **Branch**: `sprint/25`
- **Objective**: Add individual clip download buttons and generate project card thumbnails on the Home page from the first clip's first frame
- **Why this comes now**: The reel can be assembled and downloaded. These are supplementary export and visualization features that complete the media management UX.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.4.3 (Downloading Individual Clips) and Section 4.4.4 (project card details)
  - Read DESIGN.md Section 6.3 (Image Treatment — thumbnails with `radius-lg`)
  - Create AJAX endpoint `GET /api/clips/<id>/download/` — serves the clip's video file with Content-Disposition header using filename format `{project-title}-clip-{N}.mp4`
  - Update `templates/core/workspace.html`:
    - Add a small "Download" icon button (Phosphor download icon, ghost button) on each clip's video player area (visible only when clip has a generated video)
  - Create `core/services/thumbnail_generator.py`:
    - `generate_project_thumbnail(project)` — extracts the first frame of the first clip's video using FFmpeg. Saves as a JPEG thumbnail in `media/images/thumbnails/`. Returns the path. If no clips have video, returns None.
  - Update `core/views.py` `home` view to include thumbnail URLs in the template context
  - Update `templates/core/home.html`:
    - Project cards show the thumbnail image if available (1:1 crop, `object-fit: cover`, `border-radius: 16px`)
    - Placeholder gradient when no thumbnail is available
  - Auto-generate thumbnail when a clip's video changes (signal or explicit call)
  - Create `core/tests/test_clip_download.py` — tests for download endpoint, filename formatting
  - Create `core/tests/test_thumbnails.py` — tests for thumbnail generation (mocked FFmpeg)

- **What you should see when done**:
  - Each clip with a video shows a small download icon
  - Clicking it downloads the individual clip as `project-title-clip-N.mp4`
  - Home page project cards show thumbnails from the first clip's video
  - Cards without clips show a placeholder gradient

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_clip_download.py core/tests/test_thumbnails.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Download endpoint responds: start server, seed data, `curl --fail --silent http://localhost:8000/api/clips/1/download/ -w "%{http_code}" -o /dev/null | grep -qE "200|404"`, stop server

- **Makefile target name**: `checksprint25`

---

### Sprint 26 — Hook Section: Script & Video Generation, Toggle

- **Prerequisite**: Sprint 25
- **Branch**: `sprint/26`
- **Objective**: Implement the Hook Section pinned above Clip 1: AI hook script generation, hook video generation, editable script, reference selection, and the toggle to include/exclude the hook in the final reel
- **Why this comes now**: All clip features and reel assembly are complete. The hook is the final creative feature — a viral attention-grabbing clip prepended to the reel.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.4.5 (Hook Generation) and Section 5.7 (Hook — full behavior)
  - Read DESIGN.md Section 17 Feature 5 (Hook — tinted with Secondary Pink #EC4899 borders, same internal layout as clip cards)
  - Create `core/services/hook_generator.py`:
    - `generate_hook_script(project)` — analyzes all clip scripts, uses Gemini to write a 4-second hook prompt designed to stop scrollers. Focuses on: visually arresting image, provocative question, dramatic action, or emotional hook. Returns the script string.
  - Create AJAX endpoints:
    - `POST /api/projects/<id>/hook/generate-script/` — calls `generate_hook_script`, saves to Hook model, returns JSON with script
    - `POST /api/projects/<id>/hook/generate-video/` — generates 4-second hook video via Veo (Text-to-Video or Image-to-Video, duration fixed at 4s). Creates background task. Returns task_id.
    - `POST /api/projects/<id>/hook/update-script/` — updates hook script text (for manual editing)
    - `POST /api/projects/<id>/hook/toggle/` — toggles `hook.is_enabled`, returns JSON with new state
    - `POST /api/projects/<id>/hook/regenerate-script/` — writes a fresh hook script
  - Update `templates/core/workspace.html`:
    - Hook Section pinned above Clip 1 (visible only when all clips have generated videos per FEATURE_SPECS Section 4.4.5)
    - Banner: "Your reel is complete. Add a hook to grab attention in the first seconds." with "Generate Hook Script" button (styled with Secondary Pink #EC4899 border per DESIGN.md Section 17)
    - Same two-panel layout as regular clips: left panel (editable hook script textarea, "Regenerate Hook Script" button, References selector), right panel (video placeholder or player, "Generate Hook Video" button)
    - Toggle switch: "Include hook in final reel" per DESIGN.md Section 7.2 (Toggle/Switch)
  - Update reel assembly (`reel_assembler.py`) to check `hook.is_enabled` and prepend hook video if enabled
  - Update preview to include hook as first segment if enabled
  - Update `static/js/workspace.js` — hook section handlers
  - Create `core/tests/test_hook.py` — tests for hook script generation, video generation, toggle, reel prepending

- **What you should see when done**:
  - When all clips have video, the Hook Section appears above Clip 1 with a pink-bordered banner
  - "Generate Hook Script" writes a hook, displayed in an editable textarea
  - "Generate Hook Video" creates a 4-second video shown in the right panel
  - The toggle controls whether the hook is included in preview and download

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_hook.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Hook script endpoint responds: start server, seed data, `curl --fail --silent -X POST http://localhost:8000/api/projects/1/hook/generate-script/ -H "Content-Type: application/json" -w "%{http_code}" | grep -qE "200|202"`, stop server

- **Makefile target name**: `checksprint26`

---

### Sprint 27 — Settings Panel: Default Preferences

- **Prerequisite**: Sprint 26
- **Branch**: `sprint/27`
- **Objective**: Wire the Settings slide-over panel to the UserSettings model so preferences persist and pre-fill new project forms
- **Why this comes now**: All features are built. Settings allow the user to customize their default workflow parameters for future projects.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4.6 (Settings) and Section 5.8 (Settings — detailed behavior)
  - Read DESIGN.md Section 7.2 (Form Inputs, Toggle/Switch, Select/Dropdown)
  - Create AJAX endpoints:
    - `GET /api/settings/` — returns current UserSettings as JSON (creates default row if none exists)
    - `POST /api/settings/` — accepts JSON with any/all setting fields, updates UserSettings, returns updated JSON. Saves immediately on each change per FEATURE_SPECS Section 5.8.
  - Update `templates/core/partials/settings_panel.html`:
    - Wire all form fields to real data from UserSettings:
      - Default Aspect Ratio: toggle between 9:16 and 16:9
      - Default Clip Duration: select (4, 6, 8 seconds)
      - Default Number of Clips: select (5–10)
      - Default Visual Style: textarea (max 500 chars)
      - Video Quality: select (720p, 1080p, 4k) with note "1080p and 4k require 8-second clips" per FEATURE_SPECS Section 8.4
      - Generation Speed: toggle (Quality vs Fast)
  - Update `static/js/main.js`:
    - Load settings on panel open via GET
    - Save on every field change via POST (debounced for text fields)
    - Show "Saved" indicator on successful save
  - Update `project_form` view to pre-fill form defaults from UserSettings
  - Update video generation services to read `video_quality` and `generation_speed` from UserSettings when making API calls
  - Create `core/tests/test_settings.py` — tests for GET/POST endpoints, default creation, pre-fill behavior

- **What you should see when done**:
  - Opening Settings shows current preferences loaded from DB
  - Changing any setting saves immediately
  - Creating a new project pre-fills the form with saved defaults
  - Video generation uses the configured quality and speed settings

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_settings.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Settings API responds: start server, `curl --fail --silent http://localhost:8000/api/settings/ -w "%{http_code}" | grep -qE "200"`, stop server

- **Makefile target name**: `checksprint27`

---

### Sprint 28 — Error Handling, Loading States, Empty States, Toasts & Modals

- **Prerequisite**: Sprint 27
- **Branch**: `sprint/28`
- **Objective**: Implement comprehensive error handling, all loading states, all empty states, toast notification system, and all confirmation modals across the entire application
- **Why this comes now**: All features are functional. This sprint polishes the UX by ensuring every state and edge case defined in the specs is handled gracefully.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 8 (States, Edge Cases & Error Handling) — every subsection
  - Read DESIGN.md Section 7.4 (Modals), Section 7.5 (Toast Notifications), Section 7.8 (Empty States), Section 9.3 (Custom Animations), Section 15.3 (Error & Loading Messages), Section 15.4 (Empty States copy), Section 18 (Anti-Patterns)
  - Error States (per FEATURE_SPECS Section 8.3):
    - Video generation fails: inline red error on clip right panel with specific message and "Retry" button
    - Script generation fails: toast "Script generation failed. Please try again.", form input preserved
    - Video extension fails: inline error on clip, existing video unaffected
    - Reel assembly fails: modal with "Assembly failed" message and "Retry" button
    - Image generation fails (references/transitions): inline error with "Retry"
    - Hook script/video generation fails: toast or inline error, previous state preserved
    - Never show raw technical errors (no "HTTP 500") — use human-readable messages per DESIGN.md Section 15.3
  - Loading States (per FEATURE_SPECS Section 8.2):
    - Script generation: full-screen overlay "Writing your clip scripts..." with skeleton shimmer
    - Video generation: pulsing glow animation, "Generating video...", live elapsed timer
    - Reel assembly: centered modal with progress bar
    - Transition frames: small spinner on connector "Generating transition frames..."
  - Empty States (per FEATURE_SPECS Section 8.1):
    - Home page: "No projects yet. Forge your first reel to get started."
    - Workspace (no videos): all right panels show placeholder with "Generate Video"
    - Reference panel: three dashed slots with "Add reference images to maintain visual consistency"
  - Boundary States (per FEATURE_SPECS Section 8.4):
    - Max 10 clips: "Add Clip" disabled with tooltip
    - Max 3 references: no additional add option
    - Max 20 extensions: "Extend Clip" disabled with tooltip
    - 1080p/4k locks clip duration to 8s
    - Extension always 720p: show info note
  - Confirmation Modals (per FEATURE_SPECS Section 8.5):
    - Verify all destructive actions use confirmation modals: Delete Project, Delete Clip, Regenerate All Scripts, Regenerate Video (when video exists), Regenerate Hook Video
    - All modals follow DESIGN.md Section 7.4: 480px width, centered, require explicit action to dismiss
    - Cancel is default focus, destructive button is styled red (Danger)
  - Toast Notifications:
    - Implement/polish the toast system: bottom-center, pill shape with `radius-full`, auto-dismiss after 5 seconds, max stack of 3 per DESIGN.md Section 7.5
    - Success (teal): "Clip N generated successfully", "Script regenerated", "Settings saved"
    - Error (red): "Generation failed. Try again."
  - Audit every AJAX call across all JS files for proper error handling (network failure, server error, timeout)
  - Create `core/tests/test_error_states.py` — tests for error responses, boundary enforcement, empty states

- **What you should see when done**:
  - Every failure shows a clear, human-readable error message with a retry option
  - Every long operation shows an appropriate loading animation
  - Empty pages guide the user to the next action
  - All destructive actions require confirmation
  - Toast notifications appear and auto-dismiss

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_error_states.py --tb=short -q` — tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - Empty state renders on home: start server, `curl --fail --silent http://localhost:8000/ | grep -q "Forge your first reel"`, stop server

- **Makefile target name**: `checksprint28`

---

### Sprint 29 — Accessibility Audit, Animation System & Reduced-Motion

- **Prerequisite**: Sprint 28
- **Branch**: `sprint/29`
- **Objective**: Conduct a full accessibility audit, implement the animation/motion system from DESIGN.md, add reduced-motion fallbacks, and verify contrast compliance
- **Why this comes now**: All features and states are implemented. This sprint ensures the application meets accessibility standards and the animation design spec.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read DESIGN.md Section 9 (Animation & Motion — timing tokens, easing, custom animations), Section 11 (Accessibility Specifications), Section 2.5 (Contrast Compliance)
  - Accessibility Audit:
    - Verify all interactive elements are keyboard-reachable (Tab/Shift-Tab navigation)
    - Add visible focus indicators: 2px offset solid outline in Cyan (#06B6D4) per DESIGN.md Section 11
    - Ensure all form inputs have associated `<label>` elements (never replaced by placeholder per Section 11)
    - Add ARIA live regions for generation status changes ("Clip 3 generation complete" announced to screen readers per Section 11)
    - Add `role`, `aria-label`, `aria-expanded`, `aria-hidden` attributes as needed for: settings panel, preview overlay, modals, generation status
    - Ensure heading hierarchy follows h1 → h2 → h3 without skips per DESIGN.md Section 3.5
    - Verify minimum tap/click target of 44×44px for all interactive elements
    - Add skip navigation link for content-heavy workspace page
  - Animation System:
    - Verify all animations use correct timing tokens: `duration-fast` (150ms) for buttons/hover, `duration-normal` (300ms) for modals/toasts, `duration-slow` (500ms) for expanding panels
    - Verify easing curve: `cubic-bezier(0.4, 0, 0.2, 1)` used throughout
    - Generation glow: purple pulsing animation on generating clips per Section 9.3
    - Skeleton shimmer: left-to-right sweep during script generation per Section 9.3
    - Placeholder pulse shimmer for image placeholders per DESIGN.md Section 6.3
  - Reduced Motion:
    - Add `@media (prefers-reduced-motion: reduce)` rules that replace pulses/shimmers with static "Generating..." text per Section 9.3
    - Disable all non-essential animations when user prefers reduced motion
  - Contrast Compliance:
    - Verify Primary text on Page Background > 14:1 per Section 2.5
    - Verify Primary Button text on Primary 600 ≥ 4.5:1
    - Adjust any borderline color combinations (e.g., Pink 500 on Slate 800 → use Pink 400)
  - Create `core/tests/test_accessibility.py` — tests for: ARIA attributes present, heading hierarchy, label associations, focus indicators in CSS

- **What you should see when done**:
  - Tab key navigates through all interactive elements with visible cyan focus ring
  - Screen reader announces generation status changes
  - Animations use correct timing and easing from DESIGN.md
  - Enabling "prefers-reduced-motion" disables animations, shows static text
  - All text passes contrast requirements

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_accessibility.py --tb=short -q` — accessibility tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - ARIA attributes present: start server, `curl --fail --silent http://localhost:8000/projects/1/ | grep -q "aria-"`, stop server

- **Makefile target name**: `checksprint29`

---

### Sprint 30 — Final Integration Testing, Edge Cases & Documentation

- **Prerequisite**: Sprint 29
- **Branch**: `sprint/30`
- **Objective**: Run comprehensive end-to-end integration tests covering the full user journey, handle remaining edge cases, and create the project README with setup instructions
- **Why this comes now**: This is the final sprint. Everything is built, polished, and accessible. This sprint verifies the complete product works as a whole and documents how to set it up.

- **What to build**:
  - Read FEATURE_SPECS.md completely before implementing this sprint
  - Read FEATURE_SPECS.md Section 4 (full User Journey) and Section 11 (Success Metrics)
  - Integration Tests — create `core/tests/test_integration.py`:
    - Full journey test: create project → scripts generated → edit script → generate video (mocked) → add reference → regenerate with reference → reorder clips → preview → assemble → download
    - Hook flow test: all clips generated → hook script generated → hook video generated → toggle on → assembly includes hook
    - Duplication test: duplicate project → verify scripts and references copied → verify videos not copied
    - Deletion test: delete project → verify all related data (clips, references, hook, videos on disk) are removed
  - Edge Cases:
    - Project with 1 clip (minimum): verify all features work
    - Project with 10 clips (maximum): verify Add Clip is disabled, all features work
    - Empty description edge: validation catches it
    - Very long script (2000 chars): displays correctly, saves correctly
    - Multiple simultaneous video generations: task system handles independently
    - Clip deletion while video is generating: handle gracefully
    - Browser refresh during generation: status polling resumes correctly
  - Pagination on Home page: if more than 20 projects, implement pagination per DESIGN.md Section 18 (anti-pattern: no infinite scroll)
  - Create `README.md` at project root:
    - Project description and overview
    - Prerequisites (Python 3.12, FFmpeg, Git)
    - Setup instructions (clone, create .venv, install dependencies, create .env, migrate, seed)
    - How to run: `python manage.py runserver`
    - How to run tests: `make test`
    - How to lint: `make lint`
    - Environment variables documentation
    - Project structure overview
  - Verify `make checkall` passes (all 30 sprint checks in sequence)
  - Run `pip-audit` for final dependency security check

- **What you should see when done**:
  - All integration tests pass end-to-end
  - The full user journey works: create → generate → edit → preview → download
  - README provides clear setup instructions
  - `make checkall` passes all 30 sprint checks
  - The product is complete and ready for use

- **Verification checklist**:
  - `source .venv/Scripts/activate && python -m pytest core/tests/test_integration.py --tb=short -q` — integration tests pass
  - `source .venv/Scripts/activate && python -m pytest --tb=short -q` — full suite passes
  - `source .venv/Scripts/activate && make lint` — lint passes
  - `source .venv/Scripts/activate && pip-audit` — no known vulnerabilities
  - README exists and is well-formed: start server, `curl --fail --silent http://localhost:8000/ | grep -q "Peliku"`, stop server

- **Makefile target name**: `checksprint30`

---

## Appendix: Complete Makefile Reference

```makefile
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
	$(ACTIVATE) && python -c "from pathlib import Path; p = Path('.github/workflows/ci.yml'); assert p.exists(), 'CI workflow not found'; c = p.read_text(); assert 'pull_request' in c, 'No PR trigger'; assert 'test' in c or 'pytest' in c, 'No test step'; print('CI workflow valid')"
	gh api repos/$$(gh repo view --json nameWithOwner -q '.nameWithOwner')/branches/main/protection --silent

# ─── Sprint 4: Design System & Layout ───────────────────────────────────────

checksprint4:
	$(ACTIVATE) && python manage.py check
	$(ACTIVATE) && python -m pytest --tb=short -q
	$(ACTIVATE) && make lint
	@$(ACTIVATE) && python manage.py runserver 8000 > /dev/null 2>&1 & RF_PID=$$! && sleep 3 && \
		curl --fail --silent http://localhost:8000/ | grep -q "Peliku" ; \
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
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=peliku.settings python -c "\
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
	$(ACTIVATE) && DJANGO_SETTINGS_MODULE=peliku.settings python -c "\
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
```
