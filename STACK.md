# Technology Stack — ReelForge

> Generated from: FEATURE_SPECS.md
> Date: March 15, 2026
> Preferences applied: Django for front and backend, HTML/CSS/jQuery/Vanilla JavaScript for frontend, SQLite for database, no authentication, local file storage, Gemini AI for all AI generation

---

## 1. Architecture Overview

ReelForge uses a **Django monolith** architecture where Django handles everything: HTTP routing, template rendering, business logic, database access, file storage, and API communication with Gemini AI services. The frontend is rendered server-side using Django templates with progressive enhancement via jQuery and vanilla JavaScript for interactivity. This is the simplest possible architecture for a single-user tool with no scaling requirements, no deployment complexity, and no team coordination overhead. The single-user constraint means no authentication system, no multi-tenancy concerns, and no concurrent modification conflicts — everything Django adds complexity for in typical web apps is unnecessary here.

The primary language is **Python 3.12** for the backend (Django, business logic, AI integration) and **JavaScript** for frontend interactivity. Python was chosen because the Gemini AI SDK (`google-genai`) is Python-first, Django is a mature Python framework with everything built-in, and Python's simplicity matches the straightforward requirements of a personal tool. JavaScript is kept minimal and framework-free per user preference — jQuery handles DOM manipulation and AJAX, vanilla JavaScript handles everything else.

Trade-offs: A monolith becomes harder to scale horizontally if this ever becomes multi-user, but that is explicitly out of scope. Server-side rendering with Django templates is less interactive than a React SPA, but the specs do not require real-time collaborative features or instant UI updates — the workflow is create, generate (wait), review, iterate. This architecture minimizes moving parts and maximizes simplicity for a solo developer maintaining a personal tool.

---

## 2. Frontend

- **Django Templates (built into Django)**
  - Purpose: server-side HTML rendering for all pages (Home, Project Workspace, Settings)
  - Why chosen: Django's template engine is fast, secure (auto-escapes HTML), and requires zero build step. Every page is a server-rendered HTML response. No webpack, no build artifacts, no hydration mismatches. The specs require a dark-themed, minimal, production-focused UI with editable text areas, video players, drag-and-drop reordering, and AJAX updates — all achievable with server-rendered HTML enhanced with JavaScript.
  - Trade-off: No client-side routing or instant navigation. Every page transition is a full server round-trip. Acceptable because this is a desktop-focused tool where page loads are infrequent (the user stays in the Project Workspace for most of their session).

- **jQuery 3.7+**
  - Purpose: DOM manipulation, event handling, AJAX requests to Django backend for video generation, script regeneration, clip updates, and all asynchronous operations not requiring page reload
  - Why chosen: User preference. jQuery is lightweight (30KB minified), works everywhere, requires no build step, and handles 100% of the interactivity needs in the specs: show/hide panels, update clip status indicators, trigger async generation calls, handle drag-and-drop with jQuery UI, update video players when generation completes. The specs do not require complex client-side state management or reactive data binding — jQuery's imperative approach fits perfectly.
  - Trade-off: jQuery is less declarative and harder to test than modern frameworks. But for a solo tool with no CI/CD or team maintenance requirements, this is irrelevant. The user prefers jQuery, and it works.

- **Vanilla JavaScript (ES6+)**
  - Purpose: custom logic not covered by jQuery — video player controls, drag-and-drop gestures for clip reordering, keyboard shortcuts, modal toggling, scrubber bar interactions in the reel preview
  - Why chosen: User preference. For anything beyond basic DOM updates, vanilla JS provides full control without adding another dependency. The specs require custom interactions like clicking a scrubber bar segment to jump to a clip, dragging clips to reorder them, and toggling between generation modes — all implementable with plain JavaScript event listeners and DOM APIs.
  - Trade-off: More verbose than framework abstractions like React hooks or Vue reactivity. But the specs do not require complex UI synchronization or nested component hierarchies — the interface is a linear sequence of clip sections with independent state.

---

## 3. Styling & UI Components

- **CSS3 (custom stylesheets)**
  - Purpose: all visual styling — layout, typography, colors, spacing, dark theme, component states (hover, focus, disabled)
  - Why chosen: The specs describe a minimal, dark-themed, production-focused UI. No design system library is needed. Custom CSS gives complete control over the exact aesthetic without fighting framework defaults. The layout is straightforward: a header nav bar, a grid of project cards on the Home page, a vertical sequence of clip sections in the workspace, and a few overlays (modals, settings panel). All achievable with Flexbox and CSS Grid.

- **No CSS framework or component library**
  - Why: The specs do not require a large component library (no data tables, no complex form controls, no marketing landing pages). The UI is focused: text areas, video players, buttons, cards, and overlays. Adding Tailwind or Bootstrap would introduce hundreds of unused classes and override battles. Custom CSS keeps the bundle small and the design intentional.
  - Trade-off: No pre-built accessible components. Every button, input, modal, and focus state must be manually styled and tested for accessibility. Acceptable because this is a solo tool with a single user who knows how it works. ARIA attributes and keyboard navigation are still implemented but not battle-tested across assistive technologies.

---

## 4. Backend & API Layer

- **Django 5.1+**
  - Purpose: HTTP server, URL routing, view logic, template rendering, ORM for database access, file handling, business logic for script generation, video assembly, and AI API coordination
  - Why chosen: Django is the most complete Python web framework. It includes everything needed for this project: an ORM (no need for SQLAlchemy), a migration system, a template engine, built-in form handling, file upload handling, static file serving, a development server, and an admin interface (useful for debugging project state). The specs require creating projects, generating scripts, managing video files, assembling reels, and coordinating multiple AI API calls — Django's "batteries included" philosophy means no hunting for external libraries to fill gaps.
  - Trade-off: Django is heavier than Flask or FastAPI. But the specs do not require microsecond response times or stripped-down minimalism — they require a complete, reliable system for managing multi-step AI workflows. Django's maturity and completeness eliminate entire categories of bugs and edge cases that would require manual handling in a lighter framework.

- **Plain Django views with JsonResponse**
  - Purpose: AJAX endpoints for video generation, script regeneration, clip updates, and status polling — any operation triggered from the frontend without a page reload
  - Why chosen: Simplicity. Django's built-in JsonResponse handles all AJAX needs without additional dependencies. For a solo dev tool, plain Django views returning JSON are sufficient. No need for DRF's serializers, ViewSets, or browsable API when there is one developer who knows the endpoints.
  - Trade-off: More manual JSON formatting compared to DRF, but the API surface is tiny (10-15 endpoints max). The simplicity wins for a personal tool.

- **Python threading for long-running tasks**
  - Purpose: handle long-running AI operations (video generation: 11s–6min per clip, image generation, script generation) without blocking the HTTP response
  - Why chosen: For a development-only solo tool, Python's built-in `threading` module is sufficient. Django views spawn threads for AI calls, store task status in the database, and return immediately. The frontend polls a status endpoint. No external dependencies (Celery, Redis), no separate worker processes, no message broker. Just Python threads and SQLite.
  - Trade-off: Threading is less robust than Celery (threads can die silently, no automatic retry, limited concurrency control). But for a solo user generating 1-2 videos at a time, threading is adequate. If threading proves problematic, migration to Celery is straightforward.

---

## 5. Database & Storage

- **SQLite 3**
  - Purpose: persistent storage for all application data — projects (title, description, visual style, settings), clips (scripts, video file paths, generation metadata), reference images (file paths, labels), hooks, settings, and task status
  - Why chosen: User preference. SQLite is a self-contained, zero-configuration, file-based database. No separate server process, no connection pooling, no network latency. Perfect for a single-user tool. Django's ORM supports SQLite out of the box. The data volume is tiny: a few hundred projects at most, each with 5–10 clips, 3 reference images, and metadata. SQLite handles this effortlessly.
  - Data it stores: Projects table (title, description, visual_style, aspect_ratio, clip_duration, num_clips, created_at, updated_at), Clips table (project_id FK, sequence_number, script_text, video_file_path, generation_status, generation_method), ReferenceImages table (project_id FK, slot_number, image_file_path, label), Hooks table (project_id FK, script_text, video_file_path, enabled), Settings table (singleton row with default_aspect_ratio, default_clip_duration, default_visual_style, video_quality, generation_speed)
  - Trade-off: SQLite does not support concurrent writes (only one write transaction at a time). But the specs explicitly state this is a single-user tool with no concurrent modification conflicts. SQLite's write serialization is invisible to a solo user. If this ever becomes multi-user, migration to PostgreSQL is straightforward (Django ORM abstracts the database).

- **Local file system storage**
  - Purpose: storage for all generated media files — video files (.mp4), reference images (.png/.jpg), transition frame images, and assembled reel exports
  - Why chosen: User preference. The specs state: "Storage of videos will use the local machine storage system." Django's FileField and ImageField handle file uploads and storage with zero configuration. Files are stored in a `MEDIA_ROOT` directory (default: `media/` in the project root), organized by type (videos/, images/, reels/). File paths are saved in the database; files are served via Django's static file serving in development and a simple web server (nginx or Whitenoise) in production.
  - Trade-off: No built-in redundancy or backup. If the hard drive fails, all videos are lost. Acceptable for a personal tool where the user controls backups. If deployed to a server, standard server backup procedures apply. Cloud storage (S3) would add latency, complexity, and cost for zero benefit in a solo tool.

---

## 6. Authentication & Authorization

- **None**
  - Why: User preference and specs explicitly state: "No authentification. This is a solo tool." The tool runs locally or on a private server accessible only to the user. No login screen, no user accounts, no password hashing, no session management, no CSRF tokens, no OAuth flows. Django's authentication system is completely disabled.
  - Trade-off: If the tool is ever exposed to a network where others can access it, there is zero security. Acceptable because the specs assume private deployment. If network security is needed later, HTTP basic auth (via nginx or Apache) or a single hardcoded login added to Django settings would suffice before implementing full user accounts.

---

## 7. Third-Party Services & Integrations

- **Google Gemini API (google-genai Python SDK)**
  - Purpose: all AI generation — text (script generation via Gemini 3 Flash), images (reference images and transition frames via Nano Banana), and videos (clip generation via Veo 3.1)
  - Triggered by: User clicks "Generate Scripts", "Generate Video", "Regenerate Script", "Generate Reference Image", "Generate Transition Frame", "Generate Hook Script", "Generate Hook Video", or "Extend Clip"
  - Spec reference: Section 5.2 (AI Script Generation), Section 5.3 (Video Generation), Section 5.4 (Reference Images), Section 5.5 (Transition Frames), Section 5.7 (Hook). Every AI operation in the specs maps to a Gemini API call.
  - Alternatives considered: OpenAI (GPT-4 for text, DALL-E for images, no video generation), Anthropic (Claude for text, no image or video), Stability AI (Stable Diffusion for images, no video). Rejected because the user explicitly specified "All AI generations will be with gemini." Gemini is also the only API offering video generation (Veo 3.1) integrated into a single SDK.
  - Pricing model: Gemini API is pay-per-use. Text generation (Gemini 3 Flash) is $0.10 per 1M input tokens, $0.40 per 1M output tokens. Image generation (Nano Banana) pricing TBD but expected to be competitive with DALL-E 3 (~$0.04 per image). Video generation (Veo 3.1) pricing TBD but expected to be the most expensive operation. No free tier for production use. The user pays per API call. For a personal tool generating a few reels per week, monthly costs are estimated at $10–$50 depending on iteration frequency.

- **SQLite for task status tracking**
  - Purpose: store status and results of long-running tasks (video generation, image generation, script generation, video assembly) for polling
  - Triggered by: Every background job initiated from the frontend
  - Spec reference: Background jobs are implicit in the specs' requirement for non-blocking generation with live status indicators (Section 4.3 and Section 8.2 loading states)
  - Why chosen: No external dependencies. A simple `Tasks` table stores task ID, status (pending/running/completed/failed), progress percentage, result data, and error messages. Django views update the table, frontend polls a status endpoint. Perfectly adequate for a solo dev tool.
  - Trade-off: SQLite write serialization means task status updates are slightly slower than Redis (milliseconds vs. microseconds). Imperceptible for a single user.

---

## 8. Infrastructure & Deployment

- **Development-only deployment (Django's runserver)**
  - Purpose: run the application on the developer's machine
  - Why chosen: This is a personal dev tool with no production deployment requirements. `python manage.py runserver` provides everything needed: auto-reload on code changes, detailed error pages, static file serving, and SQLite database access.
  - How to run: Activate `.venv`, run `python manage.py runserver`, open `http://127.0.0.1:8000` in browser. That's it.
  - No production server (no Gunicorn, no nginx, no systemd services).
  - No CI/CD pipeline.
  - No domain, no DNS, no SSL/TLS. Always runs on localhost.
  - Settings: DEBUG=True always. ALLOWED_HOSTS includes localhost and 127.0.0.1.

- **Git version control**
  - Purpose: sync code between two development machines
  - Why chosen: The user works on two different computers and needs to push changes from one machine and pull them on the other. Git provides this with a remote repository (GitHub, GitLab, or self-hosted).
  - Workflow: Commit changes locally, push to remote (`git push`), pull on the other machine (`git pull`). No branching strategy needed (single developer, no collaboration).
  - The `.env` file (with the Gemini API key) is gitignored — must be manually copied to the second machine or recreated.

---

## 9. Monitoring, Logging & Observability

- **Python logging module (built into Python)**
  - Purpose: application logs — errors, warnings, info messages for debugging script generation logic, video assembly, API calls
  - What it monitors: Django request errors, Celery task failures, Gemini API errors, file I/O errors, database errors
  - Why chosen: Lightweight, requires no external service. Logs are written to a file (logs/reelforge.log) and/or stdout. The user can tail the log file to see what is happening. For a personal tool, this is sufficient.

- **Django Debug Toolbar (development only)**
  - Purpose: in-browser debugging panel showing SQL queries, request/response data, template rendering time
  - Why chosen: Makes Django development faster. The user can see exactly what database queries are running, why a page is slow, and what templates are being rendered. Disabled in production.

- **No external monitoring, uptime alerts, or APM**
  - Why: This is a personal tool on a private server. If it breaks, the user notices immediately because they are the only user. No need for PagerDuty, Sentry, or Datadog. If error tracking becomes useful, Sentry's free tier (5,000 events/month) can be added later by installing `sentry-sdk` and adding 5 lines to Django settings.

---

## 10. Developer Tooling & Code Quality

- **Python 3.12**
  - Purpose: runtime for Django, Celery, and all business logic
  - Why chosen: User preference (from workspace context). Python 3.12 is the latest stable version with performance improvements and modern syntax.

- **pip + .venv (virtual environment)**
  - Purpose: isolated Python dependency management
  - Why chosen: User preference from memory notes ("never install Python dependencies globally"). All Python packages are installed inside `.venv` using `python -m pip`.

- **Black (code formatter)**
  - Purpose: automatic Python code formatting — consistent style, no manual formatting debates
  - Why chosen: Standard in the Python community. Opinionated and deterministic. Run via `black .` before committing.

- **Flake8 (linter)**
  - Purpose: catch Python code smells, unused imports, undefined variables, style violations
  - Why chosen: Lightweight, fast, well-integrated with Django. Run via `flake8 .` before committing.

- **isort (import sorter)**
  - Purpose: automatically organize Python imports (standard library, third-party, internal) and remove unused ones
  - Why chosen: Complements Black. Run via `isort .` before committing.

- **pytest + pytest-django (testing framework)**
  - Purpose: unit tests for Django views, models, business logic, Celery tasks; integration tests for API calls to Gemini (mocked)
  - Why chosen: pytest is the modern Python testing standard. Cleaner syntax than unittest. pytest-django integrates seamlessly with Django's test database and fixtures.

- **pre-commit (Git hooks)**
  - Purpose: automatically run Black, Flake8, and isort before every commit to prevent committing broken or badly formatted code
  - Why chosen: Enforces code quality without manual steps. Configured in .pre-commit-config.yaml.

- **Local development setup**
  - Dev server: `python manage.py runserver` (hot reload enabled)
  - Seed data: Django management command `python manage.py seed_dev_data` creates sample projects for testing
  - Database migrations: `python manage.py makemigrations` and `python manage.py migrate`
  - No separate processes needed (no Celery workers, no Redis server)

- **No TypeScript, no build step**
  - Why: jQuery and vanilla JavaScript are written directly, served as static files. No compilation. No webpack, no Vite, no Babel. The user edits a .js file, refreshes the browser, and sees the changes immediately.

---

## 11. Security Considerations

This section describes how the stack addresses security across layers. No new tools are introduced — this explains how the tools already chosen address security requirements from the specs.

- **How user input is validated and sanitized**: All user input (project titles, descriptions, visual styles, clip scripts) flows through Django forms or DRF serializers, which validate data types, lengths, and required fields. Django templates auto-escape HTML output, preventing XSS. All database writes use Django ORM parameterized queries, preventing SQL injection. User-uploaded images are validated by file extension and MIME type (via Django's ImageField) to prevent malicious uploads.

- **How secrets and credentials are managed**: The Gemini API key is stored in a `.env` file (gitignored) and loaded into Django settings via `python-decouple` or `django-environ`. The key is never hardcoded in source code. In production, the `.env` file is placed on the server with restrictive file permissions (chmod 600).

- **How API endpoints are protected**: Since there is no authentication system, all endpoints are "public" to whoever has access to the server. In a local deployment, the server binds to `127.0.0.1` (localhost only), preventing network access. In a private server deployment, the server is behind a firewall or VPN. If the tool is ever exposed to the internet, HTTP basic auth is added via nginx configuration. No CSRF protection is enabled since there are no user accounts or sessions to hijack.

- **How data is encrypted**: At rest: not encrypted (SQLite database and media files are stored in plaintext on the file system). Acceptable for a personal tool on a machine the user controls. If the machine is shared, full-disk encryption (BitLocker on Windows, LUKS on Linux) provides OS-level protection. In transit: HTTPS (TLS 1.3) encrypts all traffic between the browser and server if the tool is deployed with a domain and SSL certificate. Not required for localhost deployment.

- **How dependencies are audited for vulnerabilities**: `pip-audit` scans Python dependencies for known CVEs. Run manually before deploying: `pip-audit`. Django's security releases are monitored via the Django security mailing list. All dependencies are pinned in `requirements.txt` to prevent surprise breakage from upstream updates.

- **How access control is enforced at the data layer**: Not applicable. There is only one user, and they have full access to everything. No row-level security, no permissions system, no middleware checks. Django's admin interface is disabled in production to prevent accidental exposure.

---

## 12. Feature-to-Stack Mapping

For every major feature area from FEATURE_SPECS.md, this section lists the tools involved and how they work together.

**Home & Project Management (Section 5.1)**
- Tools: Django (views, ORM, templates), SQLite (projects table), jQuery (AJAX for delete/rename/duplicate actions)
- How they work together: Django renders the Home page template with a list of all projects from the database. Each project card shows data from the Projects table. Clicking "New Project" loads a Django form. Submitting the form saves a new Project record and triggers script generation via Celery. Three-dot menu actions (duplicate, rename, delete) send AJAX requests to Django endpoints that update or delete database records and return JSON confirmation.
- Notes: Search functionality (Section 6.2) is a Django ORM query filtering by project title.

**AI Script Generation (Section 5.2)**
- Tools: Django (orchestration), Python threading (background execution), Gemini API (text generation via google-genai SDK), SQLite (clips table and task status table)
- How they work together: User submits the New Project form. Django creates a Project record, creates a Task record (status: pending), spawns a Python thread to call the Gemini API, and redirects to the workspace with a "Generating scripts..." loading state. The thread calls the Gemini API with the project description and visual style, receives 5–10 clip scripts, saves them to the Clips table, updates the Task record (status: completed), and exits. The frontend polls a Django status endpoint every 2 seconds, which queries the Task table and returns JSON. For single-script regeneration or manual editing, the same flow applies but updates only one Clip record.
- Notes: All scripts for a project are sent as context to the Gemini API to maintain narrative coherence (Section 13 assumptions).

**Video Generation (Section 5.3)**
- Tools: Django (orchestration), Python threading (background execution), Gemini Veo API (video generation), local file system (video storage), SQLite (clips table for video_file_path and status, tasks table), jQuery (status polling)
- How they work together: User clicks "Generate Video" on a clip. jQuery sends an AJAX request to a Django endpoint with the clip ID, script, generation method, selected reference images, and project settings (aspect ratio, duration, resolution). Django creates a Task record, spawns a thread, and returns the task ID. The frontend polls a status endpoint every 2 seconds. The thread calls the Veo API with the script and references, waits for video generation (11s–6min depending on resolution), downloads the resulting MP4 to the local file system (media/videos/), saves the file path to the Clip record, updates the Task record (status: completed), and exits. The frontend receives the completion status, updates the clip's video player with the new file path (served by Django as a static file), and shows a success toast notification.
- Notes: All five generation methods (text-to-video, image-to-video, frame interpolation, extend from previous clip, video extension) use the same threading architecture but call different Veo API endpoints. Video extension chains off the previous generation's Veo reference ID stored in the Clip record.

**Reference Images (Section 5.4)**
- Tools: Django (orchestration), Python threading (background execution), Gemini Nano Banana API (image generation), local file system (image storage), SQLite (reference_images table, tasks table), jQuery (AJAX updates)
- How they work together: User clicks "Generate" in a reference image slot and enters a prompt. jQuery sends an AJAX request to Django with the prompt and slot number. Django creates a Task record, spawns a thread, and returns the task ID. The thread calls the Nano Banana API, downloads the resulting image to the local file system (media/images/references/), saves the file path and label to the ReferenceImages table, updates the Task record, and exits. The frontend polls for status, then updates the slot's thumbnail with the new image (served by Django). For image upload, the same flow applies but skips the Nano Banana API — Django handles the upload via a form and saves the file directly.
- Notes: Reference images are linked to a project (project_id FK) and selected per-clip via a checkboxes interface. The selected reference IDs are passed to the Veo API as part of the video generation request.

**Transition Frames (Section 5.5)**
- Tools: Django, Python threading, Gemini Nano Banana API, local file system, SQLite (transition_frames table, tasks table), jQuery
- How they work together: User clicks "Generate Transition Frame" between two clips. Django creates a Task record, spawns a thread with the two clip IDs, and returns the task ID. The thread reads both clips' scripts, calls the Nano Banana API twice (once for the last frame of the upper clip, once for the first frame of the lower clip), downloads both images to the local file system, saves their paths to the TransitionFrames table (or a frames column in the Clips table), updates the Task record, and exits. The frontend polls for status, then updates the connector area with the two frame thumbnails. These frames are then available as options in the "Set First Frame" or "Set Last Frame" selectors when the user generates those clips with frame interpolation.

**Reel Assembly & Export (Section 5.6)**
- Tools: Django (orchestration), Python threading (background execution), FFmpeg (video concatenation), local file system (assembled reel storage, clip video files), SQLite (projects table, clips table for video paths and order, tasks table), jQuery (AJAX trigger and status polling)
- How they work together: User clicks "Download Reel". jQuery sends an AJAX request to Django with the project ID. Django checks that all clips have video files, creates a Task record, spawns a thread, and returns the task ID. The thread retrieves all Clip records for the project ordered by sequence_number, optionally prepends the Hook video if the hook is enabled, uses FFmpeg to concatenate all video files in order (via `ffmpeg -f concat -i filelist.txt -c copy output.mp4`), saves the assembled reel to the local file system (media/reels/), updates the Task record with the file path, and exits. The frontend polls for status, then triggers a browser download by setting `window.location.href` to the assembled reel's URL.
- Notes: Individual clip download is a simple Django view that serves the clip's video file with a Content-Disposition header set to attachment. No threading needed.

**Hook (Section 5.7)**
- Tools: Same as AI Script Generation and Video Generation (Django, Python threading, Gemini API, local file system, SQLite)
- How they work together: After all clips have videos, the workspace frontend shows a "Generate Hook Script" button. Clicking it sends an AJAX request to Django with the project ID. Django creates a Task record, spawns a thread that reads all clip scripts, calls the Gemini API with a prompt template for hook script generation, receives a 4-second hook script, saves it to the Hooks table (project_id FK, script_text), updates the Task record, and exits. The frontend polls for status, then displays the hook script in an editable text area. Generating the hook video follows the same flow as regular clip video generation but uses the Hooks table and sets duration to 4 seconds. The hook's enabled toggle is a boolean field in the Hooks table that Django reads during reel assembly to decide whether to prepend the hook video.

**Settings (Section 4.6, Section 5.8)**
- Tools: Django (views, forms, ORM), SQLite (settings table with a singleton row), jQuery (AJAX save)
- How they work together: The settings panel is rendered by Django from the Settings table. User changes a setting (e.g., default aspect ratio). jQuery sends an AJAX request to Django with the updated field. Django updates the Settings record and returns JSON confirmation. The frontend shows a brief "Settings saved" toast notification. New projects read from the Settings table to pre-fill form defaults.

**Project Workspace UI (Section 4.3)**
- Tools: Django templates (server-side rendering of clip sections), jQuery (drag-and-drop for clip reordering via jQuery UI Sortable), vanilla JavaScript (video player controls, scrubber bar interactions, modal toggling), SQLite (clips table for sequence_number updates)
- How they work together: Django renders the workspace page with all clip sections in order. jQuery UI Sortable makes the clip list draggable. When the user drops a clip in a new position, jQuery sends an AJAX request to Django with the new order (array of clip IDs). Django updates the sequence_number field for all affected Clip records and returns JSON confirmation. The frontend does not reload the page — the new order persists in the database for the next page load. Video players are HTML5 `<video>` elements with vanilla JavaScript event listeners for custom controls.

**Reel Preview (Section 4.4.1)**
- Tools: Django template (full-screen overlay), vanilla JavaScript (video playback sequencing, scrubber bar click handling), HTML5 video element
- How they work together: User clicks "Preview Reel". Django loads the preview overlay template with a list of all clip video URLs plus the hook video URL if enabled. Vanilla JavaScript plays the videos in sequence using the `ended` event to trigger the next video. The scrubber bar is an SVG or div with click event listeners that calculate which clip was clicked based on click position and jump to that clip's video by setting the current video's `src` and calling `play()`.

**Clip Reordering (Section 4.3.6)**
- Tools: jQuery UI Sortable, Django (AJAX endpoint to save new order), SQLite (clips table sequence_number updates)
- How they work together: Described above in "Project Workspace UI".

**Background Job Status Polling**
- Tools: Django (status endpoint), SQLite (tasks table), jQuery (polling loop)
- How they work together: When the frontend triggers a background job (video generation, script generation, etc.), Django returns a task ID. The frontend starts a polling loop: every 2 seconds, jQuery calls a Django status endpoint with the task ID. Django queries the Tasks table for the task's current status and any result data (progress percentage, elapsed time, completion, error). Django returns JSON with the status. The frontend updates the UI (progress bar, status text, elapsed time counter). When the task completes (status changes to 'completed'), the frontend stops polling and updates the UI with the result (e.g., displays the generated video).

---

## 13. Gaps, Risks & Deferred Decisions

### Gaps

- **Video format compatibility**: The specs assume Veo generates MP4 files compatible with Instagram and TikTok. If Veo outputs a different codec or container format, FFmpeg transcoding will be needed during assembly. This is a known risk but cannot be validated until Veo API access is confirmed.

- **Thread error handling**: Video generation threads can fail silently if not properly wrapped in try-except blocks. The system needs robust error handling to ensure thread failures are caught, logged to the Tasks table (status: failed, error message), and surfaced to the frontend. This will be implemented during development.

- **API timeout handling**: Video generation can take up to 6 minutes. The Veo API might have its own timeout or rate limits. The system does not yet have retry logic for transient API failures. This will be added once API behavior is observed in practice.

### Risks

- **Veo API availability and pricing**: Veo 3.1 is in preview as of the FEATURE_SPECS.md date. API pricing is not publicly finalized. If pricing is prohibitively expensive (e.g., $1+ per video), the user may need to switch to a cheaper model or reduce iteration frequency. Mitigation: Use Veo 3.1 Fast for drafts, reserve the quality model for final renders only.

- **Thread pool exhaustion**: Python threads are lightweight but not unlimited. If the user triggers 10+ video generations simultaneously, thread creation could slow down or fail. Mitigation: limit concurrent threads using a ThreadPoolExecutor with max_workers=5. Queue additional requests in the database (status: pending) and process them as threads become available.

- **SQLite write lock contention**: If multiple threads attempt to update the Tasks table simultaneously, SQLite's write serialization could cause brief delays. Mitigation: wrap database writes in transactions and accept that updates are queued (milliseconds). For a solo user, this is imperceptible.

- **Gemini API rate limits**: The Gemini API has rate limits (exact limits TBD, vary by model). If the user triggers rapid-fire generation (e.g., regenerating all 7 clips at once), they might hit the limit. Mitigation: implement exponential backoff retry logic in the generation threads. Display a user-facing error message: "API rate limit reached. Please wait 30 seconds and try again."

- **Local storage capacity**: High-resolution videos (4K, extended to 148 seconds) are large (500MB+ per clip). A project with 10 extended 4K clips could consume 5GB+. If the user creates dozens of projects, local storage fills up. Mitigation: the user manages their own storage. A future feature could add a "Delete old videos" button or automatic cleanup of videos older than 30 days.

### Deferred to V2

- **Batch generation**: Generate all 7 clips at once with one click. Not needed for V1 because the user reviews each clip individually (Section 12 out of scope). When added, this will spawn 7 threads (or use ThreadPoolExecutor to limit concurrency) and track 7 separate task IDs.

- **Version history per clip**: Undo to a previous generation. Not needed for V1 (Section 12 out of scope). When added, this will require storing multiple video files per clip and adding a version selector UI.

- **Custom transition effects (crossfade, wipe, zoom)**: Not needed for V1 (Section 12 out of scope). When added, FFmpeg's `xfade` filter will handle this during assembly.

- **Production deployment**: Not needed for V1 (dev-only tool). If the user later wants to deploy to a server, this would require Gunicorn, nginx, proper async task handling (migrate to Celery), and security hardening. Out of scope for a dev machine tool.

---

## 14. Rejected Alternatives

**React / Vue / Svelte (modern frontend frameworks)**
- Category: frontend
- Why rejected: User explicitly prefers jQuery and vanilla JavaScript. React would require a build step (Vite, webpack), a state management library (Redux, Zustand), and learning a new paradigm (components, hooks). The specs do not require complex client-side state or instant reactivity — the UI is mostly static with async updates triggered by AJAX. jQuery and vanilla JS fully cover the requirements with zero build step and zero learning curve for a developer familiar with these tools.
- When it might be reconsidered: If the tool becomes multi-user with real-time collaborative editing (multiple users editing the same project simultaneously), React or Vue with WebSockets would provide better UX than jQuery polling. Not in scope for V1.

**FastAPI / Flask (lighter Python frameworks)**
- Category: backend
- Why rejected: Django's batteries-included philosophy eliminates dozens of decisions and third-party libraries. Flask would require adding SQLAlchemy (ORM), Alembic (migrations), Flask-WTF (forms), a template engine (Jinja2 is built in, but Flask has no form handling or admin interface), and manual file upload handling. FastAPI would require the same plus async/await everywhere, which adds complexity without benefit (the specs do not require websockets or async I/O — all "async" operations are background jobs via Celery, which works the same in Django and FastAPI). Django's admin interface is valuable for debugging project state. The ORM, migration system, and form handling save weeks of boilerplate.
- When it might be reconsidered: If the tool needs to handle thousands of concurrent WebSocket connections for real-time updates, FastAPI's async I/O would outperform Django. Not relevant for a solo tool.

**PostgreSQL / MySQL (client-server databases)**
- Category: database
- Why rejected: User explicitly prefers SQLite. PostgreSQL requires a separate database server process, connection pooling configuration, backup scripts, and network configuration. Overkill for a single-user tool with minimal data volume. SQLite is simpler and perfectly capable.
- When it might be reconsidered: If the tool becomes multi-user with concurrent writes, PostgreSQL's MVCC (multi-version concurrency control) would eliminate write lock contention. Also, if the database grows beyond 1GB, PostgreSQL's performance would scale better. Not relevant for V1.

**AWS S3 / Cloudinary (cloud file storage)**
- Category: storage
- Why rejected: User explicitly prefers local file storage. Cloud storage adds latency (upload/download time), cost ($0.023/GB/month for S3 + data transfer fees), and complexity (IAM credentials, boto3 SDK, pre-signed URLs). The specs state the tool is personal and runs locally or on a private server. Local file system is simpler, faster, and free.
- When it might be reconsidered: If the tool is deployed to multiple servers for redundancy, S3 would provide a shared storage layer. Also, if the user wants to access videos from multiple devices without syncing files manually, S3 would help. Not relevant for V1.

**Next.js / Nuxt (full-stack frameworks)**
- Category: architecture
- Why rejected: These are JavaScript-first frameworks. The user wants Django for the backend, and the Gemini SDK is Python-first. Next.js would require duplicating the backend in Node.js (no Django) or running a separate Python API server (two servers instead of one). Adds complexity, deployment overhead, and splits the codebase into two languages. Django SSR (server-side rendering with templates) provides the same SEO and initial page load benefits without the JavaScript framework overhead. The specs do not require SEO (private tool), instant client-side navigation, or a marketing site — all the features that justify Next.js.
- When it might be reconsidered: If the tool needs a public-facing landing page with marketing content, blog, and SEO-optimized pages, Next.js would shine. Not relevant for a solo tool with no public presence.

**Tailwind CSS / Bootstrap (CSS frameworks)**
- Category: styling
- Why rejected: The specs describe a minimal, dark-themed, production-focused UI with a small set of components (cards, buttons, text areas, video players, modals). Tailwind's utility-first approach works best for rapid prototyping with a design system library (like Tailwind UI or DaisyUI). Here, there is no design system — every component is custom. Tailwind would add hundreds of unused classes and a build step (PostCSS to purge unused classes). Bootstrap's default theme is bright, blue, and marketing-focused — the opposite of the dark, minimal aesthetic in the specs. Custom CSS gives full control without fighting framework defaults.
- When it might be reconsidered: If the tool expands to include a public-facing landing page, marketing site, or documentation portal, Tailwind would accelerate development. Not relevant for V1, which is purely a production tool interface.

**WebSockets (real-time communication)**
- Category: backend communication
- Why rejected: The specs require live status updates for video generation, but polling is sufficient. WebSockets add complexity (Django Channels, Redis as a channel layer, client-side reconnection logic) for marginal UX improvement (polling every 2 seconds feels instant to a human). WebSockets are justified for chat apps, collaborative editors, or gaming where latency matters. Here, waiting 11 seconds to 6 minutes for video generation renders the difference between 2-second polling and instant WebSocket push irrelevant.
- When it might be reconsidered: If the tool becomes multi-user with real-time collaborative script editing (Google Docs style), WebSockets would enable instant synchronization. Not in scope for V1.

**Docker / Kubernetes (containerization)**
- Category: deployment
- Why rejected: This is a personal tool running on a single server. Docker adds a layer of abstraction and complexity (Dockerfile, docker-compose.yml, volume mounts, networking) for zero benefit when the target environment is a single Linux machine the user controls. The user can install Python, Redis, and nginx directly on the machine. No need for orchestration, service discovery, or horizontal scaling. Docker makes sense for teams with heterogeneous dev environments or multi-service architectures. Here, it is over-engineering.
- When it might be reconsidered: If the tool is packaged for easy distribution to non-technical users ("download and run ReelForge on any machine"), Docker would provide a one-command installation. Also useful if the tool expands to multiple services (e.g., a separate video processing service, a separate AI service). Not relevant for V1.
