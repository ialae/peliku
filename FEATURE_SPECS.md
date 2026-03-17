# Feature Specifications — Peliku

## 1. Product Vision

Peliku is a personal web-based tool for creating viral short-form video reels ready to post on Instagram and TikTok. Today, producing a cohesive 60-second reel requires juggling multiple AI tools, manually writing prompts that stay visually consistent across clips, and stitching everything together — a tedious, error-prone process that breaks creative flow. Peliku eliminates that friction: describe your reel idea in plain language, and AI instantly writes seven detailed, visually coherent clip scripts that share a unified narrative thread, consistent characters, environment, color palette, and mood. Then generate, preview, refine, and assemble every clip — all in one place — and download the final reel as a single MP4 file.

---

## 2. Target Users

### 2.1 Primary User

- A solo content creator who produces short-form video content for Instagram Reels and TikTok
- Comfortable with AI tools and prompt-based workflows but frustrated by the manual coordination required to keep seven separate AI video clips visually and narratively coherent
- Currently solves this by writing prompts one at a time in separate tools, copying style notes between them, generating videos individually, then importing everything into a video editor to stitch clips together
- Success looks like: going from a rough idea to a downloadable, post-ready 60-second reel entirely inside one tool, with full control over each clip, without ever leaving the browser
- Uses the tool several times per week, whenever a new reel idea strikes

### 2.2 Anti-Users

- Teams or agencies looking for multi-user collaboration, approval workflows, or shared asset libraries — this is a personal power tool, not a team platform
- Users who need direct publishing to Instagram or TikTok from within the tool — Peliku produces a downloadable file; publishing happens separately
- Users looking for a fully automated "one-click reel" generator with no creative control — Peliku is designed for creators who want to steer every clip

---

## 3. Core Value Propositions

- Users can describe a reel idea in a few sentences so that AI breaks it into seven coherent, production-ready clip scripts in seconds
- Users can maintain visual consistency (characters, colors, environment, mood) across all seven clips so that the final reel feels like a single cohesive story, not a random collage
- Users can generate, preview, and regenerate any individual clip without affecting the others so that they keep full creative control over every moment of the reel
- Users can use AI-generated reference images to lock the appearance of characters and key objects so that they look the same across all seven clips
- Users can use frame interpolation between clips so that transitions feel smooth and cinematic rather than jarring cuts
- Users can extend any clip beyond its initial duration so that important moments get the screen time they deserve
- Users can reorder, replace, or adjust any clip at any point so that the creative process stays fluid and non-destructive
- Users can generate an AI-crafted hook clip that is placed at the very beginning of the reel so that viewers stop scrolling and watch the full video
- Users can download the assembled reel as a single MP4 file in portrait format so that it is immediately ready to upload to Instagram or TikTok

---

## 4. User Journey

### 4.1 Discovery & First Impression

- The user opens the app in their browser (bookmarked URL or typed address)
- The landing screen is the Home page — a clean grid of the user's previous reel projects, sorted by most recently edited
- If this is the user's first visit, the Home page shows an empty state with a friendly message and a prominent button to create the first project
- The overall feel is minimal, dark-themed, and production-focused — like a filmmaker's workbench, not a social media dashboard

### 4.2 Creating a New Project

- The user clicks the "New Project" button visible on the Home page
- A creation form appears with the following fields:
  - **Title** — a short name for the reel project (required, plain text, maximum 100 characters)
  - **Description** — a free-form text area where the user describes the reel idea: the story, the vibe, the setting, characters, the message, the emotion they want to evoke (required, plain text, maximum 2,000 characters)
  - **Aspect Ratio** — a toggle to choose between Portrait (9:16, the default, optimized for Reels/TikTok) or Landscape (16:9)
  - **Clip Duration** — a choice of how long each individual clip should be: 4 seconds, 6 seconds, or 8 seconds (default: 8 seconds)
  - **Visual Style** — an optional text field where the user can specify a global visual style directive that applies to every clip (for example: "cinematic film grain, warm golden-hour tones, shallow depth of field"). Maximum 500 characters. If left empty, AI infers the style from the description.
  - **Number of Clips** — defaults to 7, but the user can choose 5, 6, 7, 8, 9, or 10 to control reel length
- The user fills in the fields and clicks "Generate Scripts"
- A loading state appears with a progress message: "Writing your clip scripts..."
- After AI finishes, the user is taken to the Project Workspace

### 4.3 Core Workflow — Project Workspace (Script Review & Video Generation)

This is the primary screen where all creative work happens. It is organized as a vertical sequence of clip sections, one for each clip in the reel.

**Initial State (Scripts Only, No Videos Yet)**

- At the top of the workspace: the project title, description summary, and global settings (aspect ratio, clip duration, visual style) displayed as a compact, editable header bar
- Below the header: a horizontal **Reference Images Panel** (collapsed by default, expandable). This is where the user can generate and manage up to 3 reference images that will be attached to every clip generation to maintain visual consistency (characters, key objects). More detail in Section 4.3.2.
- Below that: the clip sections, arranged vertically in order (Clip 1 through Clip 7, or however many were chosen)

**Each Clip Section contains two side-by-side panels:**

- **Left Panel — Script/Prompt**
  - Displays the AI-generated detailed prompt for this clip
  - The prompt is fully editable as a text area — the user can modify any part of it
  - Below the text area:
    - A "Regenerate Script" button that asks AI to rewrite just this clip's script while keeping it consistent with the other clips
    - A character count indicator
  - The script includes all Veo-relevant details: subject, action, camera motion, composition, lighting, color palette, ambient sounds, dialogue (if any), and how it connects to the previous and next clips

- **Right Panel — Video**
  - Initially shows an empty placeholder with a large "Generate Video" button
  - Once a video is generated, the placeholder is replaced by a video player showing the clip
  - Below the video player:
    - A "Regenerate Video" button to generate a new video from the current script
    - An "Extend Clip" button to add 7 more seconds to the clip using Veo Video Extension
    - A "Generation Method" dropdown (see Section 4.3.1 for details)
    - A status indicator showing: idle, generating (with elapsed time), completed, or failed with an error message

**Between each pair of consecutive clip sections**, a thin horizontal connector line with a small icon indicates the narrative flow. A "Generate Transition Frame" button sits on this connector — clicking it generates a last-frame image for the clip above and a first-frame image for the clip below, enabling smooth frame interpolation between clips (see Section 4.3.3).

#### 4.3.1 Generation Methods

When generating a video for a clip, the user can choose from several methods via the "Generation Method" dropdown on the right panel:

- **Text-to-Video (default)** — generates the clip purely from the script prompt. Simplest method, good for first drafts.
- **Image-to-Video** — uses a starting frame image (either AI-generated or uploaded by the user) as the first frame, then animates it according to the script. The user clicks a "Set First Frame" button that opens a sub-panel where they can:
  - Generate a first-frame image from the script using AI image generation
  - Upload their own image from their computer
  - Use the last frame of the previous clip (if available) for continuity
- **Frame Interpolation** — specifies both a first frame and a last frame, and generates a video that smoothly transitions between them according to the script. The user provides:
  - The first frame (generated, uploaded, or pulled from the previous clip's last frame)
  - The last frame (generated, uploaded, or pulled from the next clip's first frame)
  - This method is ideal for ensuring seamless visual continuity between clips
- **Extend from Previous Clip** — instead of generating this clip independently, the user extends the previous clip's video into this clip's time slot. This creates the most seamless possible transition because the new footage literally grows out of the previous clip's video. How it works:
  - Available only on Clip 2 and above (there is no previous clip for Clip 1)
  - Requires that the previous clip already has a generated video
  - The current clip's script is used as the extension prompt — it describes what happens next after the previous clip ends
  - The AI video service takes the previous clip's generated video and appends new footage guided by the current clip's script
  - The result is a single combined video that contains both the previous clip's content and the new extension
  - The system automatically splits the combined video at the boundary: the previous clip keeps its original portion, and the newly extended portion becomes the current clip's video
  - Resolution is locked to 720p for extensions (a constraint of the video generation engine)
  - This method is the strongest tool for narrative and visual continuity — ideal for clips that continue the same scene, follow the same character's movement, or maintain an unbroken camera motion across a cut point
  - The user can chain this across multiple consecutive clips (for example: generate Clip 1 with Text-to-Video, then generate Clip 2, 3, and 4 each using "Extend from Previous Clip") to produce a long, unbroken sequence that is later split into individual clip segments

For every generation method, the clip section shows a "References" selector below the generation method dropdown. This selector lists all reference images currently defined in the Reference Images Panel as checkboxes. The user picks which references to include for this specific clip — none, one, two, or all three. This prevents unwanted characters or objects from appearing in clips where only a subset of references is relevant.

#### 4.3.2 Reference Images Panel

This expandable panel at the top of the workspace lets the user create and manage reference images that get attached to every video generation call, ensuring visual consistency across all clips.

- The panel shows up to 3 reference image slots (the maximum supported)
- Each slot has:
  - A thumbnail preview of the reference image (or an empty placeholder)
  - A label field where the user names the reference (for example: "Main character", "Red sports car", "Castle exterior")
  - A "Generate" button that creates a reference image using AI image generation based on a prompt the user provides
  - An "Upload" button to use an existing image from the user's computer
  - A "Remove" button to clear the slot
- When reference images are defined, they do not attach to clips automatically — each clip has its own "References" selector where the user chooses which of the available references to include for that clip
- A "Select All" shortcut on the selector applies all defined references to the clip at once
- The per-clip reference selection is saved and remembered; if the user regenerates the clip, the same selection is reused unless the user changes it
- The user can change or remove reference images at any time from the panel; this only affects future generations on clips that include that reference, not already-generated clips

#### 4.3.3 Transition Frames (Cross-Clip Continuity)

Between each pair of consecutive clips, the user can generate transition frames to create smooth visual continuity:

- Clicking "Generate Transition Frame" on the connector between Clip N and Clip N+1 triggers AI to:
  - Generate an image representing the ideal ending frame of Clip N (based on Clip N's script and the beginning of Clip N+1's script)
  - Generate an image representing the ideal starting frame of Clip N+1 (based on the ending of Clip N's script and Clip N+1's script)
- These images are then automatically set as the last frame of Clip N and the first frame of Clip N+1
- The user can then regenerate those clips using Frame Interpolation mode to produce videos that flow smoothly into each other
- Transition frames are optional — the user can skip this entirely and rely on straight cuts

#### 4.3.4 Extending a Clip

- Clicking "Extend Clip" on a generated video triggers Veo Video Extension, which adds 7 seconds to the clip
- Extension can only be performed on clips that were generated within the current session (Veo requires the original generation reference)
- Extension uses 720p resolution regardless of other settings (a constraint of the video generation engine)
- The user can extend a clip multiple times (up to 20 extensions per clip, reaching approximately 148 seconds total)
- Each extension requires a prompt describing what happens next in the extended portion — the user is prompted to enter this
- After extension, the clip section updates to show the new, longer video

#### 4.3.5 Editing a Script and Regenerating

- The user can edit any clip's script at any time by clicking into the text area on the left panel
- After editing, the user can:
  - Click "Regenerate Video" to generate a new video based on the updated script (previous video is replaced)
  - Click "Regenerate Script" to ask AI to rewrite the script from scratch while maintaining coherence with neighboring clips
- Regenerating a script does not automatically regenerate the video — the user decides when to generate

#### 4.3.6 Reordering Clips

- Each clip section has a drag handle on its left edge
- The user can drag and drop clips to reorder them
- Reordering updates the clip numbers but does not regenerate scripts or videos
- After reordering, the user can click "Refresh All Scripts" in the project header to ask AI to revise the narrative thread across all clips to match the new order

#### 4.3.7 Adding and Removing Clips

- A "Add Clip" button at the bottom of the clip list appends a new empty clip section
- The user can write a script for it manually or click "Generate Script" to have AI write one that fits the narrative
- Each clip section has a "Delete Clip" button (with confirmation) to remove it from the reel
- The minimum number of clips is 1; the maximum is 10

### 4.4 Secondary Workflows

#### 4.4.1 Previewing the Full Reel (Timeline Preview)

- A "Preview Reel" button in the project header opens a full-screen overlay
- The overlay plays all generated clips in sequence, one after another, simulating the final reel experience
- Clips without generated videos are represented by a dark placeholder card showing the clip number and a "No video yet" message — the preview skips them automatically
- Playback controls: play, pause, restart, and a scrubber bar showing clip boundaries
- The user can click on any clip segment in the scrubber bar to jump directly to that clip
- A "Close" button returns to the workspace

#### 4.4.2 Assembling and Downloading the Final Reel

- A "Download Reel" button in the project header becomes active only when all clips have generated videos
- Clicking it triggers server-side concatenation of all clip videos in order, producing a single MP4 file
- A progress indicator shows: "Assembling your reel..."
- Once ready, the browser downloads the file automatically
- The file is named using the project title (sanitized for file systems), for example: `my-epic-sunset-reel.mp4`
- If some clips have been extended, the final reel includes the full extended versions
- If a hook is generated and its toggle is set to "on", the hook is prepended to the reel as the first 4 seconds of the final MP4
- The download is in the aspect ratio chosen at project creation (9:16 or 16:9)

#### 4.4.3 Downloading Individual Clips

- Each clip section with a generated video has a small "Download" icon button on the video player
- Clicking it downloads just that single clip as an MP4 file
- The file is named with the project title and clip number, for example: `my-epic-sunset-reel-clip-3.mp4`

#### 4.4.4 Managing Projects on the Home Page

- The Home page shows all projects as cards in a grid layout
- Each project card displays:
  - The project title
  - A thumbnail (the first frame of the first generated clip, or a default placeholder if no clips are generated yet)
  - The creation date
  - The number of clips with generated videos out of the total (for example: "5/7 clips generated")
  - The aspect ratio badge (9:16 or 16:9)
- Clicking a project card opens its workspace
- Each card has a three-dot menu with:
  - **Duplicate** — creates a full copy of the project (scripts, settings, and reference images; videos are not copied since they expire)
  - **Rename** — opens an inline editor for the title
  - **Delete** — removes the project permanently after confirmation

#### 4.4.5 Hook Generation

Once the reel is complete (all clips have generated videos and the user has previewed or downloaded the assembled reel), the workspace unlocks a **Hook** section pinned above Clip 1.

- A banner appears at the top of the clip list: "Your reel is complete. Add a hook to grab attention in the first seconds."
- Clicking "Generate Hook Script" triggers AI to analyze the assembled reel (or all clip scripts if the assembled file is not yet available) and write a powerful 4-second hook prompt designed to stop viewers from scrolling on TikTok and Instagram
- The AI-generated hook script focuses on: a visually arresting opening image, a provocative question or teaser text, a dramatic action, or an emotional hook — whichever best suits the reel content
- The hook script appears in an editable text area in a **Hook Section** pinned above Clip 1, using the same two-panel layout as regular clips (script on the left, video on the right)
- The user can freely edit the hook script before generating the video
- Below the hook script, a "References" selector (identical to the one on regular clips) lets the user pick which reference images to include in the hook generation
- The user clicks "Generate Hook Video" to produce the 4-second clip
  - Generation uses the same methods available for regular clips (Text-to-Video or Image-to-Video), but duration is fixed at 4 seconds
  - The user can regenerate the hook video as many times as needed
- Once the hook video is generated, it is shown in the video player in the hook section's right panel
- The hook can be toggled on or off with a switch: "Include hook in final reel"
  - When on, the hook is prepended to the reel during assembly and download — the final MP4 starts with the 4-second hook followed by all clips in order
  - When off, the reel downloads without the hook, as before
- The hook is optional — the user can skip it entirely and download the reel without one
- The hook does not count toward the project's clip limit (10 clips maximum applies only to main clips)
- "Regenerate Hook Script" asks AI to write a fresh hook script based on the current reel content

#### 4.4.6 Regenerating All Scripts

- In the project workspace header, a "Regenerate All Scripts" button rewrites all clip scripts from scratch based on the project title, description, visual style, and current reference images
- This is useful when the user has significantly changed the project direction and wants a fresh set of coherent scripts
- A confirmation dialog warns: "This will replace all current scripts. Videos will not be affected until you regenerate them individually."
- After regeneration, all scripts are updated but no videos are regenerated automatically

### 4.5 Notifications & Communication

- This is a personal tool with no email, push, or SMS notifications
- All feedback is delivered in-app:
  - Video generation progress is shown as a real-time status on each clip (elapsed time, percentage if available)
  - Success messages appear as brief toast notifications at the bottom of the screen ("Clip 3 generated successfully")
  - Errors appear as inline messages on the affected clip section with a description of what went wrong and a "Retry" option
  - Reel assembly progress appears as a modal with a progress bar

### 4.6 Settings

- Accessed via a gear icon in the top navigation bar
- Available settings:
  - **Default Aspect Ratio** — set the default for new projects (9:16 or 16:9)
  - **Default Clip Duration** — set the default duration for new projects (4, 6, or 8 seconds)
  - **Default Number of Clips** — set the default clip count for new projects (5 through 10)
  - **Default Visual Style** — set a global default visual style directive that pre-fills on new projects
  - **Video Quality** — choose the default resolution for video generation: 720p (fastest), 1080p (high quality), or 4k (ultra HD, slowest). Note: 1080p and 4k require 8-second clip duration. Video extension always uses 720p regardless of this setting.
  - **Generation Speed** — toggle between "Quality" (uses the highest-quality model) and "Fast" (uses the speed-optimized model for quicker iteration)

### 4.7 Offboarding & Exit

- The user can close the browser tab at any time — all project data is saved automatically as they work
- There is no account to cancel or subscription to manage
- Important: generated videos are stored temporarily by the AI video service and expire after 2 days. Peliku downloads and saves video files to the server as soon as they are generated to prevent expiration. The user should download their final reel promptly.
- The user can delete individual projects or all projects from the Home page. Deletion is permanent.

---

## 5. Feature Inventory

### 5.1 Home & Project Management

**Project Dashboard (Home Page)**
- What it is: the landing screen showing all reel projects as a visual grid
- Who uses it: the sole user
- Why it matters: provides instant access to all work-in-progress and completed reels, making it easy to pick up where you left off
- Key behaviors:
  - Displays projects as cards sorted by last-edited date (most recent first)
  - Each card shows title, thumbnail, creation date, clip progress, and aspect ratio
  - Clicking a card opens the project workspace
  - Three-dot menu per card with Duplicate, Rename, and Delete actions
  - "New Project" button is always visible in the top-right corner

**New Project Form**
- What it is: a creation form where the user defines a new reel project
- Who uses it: the sole user
- Why it matters: captures the creative intent and global parameters that drive AI script generation
- Key behaviors:
  - Fields: Title (required), Description (required), Aspect Ratio (toggle), Clip Duration (select), Visual Style (optional text), Number of Clips (select)
  - "Generate Scripts" button submits the form and triggers AI to write all clip scripts
  - Loading state while AI works, then redirect to the project workspace

**Project Duplication**
- What it is: creates a complete copy of an existing project
- Who uses it: the sole user
- Why it matters: allows experimenting with variations of a reel idea without losing the original
- Key behaviors:
  - Copies all scripts, settings, visual style, and reference images
  - Does not copy generated videos (they must be regenerated)
  - The duplicate is named "[Original Title] (Copy)" and appears on the Home page

**Project Deletion**
- What it is: permanently removes a project and all its data
- Who uses it: the sole user
- Why it matters: keeps the Home page clean and frees storage
- Key behaviors:
  - Requires confirmation: "Delete '[Project Title]'? This cannot be undone."
  - Removes all scripts, generated videos, reference images, and settings

### 5.2 AI Script Generation

**Initial Script Generation**
- What it is: AI reads the project title, description, visual style, and number of clips, then writes a detailed video generation prompt for each clip
- Who uses it: the sole user
- Why it matters: this is the core intelligence of the tool — it transforms a rough idea into a structured sequence of production-ready prompts that share a unified narrative thread, consistent characters, environment, color palette, and mood
- Key behaviors:
  - Generates one script per clip (5 to 10 scripts depending on project settings)
  - Each script is detailed enough to produce a coherent video: subject, action, camera motion, composition, lighting, ambient sounds, dialogue, style, and how it connects to the previous and next clips
  - All scripts share a "fil conducteur" — a narrative thread, recurring visual motifs, consistent character descriptions, and a unified color palette
  - Scripts include audio cues (dialogue in quotes, sound effects described explicitly, ambient noise specified) so that the AI video generator produces appropriate sound
  - The first clip's script establishes the scene; the last clip's script provides a clear resolution or punchline

**Single Script Regeneration**
- What it is: AI rewrites one clip's script while keeping it coherent with its neighboring clips
- Who uses it: the sole user
- Why it matters: allows targeted refinement without starting over
- Key behaviors:
  - Takes into account the scripts of the clip before and after (if they exist) to maintain narrative flow
  - Preserves the global visual style, characters, and mood
  - The user can regenerate a single script without affecting any other clip

**Full Script Regeneration**
- What it is: AI rewrites all clip scripts from scratch based on the current project title, description, and visual style
- Who uses it: the sole user
- Why it matters: allows a complete creative reset when the project direction has changed significantly
- Key behaviors:
  - Warns the user before proceeding
  - Replaces all scripts but does not touch generated videos

**Manual Script Editing**
- What it is: the user can directly edit any clip's script in a text area
- Who uses it: the sole user
- Why it matters: gives the user final say over every word in the prompt — AI suggests, the human decides
- Key behaviors:
  - Free-form text editing in the left panel of each clip section
  - Changes are saved automatically
  - No automatic video regeneration after editing — the user triggers that explicitly

### 5.3 Video Generation

**Text-to-Video Generation**
- What it is: generates a video clip from a text prompt alone
- Who uses it: the sole user
- Why it matters: the fastest way to produce a first draft of any clip
- Key behaviors:
  - Uses the clip's script as the prompt
  - Automatically attaches reference images if any are defined
  - Applies project-level settings (aspect ratio, duration, resolution)
  - Shows generation progress with elapsed time
  - Displays the result in the clip's video player when done

**Image-to-Video Generation**
- What it is: generates a video clip using a starting frame image
- Who uses it: the sole user
- Why it matters: gives precise control over the opening frame, ensuring visual continuity with the previous clip or matching a specific composition
- Key behaviors:
  - The user provides a first frame via one of three methods:
    - Generate an image from the script using AI image generation
    - Upload an image from their computer
    - Use the last frame of the previous clip (if available)
  - The video animates from this starting frame according to the script
  - Reference images are automatically attached

**Frame Interpolation**
- What it is: generates a video that smoothly transitions between a specified first frame and last frame
- Who uses it: the sole user
- Why it matters: the most powerful method for ensuring seamless transitions between clips — the video is constrained to start and end at precise visual states
- Key behaviors:
  - The user provides both a first frame and a last frame (generated, uploaded, or pulled from adjacent clips)
  - The AI generates a video that begins at the first frame and ends at the last frame, following the script
  - Ideal for clips in the middle of the reel where both the entry and exit points need to match neighboring clips

**Video Extension**
- What it is: adds 7 additional seconds to an already-generated clip
- Who uses it: the sole user
- Why it matters: allows a clip to hold on an important moment, complete an action, or let a scene breathe — without regenerating from scratch
- Key behaviors:
  - Only works on clips generated within the current session (requires the original generation reference)
  - The user provides a short prompt describing what happens in the extended portion
  - Resolution is locked to 720p for extensions
  - Can be applied up to 20 times per clip (maximum total duration: approximately 148 seconds)
  - The result is a single combined video (original + extension)

**Extend from Previous Clip (Generation Method)**
- What it is: generates the current clip's video by extending the previous clip's video, using the current clip's script as the extension prompt
- Who uses it: the sole user
- Why it matters: produces the most seamless possible transition between two consecutive clips — the new footage literally grows out of the previous clip's video, so there is zero visual discontinuity at the cut point
- Key behaviors:
  - Available on Clip 2 and above only (Clip 1 has no previous clip)
  - Requires the previous clip to already have a generated video
  - The current clip's script serves as the extension prompt describing what happens next
  - The AI takes the previous clip's video and appends new footage guided by the script
  - The system splits the combined result: the previous clip keeps its original portion, the new portion becomes this clip's video
  - Resolution is locked to 720p (video extension constraint)
  - Can be chained across consecutive clips (generate Clip 1 independently, then Clip 2, 3, 4 each extend from their predecessor) to produce a long unbroken sequence split into individual segments
  - Ideal for scenes where a character's motion, camera movement, or environment continues unbroken across a clip boundary

**Video Regeneration**
- What it is: discards the current video for a clip and generates a new one from the current script
- Who uses it: the sole user
- Why it matters: allows iteration — if a clip does not look right, try again with the same or edited script
- Key behaviors:
  - Replaces the existing video entirely
  - Uses the currently selected generation method (text-to-video, image-to-video, frame interpolation, or extend from previous clip)
  - Previous video is lost after regeneration

### 5.4 Reference Images

**Reference Image Generation**
- What it is: generates a reference image from a text prompt using AI image generation
- Who uses it: the sole user
- Why it matters: locks the visual appearance of characters, objects, or environments so they look consistent across all clips
- Key behaviors:
  - The user enters a descriptive prompt (for example: "A young woman with short red hair, green eyes, wearing a black leather jacket, photorealistic portrait")
  - AI generates the image and displays it as a thumbnail in the Reference Images Panel
  - The user labels the reference for their own identification

**Reference Image Upload**
- What it is: the user uploads an existing image from their computer to use as a reference
- Who uses it: the sole user
- Why it matters: allows using existing character designs, photos, or brand assets as visual anchors
- Key behaviors:
  - Accepts common image formats (JPEG, PNG, WebP)
  - Displays the uploaded image as a thumbnail in the Reference Images Panel
  - The user labels the reference

**Reference Image Management**
- What it is: the panel where all reference images are defined and managed; per-clip selection of which references to use happens inside each clip section
- Who uses it: the sole user
- Why it matters: central library of visual anchors — the user defines up to 3 references here, then chooses the relevant subset on each clip to avoid unwanted characters or objects appearing where they do not belong
- Key behaviors:
  - Up to 3 reference image slots
  - Each slot shows a thumbnail, label, and remove button
  - References are not auto-attached to any clip; each clip independently selects which references to include via a "References" selector
  - Adding or removing a reference from the panel only affects future generations on clips that have that reference selected, not already-generated clips

### 5.5 Transition Frames

**Transition Frame Generation**
- What it is: generates a pair of images (last frame of Clip N, first frame of Clip N+1) designed to create smooth visual continuity between consecutive clips
- Who uses it: the sole user
- Why it matters: removes jarring visual cuts between clips, making the reel feel like a single continuous piece
- Key behaviors:
  - The user clicks "Generate Transition Frame" on the connector between two clips
  - AI analyzes both clips' scripts and generates:
    - An ending frame for the upper clip that visually bridges toward the next clip's content
    - A starting frame for the lower clip that visually connects back to the previous clip's conclusion
  - These frames are automatically set as the last-frame and first-frame for their respective clips
  - The user can then regenerate those clips using Frame Interpolation to produce videos that smoothly flow into each other
  - Transition frames are optional and independent per clip boundary

### 5.6 Reel Assembly & Export

**Reel Preview**
- What it is: a full-screen playback of all generated clips in sequence, optionally preceded by the hook
- Who uses it: the sole user
- Why it matters: lets the user see the complete reel experience before committing to a final export
- Key behaviors:
  - If a hook is generated and toggled on, it plays first, followed by all clips in order
  - Plays all clips with generated videos in sequence
  - Skips clips without videos (shows a placeholder indicator in the scrubber)
  - Playback controls: play, pause, restart, scrubber bar showing hook (if present) and clip boundaries
  - Click any segment in the scrubber to jump to that clip or the hook
  - Close button returns to the workspace

**Reel Download**
- What it is: concatenates all clip videos in order (optionally preceded by the hook) and produces a single downloadable MP4 file
- Who uses it: the sole user
- Why it matters: this is the final deliverable — the file the user uploads to Instagram or TikTok
- Key behaviors:
  - Available only when all clips have generated videos
  - If a hook is generated and toggled on, it is prepended as the first segment of the final MP4
  - Triggers server-side assembly with a progress indicator
  - Downloads automatically when ready
  - File is named after the project title (sanitized for file systems)
  - Maintains the project's aspect ratio and resolution

**Individual Clip Download**
- What it is: downloads a single clip's video as a standalone MP4 file
- Who uses it: the sole user
- Why it matters: useful for repurposing individual clips or sharing specific segments
- Key behaviors:
  - Available on any clip with a generated video
  - File named with project title and clip number

### 5.7 Hook

**Hook Script Generation**
- What it is: AI analyzes the complete reel and writes a 4-second hook prompt designed to stop viewers from scrolling
- Who uses it: the sole user
- Why it matters: the first seconds of a reel determine whether a viewer keeps watching or scrolls past — a strong hook dramatically increases engagement
- Key behaviors:
  - Available once all clips have generated videos (the reel is complete)
  - AI reads all clip scripts (and the assembled video if available) to craft a hook that teases, provokes, or visually arrests the viewer
  - The hook script is fully editable before video generation
  - "Regenerate Hook Script" writes a fresh suggestion based on the current reel content

**Hook Video Generation**
- What it is: generates a 4-second video clip from the hook script
- Who uses it: the sole user
- Why it matters: produces the actual hook video that will be placed at the beginning of the reel
- Key behaviors:
  - Duration is fixed at 4 seconds
  - Supports Text-to-Video and Image-to-Video generation methods
  - The user can select which reference images to include via the per-clip "References" selector
  - Can be regenerated as many times as needed
  - The generated hook is shown in a video player in the Hook Section above Clip 1

**Hook Toggle**
- What it is: a switch that controls whether the hook is included in the final reel
- Who uses it: the sole user
- Why it matters: gives the user flexibility to produce the reel with or without the hook from the same project
- Key behaviors:
  - When on, the hook is prepended during reel preview and reel download
  - When off, the reel starts directly with Clip 1
  - Toggling does not delete the hook — it remains available for re-enabling

### 5.8 Settings

**Default Preferences**
- What it is: global settings that control default values for new projects and video generation
- Who uses it: the sole user
- Why it matters: saves time by pre-filling the user's preferred configuration on every new project
- Key behaviors:
  - Default Aspect Ratio: 9:16 or 16:9
  - Default Clip Duration: 4, 6, or 8 seconds
  - Default Number of Clips: 5 through 10
  - Default Visual Style: free text
  - Video Quality: 720p, 1080p, or 4k
  - Generation Speed: Quality (highest-quality model) or Fast (speed-optimized model)
  - Settings are saved immediately when changed

---

## 6. Content & Information Architecture

### 6.1 Content Types

**Project**
- Contains: title, description, visual style, aspect ratio, clip duration, number of clips, creation date, last-edited date
- Displayed as: a card on the Home page grid; a header summary in the workspace
- Created by: the user via the New Project form
- Organized by: last-edited date (most recent first) on the Home page

**Clip Script**
- Contains: the detailed text prompt for one video clip, including subject, action, camera, composition, lighting, sound, dialogue, and narrative connection to neighboring clips
- Displayed as: an editable text area in the left panel of each clip section
- Created by: AI during initial script generation, then optionally edited by the user
- Organized by: clip sequence number within the project

**Generated Video**
- Contains: an MP4 video file for one clip, with native AI-generated audio
- Displayed as: a video player in the right panel of each clip section
- Created by: the AI video generation service, triggered by the user
- Organized by: clip sequence number within the project

**Reference Image**
- Contains: an image file (AI-generated or uploaded) with a user-provided label
- Displayed as: a thumbnail in the Reference Images Panel at the top of the workspace
- Created by: AI image generation or user upload
- Organized by: slot position (1, 2, or 3) in the Reference Images Panel

**Transition Frame**
- Contains: a pair of images (last frame / first frame) for a clip boundary
- Displayed as: small thumbnails on the connector between two clip sections
- Created by: AI image generation, based on the scripts of the two adjacent clips
- Organized by: the boundary between two consecutive clips

**Hook**
- Contains: a 4-second video clip with its editable script/prompt, reference image selection, and an on/off toggle
- Displayed as: a dedicated Hook Section pinned above Clip 1 in the workspace, using the same two-panel layout (script left, video right)
- Created by: AI writes the hook script; the user triggers video generation
- Organized by: always a single item per project, positioned before all clips

**Assembled Reel**
- Contains: a single MP4 file with (optionally) the hook followed by all clips concatenated in order
- Displayed as: not persistently shown — it is generated on demand and downloaded immediately
- Created by: server-side concatenation triggered by the user
- Organized by: not applicable (one-time deliverable per export)

### 6.2 Search & Filtering

- The Home page shows all projects in a grid sorted by last-edited date
- A search bar at the top of the Home page allows searching projects by title
- No additional filtering or sorting options are needed for a personal tool with a manageable number of projects

### 6.3 Navigation Structure

- **Top Navigation Bar** (always visible):
  - Left: app name/logo ("Peliku"), which is also a link back to the Home page
  - Right: Settings gear icon
- **Home Page**: grid of project cards + "New Project" button
- **Project Workspace**: accessed by clicking a project card; the top nav bar remains, with a back arrow to return to the Home page
- **Settings**: accessed via the gear icon; opens as a slide-over panel from the right side, not a separate page
- **Preview Overlay**: full-screen overlay accessed from the workspace; dismissible with a close button or Escape key

---

## 7. Access, Roles & Permissions

**Sole User (Owner)**
- Who this role represents: the single person who owns and operates this tool
- What they can see: everything — all projects, all clips, all settings
- What actions they can perform: create, read, update, and delete any project; generate, regenerate, extend, reorder, and download any clip; manage reference images; change settings
- What they cannot see or do: nothing is restricted — this is a single-user personal tool
- How they are assigned this role: they are the only user; no login or account system is required

> Assumption: since this is a personal tool running on the user's own infrastructure, there is no authentication system, no login screen, and no user management. The user accesses the app directly via a URL.

**Unauthenticated Visitor**
- Not applicable. This is a personal tool not exposed to the public internet. If it is, all functionality is available to whoever has the URL.

> Assumption: the tool is either run locally or deployed to a private server. There is no public access scenario to design for.

---

## 8. States, Edge Cases & Error Handling

### 8.1 Empty States

**Home Page — No Projects Yet**
- Message: "No reels yet. Start creating."
- A large, centered "Create Your First Reel" button
- No sample data or demo projects

**Project Workspace — Scripts Generated, No Videos**
- All clip sections show their AI-generated scripts in the left panels
- All right panels show a video placeholder with a "Generate Video" button
- The "Download Reel" button is disabled, with a tooltip: "Generate all clip videos to download the reel"
- The "Preview Reel" button is available but shows a message when triggered: "No clips have been generated yet. Generate at least one clip to preview."

**Reference Images Panel — No References**
- Three empty slots, each showing a dashed border and a "+" icon
- A helper text: "Add reference images to maintain visual consistency across clips"

### 8.2 Loading States

**Script Generation**
- The New Project form shows a full-screen loading overlay with: "Writing your clip scripts..." and an animated indicator
- Duration: typically a few seconds

**Video Generation (Per Clip)**
- The right panel of the clip shows:
  - A pulsing placeholder animation
  - "Generating video..." with a live elapsed-time counter
  - A "Cancel" button (if supported by the backend)
- Duration: ranges from 11 seconds to 6 minutes depending on resolution and server load

**Reel Assembly**
- A centered modal overlay with: "Assembling your reel..." and a progress bar
- Duration: depends on the number and length of clips

**Transition Frame Generation**
- The connector area between clips shows a small spinner with "Generating transition frames..."

### 8.3 Error States

**Video Generation Fails**
- The right panel shows an error message in red text: "Video generation failed: [reason]"
- Common reasons: prompt was blocked by safety filters, server timeout, temporary service unavailability
- A "Retry" button appears to attempt generation again with the same settings
- The script is not affected — the user can also edit the script and try again

**Script Generation Fails**
- A toast notification at the bottom: "Script generation failed. Please try again."
- The user remains on the form with all their input preserved
- A "Retry" option is available

**Video Extension Fails**
- Inline error on the clip: "Extension failed: [reason]"
- Common reasons: original video reference expired (the video was generated more than 2 days ago and was not downloaded to the server in time), resolution incompatibility
- The existing clip video is not affected

**Reel Assembly Fails**
- The modal shows: "Assembly failed. Please check that all clips have generated videos and try again."
- A "Retry" button in the modal

**Image Generation Fails (Reference Images or Transition Frames)**
- Inline error in the reference image slot or transition connector: "Image generation failed. Try again."
- A "Retry" button

**Hook Script Generation Fails**
- A toast notification: "Hook script generation failed. Please try again."
- The Hook Section remains in its previous state (empty or with the old script)
- A "Retry" option is available

**Hook Video Generation Fails**
- Inline error in the Hook Section's right panel: "Hook generation failed: [reason]"
- The hook script is not affected — the user can edit the script and retry
- A "Retry" button appears

### 8.4 Boundary & Limit States

**Maximum Clips Reached (10)**
- The "Add Clip" button is disabled with a tooltip: "Maximum of 10 clips per project"

**Maximum Reference Images Reached (3)**
- All three slots are filled; no additional "+" button or "Add" option appears
- The user must remove an existing reference image before adding a new one

**Maximum Extensions Reached (20 per clip)**
- The "Extend Clip" button is disabled with a tooltip: "Maximum extension limit reached for this clip"

**Video Expiration Warning**
- When a video's underlying generation reference is approaching the 2-day expiration:
  - A small warning badge appears on the clip: "Video reference expiring soon — download your reel"
  - This warning does not block any functionality

> Assumption: The application downloads and stores generated videos on its own server immediately after generation completes, so the 2-day expiration from the AI service is handled transparently. The warning above applies to Video Extension operations, which require the original generation reference to still be active.

**Clip Duration Restriction for High Resolution**
- If the user sets Video Quality to 1080p or 4k in Settings, the Clip Duration selector in the New Project form is locked to "8 seconds" with a note: "1080p and 4k resolution require 8-second clips"

**Extension Resolution Restriction**
- The "Extend Clip" feature always operates at 720p, regardless of the project's Video Quality setting
- A small info note appears when extending: "Extensions are generated at 720p"

### 8.5 Confirmation & Destructive Actions

**Delete Project**
- Confirmation dialog: "Delete '[Project Title]'? All scripts, videos, and reference images will be permanently removed. This cannot be undone."
- Two buttons: "Cancel" (default focus) and "Delete" (styled in red)

**Delete Clip**
- Confirmation dialog: "Remove Clip [N]? The script and generated video will be deleted."
- Two buttons: "Cancel" (default focus) and "Remove"

**Regenerate All Scripts**
- Confirmation dialog: "Regenerate all scripts? This will replace all current clip scripts with new AI-generated ones. Existing videos will not be affected."
- Two buttons: "Cancel" (default focus) and "Regenerate"

**Regenerate Video (when a video already exists)**
- Confirmation dialog: "Regenerate this clip's video? The current video will be replaced."
- Two buttons: "Cancel" (default focus) and "Regenerate"

**Regenerate Hook Video (when a hook video already exists)**
- Confirmation dialog: "Regenerate the hook video? The current hook video will be replaced."
- Two buttons: "Cancel" (default focus) and "Regenerate"

### 8.6 Concurrent & Conflict States

- Since this is a single-user tool, true concurrency conflicts do not apply
- However, the user might trigger video generation for multiple clips simultaneously
- Each clip section manages its own independent generation state — generating Clip 3 does not block the user from editing Clip 5's script or triggering generation for Clip 7
- If the user edits a script while its video is being generated, the in-flight generation continues with the old script. The user can regenerate after it completes.

---

## 9. Monetization & Access Model

Not applicable. This is a free, personal utility with no monetization plans.

---

## 10. Internationalization & Localization

- The interface is in English only
- No right-to-left language support needed
- Dates are displayed in a simple, unambiguous format: "Mar 15, 2026"
- No currency or number formatting requirements

> Assumption: since this is a personal tool for a single user, internationalization is not a priority for the first version.

---

## 11. Success Metrics (User-Facing)

- The product is successful when the user can go from typing a reel idea to downloading a complete, post-ready MP4 reel without leaving the browser
- The product is successful when all seven clips in a reel visually feel like they belong to the same story — consistent characters, palette, and mood
- The product is successful when the user can regenerate any individual clip without breaking the coherence of the overall reel
- The product is successful when transition frames between clips make the reel feel like a continuous piece rather than a slideshow of disconnected clips
- The product is successful when the user chooses Peliku over manually juggling separate AI tools and a video editor for every new reel
- The product is successful when a reel created entirely in Peliku performs comparably (in engagement) to reels produced with traditional production tools

---

## 12. Out of Scope (V1)

- **Direct publishing to Instagram or TikTok** — excluded because the user prefers to handle publishing separately; adding OAuth flows and platform APIs would add significant complexity for minimal benefit in a personal tool
- **Background music and voiceover layering** — excluded because the AI video generation already produces native audio (dialogue, SFX, ambient). Additional audio work is done outside this tool.
- **Multi-user support, accounts, and authentication** — excluded because this is a personal tool for a single user. No login, no roles, no sharing.
- **Mobile-native apps (iOS, Android)** — excluded because a responsive web app is sufficient for the user's workflow. The tool is used at a desk, not on the go.
- **Custom transition effects between clips (crossfade, wipe, zoom)** — excluded because frame interpolation and transition frames provide visual continuity at the content level. Post-production transition effects are out of scope for V1. Planned for a future version.
- **Template library / preset reel types** — excluded because the user writes original reel concepts every time. Pre-made templates do not match the creative workflow. May be considered if the user develops recurring formats.
- **Automatic thumbnail generation for each reel** — excluded to keep scope focused. The user can screenshot a frame from the reel after download.
- **Version history per clip (undo to a previous generation)** — excluded because it adds storage and complexity. The user regenerates clips as needed. May be added in a future version.
- **Bulk generation (generate all 7 clips at once with one click)** — excluded for V1 because the user needs to review and approve each clip individually. Parallel generation may be introduced once the workflow is validated.
- **Collaborative features (sharing projects, feedback from others)** — excluded because this is a solo tool. No plans for collaboration.

---

## 13. Open Questions & Assumptions

### Assumptions Made

- > Assumption: the tool is used by a single person and does not require any authentication, login, or account system.
- > Assumption: the tool runs as a local or privately hosted web application, not on the public internet.
- > Assumption: generated videos are downloaded and stored server-side immediately after the AI service produces them, so the 2-day expiration of the AI video service does not cause data loss for the user.
- > Assumption: the AI video generation service (Veo 3.1) is the primary engine for all video generation. The speed-optimized variant (Veo 3.1 Fast) is used when the "Fast" generation speed setting is selected.
- > Assumption: AI image generation (Nano Banana) is used for reference image creation, first-frame and last-frame generation, and transition frame generation.
- > Assumption: all projects and their data (scripts, settings, reference images, downloaded video files) are persisted in a database on the server so that the user can return to any project at any time.
- > Assumption: the default number of clips is 7, based on the user's stated preference, but the tool supports 5 through 10 clips for flexibility.
- > Assumption: when AI generates the set of clip scripts, it receives the full project context (title, description, visual style, number of clips, and the content of any existing scripts for neighboring clips) to ensure narrative and visual coherence.
- > Assumption: the portrait aspect ratio (9:16) is the default because the primary target platforms are Instagram Reels and TikTok, both of which are portrait-first.
- > Assumption: the tool does not add its own watermark to the output. The AI-generated videos carry SynthID watermarks from the generation service, which is transparent and does not affect the visual output.

### Open Questions

- > Question: should the tool auto-save projects in real time (like Google Docs) or require an explicit "Save" action? Auto-save is assumed for V1 because it reduces friction, but it means every keystroke in a script field triggers a save. A debounced auto-save (save 1 second after the user stops typing) is the most practical approach.
- > Question: should there be a maximum number of projects? No limit is assumed for V1, but if storage becomes a concern, a limit or archival mechanism may be needed.
- > Question: should the user be able to upload their own video clips (not AI-generated) and include them in the reel alongside AI-generated clips? This is excluded from V1 for simplicity but would significantly expand creative flexibility if added later.
- > Question: when regenerating a single script, should the AI consider all other scripts in the project, or only the immediate neighbors (previous and next clips)? Considering all scripts produces better global coherence but is more expensive. The assumed approach for V1 is to send all scripts as context.
