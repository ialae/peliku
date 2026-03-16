# UI/UX Design System — ReelForge

> Generated from: FEATURE_SPECS.md
> Date: March 15, 2026
> Design type: Playful / Friendly
> Theme: Vibrant Studio
> Primary color: #A855F7 (Electric Purple) - Dark Mode Default

---

## 1. Design Philosophy

ReelForge is a creative playground disguised as a powerhouse production tool. Because crafting short-form video content is inherently a highly visual and iterative process, the design must feel vibrant, approachable, and encouraging without getting in the way of the content itself. The interface defaults to dark mode—acting like a dimmed cinematic screening room—where our vibrant jewel-toned accents serve to guide the user's eye and reward actions. The experience should feel like stepping into a modern, slightly magical video editing suite that actually does the hard work for you.

- Provide immediate, colorful visual feedback to reward progress.
- Keep the interface dark and recessive so the vibrant video content stays the hero.
- Use soft, friendly geometry and slight depth cues to make the workspace feel tangible and inviting.
- Never let editing feel like a chore; empty states and loading sequences must maintain a playful, encouraging tone.

---

## 2. Color System

### 2.1 Brand Colors

The palette revolves around an electric, creative vibe that pops against dark backgrounds.

- **Primary**: #A855F7 (Electric Purple) — Used for primary actions, active states, and drawing attention to the most crucial creation steps (e.g., "Generate Videos").
  - Shades: 50 (#FAF5FF), 100 (#F3E8FF), 200 (#E9D5FF), 300 (#D8B4FE), 400 (#C084FC), 500 (#A855F7 - base), 600 (#9333EA), 700 (#7E22CE), 800 (#6B21A8), 900 (#581C87), 950 (#3B0764)
  - Usage rules: Use 500/600 for primary buttons and loaded progress bars. Use lighter shades (300/400) for text accents or icons on dark backgrounds to ensure legibility.

- **Secondary**: #EC4899 (Neon Pink) — A complementary warm pop for secondary accents.
  - Shades: full scale (50–950)
  - Usage rules: Use for special feature highlights like the "Generate Hook Script" banner or unique visual calls-to-action to differentiate from standard purple flows.

- **Accent**: #06B6D4 (Vibrant Cyan) — A cool counterpoint for interactive elements like drag handles or transition connectors.
  - Shades: full scale (50–950)
  - Usage rules: Limited to small micro-interaction touches, like timeline scrubbers and active tab indicators.

### 2.2 Neutral Colors

A dark-mode-first grayscale palette rooted in deep, cool grays (Slate) that feels cinematic but modern.
- 50: #F8FAFC (Primary text on dark backgrounds)
- 100: #F1F5F9
- 200: #E2E8F0
- 300: #CBD5E1 (Secondary text, placeholders)
- 400: #94A3B8
- 500: #64748B
- 600: #475569 (Subtle borders)
- 700: #334155 (Hover states on dark)
- 800: #1E293B (Card/Panel backgrounds)
- 900: #0F172A (Page background)
- 950: #020617 (Deepest shadows, modal overlays)

### 2.3 Semantic Colors

- **Success**: #10B981 (Teal) — Used for "Generation Complete" indicators and success toasts. Includes dark variant (#064E3B) and light variant (#CCFBF1).
- **Warning**: #F59E0B (Amber) — Used for warning users about unsaved changes or clip deletion.
- **Error / Danger**: #EF4444 (Red-Pink) — Used for failed generation states and destructive confirmation buttons.
- **Info**: #3B82F6 (Blue) — Used for informational tooltips and neutral system messages.

### 2.4 Dark Mode Palette

Because ReelForge is inherently a cinematic tool, the product is primarily designed as a Dark Mode experience.
- Surface Level 0 (Body/Page): #0F172A (Neutral 900)
- Surface Level 1 (Cards, Main Clip Panels): #1E293B (Neutral 800)
- Surface Level 2 (Hover States, Input Backgrounds, Sub-panels): #334155 (Neutral 700)
- Surface Level 3 (Dropdowns, Popovers, Modals): #020617 (Neutral 950) with a subtle purple tint in the shadow.
- Primary text: Neutral 50 (#F8FAFC)
- Secondary text: Neutral 300 (#CBD5E1)
- Disabled text: Neutral 500 (#64748B)

### 2.5 Contrast Compliance

- Primary text (#F8FAFC) on Page Background (#0F172A): > 14:1 (Passes AA & AAA)
- Primary Button text (#F8FAFC) on Primary 600 (#9333EA): 5.8:1 (Passes AA)
- Error text / Warning text on Surface Level 1 evaluated to ensure > 4.5:1. For dark mode, lighter semantic borders/text are utilized to strictly conform. Borderline combo (Pink 500 on Slate 800) adjusted to Pink 400 for better legibility against dark gray.

---

## 3. Typography

### 3.1 Font Families

- **Heading font**: Quicksand — A geometric, friendly sans-serif with rounded terminals that reinforces the "Playful" and "Vibrant" vibe.
  - Fallback stack: 'Quicksand', 'Nunito', sans-serif
  - Loaded from: Google Fonts

- **Body font**: Inter — Highly legible, modern neutral sans for user interfaces and editable text areas.
  - Fallback stack: 'Inter', system-ui, -apple-system, sans-serif
  - Loaded from: Google Fonts

- **Monospace font**: JetBrains Mono — Used purely for any underlying code snippets, IDs or technical file names (e.g. download file names).
  - Fallback stack: 'JetBrains Mono', monospace

### 3.2 Type Scale

- `text-xs`: 0.75rem (12px) — line-height: 1rem — used for: timestamp indicators, character counts, status labels
- `text-sm`: 0.875rem (14px) — line-height: 1.25rem — used for: field labels, helper text, secondary buttons
- `text-base`: 1rem (16px) — line-height: 1.5rem — used for: clip scripts, main body copy, primary inputs
- `text-lg`: 1.125rem (18px) — line-height: 1.75rem — used for: section headers, empty state subheadings
- `text-xl`: 1.25rem (20px) — line-height: 1.75rem — used for: clip titles, project card titles
- `text-2xl`: 1.5rem (24px) — line-height: 2rem — used for: page headers (Project Workspace Title)
- `text-4xl`: 2.25rem (36px) — line-height: 2.5rem — used for: empty state main headlines, marketing callouts

### 3.3 Font Weights

- 400 (Regular): Body text, scripts, descriptions
- 500 (Medium): Inputs, secondary buttons, subheadings
- 700 (Bold): Primary buttons, Project Titles, Labels

### 3.4 Text Styles

- `heading-1`: text-4xl, font-bold, Quicksand, tracking-tight, Neutral 50 — used for page titles
- `heading-2`: text-2xl, font-bold, Quicksand, tracking-tight, Neutral 50 — used for project titles and major sections
- `heading-3`: text-xl, font-bold, Quicksand, Neutral 50 — used for "Clip X" headers
- `body-default`: text-base, font-regular, Inter, Neutral 100 — used for script text areas
- `body-small`: text-sm, font-regular, Inter, Neutral 300 — used for helper text
- `label`: text-sm, font-medium, Inter, Neutral 200 — used for form labels, generation method dropdowns

### 3.5 Typography Rules

- Max line width: 65 characters for script text areas to preserve high readability for creative editing.
- Heading hierarchy must strictly follow h1 -> h2 -> h3 without skipping.
- Word and line truncation (ellipses) max 2 lines on Project Cards in the Workspace.

---

## 4. Spacing & Layout

### 4.1 Spacing Scale

Base unit: 4px.
- `space-0`: 0px
- `space-1`: 4px — 0.25rem
- `space-2`: 8px — 0.5rem
- `space-3`: 12px — 0.75rem
- `space-4`: 16px — 1rem
- `space-5`: 20px — 1.25rem
- `space-6`: 24px — 1.5rem
- `space-8`: 32px — 2rem
- `space-10`: 40px — 2.5rem
- `space-12`: 48px — 3rem
- `space-16`: 64px — 4rem
- `space-20`: 80px — 5rem
- `space-24`: 96px — 6rem

### 4.2 Layout Grid

- Container max width: 1200px (to keep the clip panels focused and readable).
- Grid columns: 12 (Desktop) / 8 (Tablet) / 4 (Mobile).
- Gutter width: 24px (Mobile: 16px).
- Content padding: 32px on Desktop, 16px on Mobile.

### 4.3 Breakpoints

- **Mobile**: 320px (min) — 4 cols, 16px gutter, 16px padding
- **Tablet**: 768px (min) — 8 cols, 24px gutter, 24px padding
- **Desktop**: 1024px (min) — 12 cols, 24px gutter, 32px padding
- **Wide**: 1440px (min) — 12 cols, 24px gutter, max-width centered

### 4.4 Common Spacing Patterns

- Section Spacing: `space-12` between the Header, Reference Panel, and main Clip List.
- Stack spacing: `space-6` vertically between individual Clip cards.
- Internal Card Padding: `space-6` inside the Project Setup Form and individual Clip Left/Right panels.
- Form field spacing: `space-2` between label and input, `space-5` between distinct form fields.

---

## 5. Shapes, Borders & Elevation

### 5.1 Border Radius Scale

Consistent soft geometry defines the "Playful" studio vibe.
- `radius-none`: 0px — unused, avoid sharp corners entirely.
- `radius-sm`: 4px — used for checkboxes.
- `radius-md`: 8px — used for small buttons and inner dropdown items.
- `radius-lg`: 16px — used for Clip inputs, video players, buttons.
- `radius-xl`: 24px — used for major structural layers: Clip panel containers, Modals.
- `radius-full`: 9999px — used for pill badges, avatars, timeline scrubbers.

### 5.2 Border Styles

- Default border width: 2px (The 2px thickness gives a slightly tactile, playful feel).
- Border color: Neutral 700 (#334155) for standard borders.
- Active/Focus borders use Primary 500 (#A855F7).

### 5.3 Elevation / Shadow Scale

Since the environment is dark mode, shadows are subtle and are often accented by colored border highlights or glow effects.
- `shadow-none`: none
- `shadow-sm`: 0 1px 2px rgba(0, 0, 0, 0.5) — buttons
- `shadow-md`: 0 4px 6px -1px rgba(0, 0, 0, 0.5) — dropdowns
- `shadow-lg`: 0 10px 15px -3px rgba(0, 0, 0, 0.7) — hovering project cards on home dashboard
- `shadow-xl`: 0 25px 50px -12px rgba(0, 0, 0, 0.9) — modals, overlay previews
- `shadow-glow`: 0 0 15px rgba(168, 85, 247, 0.4) — applied to active/completed primary actions to emphasize vibrancy.

---

## 6. Iconography & Imagery

### 6.1 Icon System

- Icon library: Phosphor Icons (Rounded variant). Thick, approachable, highly legible.
- Icon style: Duotone where possible for a premium playfulness; otherwise outlined.
- Icon sizes: 16px (small inputs, labels), 24px (buttons, headers), 32px (empty states, giant placeholders).
- Icon color rules: Inherit text color, or use Primary 400 for accents.
- Pairing rule: Icons must be paired with labels (e.g., "Generate Video" always shows text alongside the magic wand icon).

### 6.2 Illustration Style 

- Flat, vibrant dark-mode optimized vector illustrations. Abstract, slightly geometric representations of camera lenses, magic sparkles, and clapperboards with overlapping translucent purple and pink shapes.
- Focus: Empty states (Dashboard, New Project), and loading assemblies ("Assembling your reel...").

### 6.3 Image Treatment

- Aspect ratios:
  - Video Previews: 9:16 (Portrait) or 16:9 (Landscape) referencing the global setting.
  - Reference Images: 1:1 squares cropped, using `object-fit: cover`.
- Placeholders: Subtle pulse shimmer animation using Neutral 800 to Neutral 700.
- Border radius: `radius-lg` (16px) for all thumbnails and playable media.

### 6.4 Avatar System

- Single creator tool, user avatars are restricted to the settings top-right corner. Use a 40px circle with user initials on a gradient purple background.

---

## 7. Component Design Specifications

### 7.1 Buttons

**Variants:**
- **Primary**: Background: Primary 600, Text: Neutral 50, Radius: `radius-lg`. On hover: Lightens to Primary 500, elevates slightly. Used for "Generate Video" -> the most critical action.
- **Secondary**: Background: Neutral 800, Text: Neutral 100, Border: 2px solid Neutral 600. Used for "Regenerate Script", "Add Clip", "Upload Image".
- **Ghost**: Background: Transparent, Text: Neutral 300. Hover: Background Neutral 800, Text Neutral 50. Used for text-links, "Remove" features.
- **Danger**: Background: Error 600, Text: Neutral 50. Used for "Delete Clip". Let's use it sparingly.

**Sizes:**
- Small: 32px height, 12px px padding, text-sm.
- Medium: 48px height, 16px px padding, text-base, 24px icon.
- Large: 56px height, 24px px padding, text-lg. (Used strictly for Project Start "Generate Scripts").

**States:**
- Default, Hover (lighter BG), Active (scale down 98%), Disabled (opacity 50%, unclickable), Loading (Spinner replaces icon).

### 7.2 Form Inputs

**Text Input & Textareas:**
- Anatomy: Label (text-sm, above), Input (Neutral 800 bg, 2px border Neutral 600, text-base), Helper text (text-xs, Neutral 400, below).
- Focus state: Border becomes Primary 500, adds an outer glow `box-shadow`.
- Textareas: Script editors default to 6 rows. Lock vertical resize to prevent layout breaking, or use auto-grow up to max 400px.

**Select / Dropdown:**
- Generation Method dropdown triggers: styled identically to secondary buttons, with a trailing caret down icon.
- Dropdown panel: Neutral 800, `radius-lg`, `shadow-lg`, with 8px gaps between options. Hovering an option sets its background to Neutral 700.

**Toggle / Switch:**
- Used for checking "Include hook in final reel".
- Size: 44px wide, 24px height. `radius-full`.
- On state: Primary 500 background, white knob. Off state: Neutral 600 background, gray knob.

### 7.3 Cards (Clip Panels)

- Default padding: `space-6` (24px).
- Background: Neutral 800.
- Border: none initially. On drag/focus, 2px solid Primary 500.
- Shadow: `shadow-md`.
- Border-radius: `radius-xl`.
- Layout: Split 50/50. Left is Scripting (Textarea + Regen Script + Reference checkboxes), Right is Output (Video Player Placeholder / Controls).

### 7.4 Modals / Dialogs

- Width: 480px fixed.
- Background: Neutral 900, border 1px solid Neutral 700.
- Centered completely. Dark overlay (Neutral 950 at 80% opacity, backdrop blur 4px).
- Requires explicit closure (Cancel or Top-Right X) to avoid losing unsaved data.

### 7.5 Toast Notifications / Snackbars

- Position: Bottom-center.
- Anatomy: Floating pill, `radius-full`, padding 12px 24px.
- Success: Teal background accent. Provides instant satisfying affirmation "Clip 3 Video Generated".
- Disappear after 5 seconds. Max stack of 3.

### 7.6 Timeline / Connectors

- Connectors between clips: A 2px vertical cyan line extending from the bottom of Clip 1 to the top of Clip 2.
- In the center of the line, a small circular "Generate Transition Frame" ghost button. When generated, the circles change to solid Cyan with a checkmark, communicating flow.

### 7.7 Navigation

- Top bar: Minimal header. Height 72px. Background Neutral 900 (sticky).
- Project title editable inline. Global setting quick-toggles.
- Actions: "Preview Reel" (Ghost) and "Download Reel" (Primary, disabled until all clips are ready).

### 7.8 Empty States & Placeholders

- **Right Panel (Video Placeholder)**: Neutral 800 dashed border (Primary 400 when hovered), huge magic wand icon in center over "Generate Video".
- **Home Dashboard Empty State**: Illustration of overlapping film reels, friendly text "No projects yet. Forge your first reel to get started." + Large Primary button.

---

## 8. Form Design & Validation

### 8.1 Validation

- Multi-step validation is skipped here as it's a dashboard config style.
- Validate on blur. Error messages appear below the field in Error Red (#EF4444) alongside an exclamation icon. The input border immediately changes to Red.
- Script area max characters (2,000) shows a counting indicator bottom right: `1980/2000` turns Amber. `2000/2000` turns Red.

---

## 9. Animation & Motion

### 9.1 Timing Tokens

- `duration-fast`: 150ms — Buttons, hover states, toggles.
- `duration-normal`: 300ms — Modals, popovers, toast sliding.
- `duration-slow`: 500ms — Expanding clip panels, timeline preview opening.

### 9.2 Easing Curves

- `ease-default`: `cubic-bezier(0.4, 0, 0.2, 1)`

### 9.3 Custom Animations

- **Generation Glow**: When a video is generating, the placeholder pulsates with a subtle Primary Purple glow. `animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;`
- **Skeleton Shimmer**: Left-to-right light gray sweep across Neutral 700 skeleton bars while scripts are written.
- **Respect Reduced Motion**: Replace all pulses and shimmers with static "Generating..." text layers.

---

## 10. Responsive Design Specifications

- **Desktop (default)**: Side-by-side split (Script Left, Video Right) inside each Clip Panel.
- **Tablet & Mobile**: The Clip Panel collapses to a single column. Script Panel stacks ON TOP of the Video Panel.
- Drag handles for reordering clips are accessible via a large hit area icon in the top right of the card on mobile, rather than the left edge on desktop.
- Touch zones for timeline scrubber in Timeline Preview must be 48px minimum vertically.

---

## 11. Accessibility Specifications

- **Focus UI**: Keyboard tabs use a 2px offset solid outline in Cyan (#06B6D4) so it pops aggressively against the dark purple/gray interface.
- ARIA live region deployed for the "Generation Method". Screen readers announce the elapsed time and completion state when a video finishes generating.
- Input labels never replaced by placeholder text.
- Reduced motion fallback explicitly specified for all progress spinners and loading fades.

---

## 12. Page & View Specifications

### 12.1 Home Dashboard
**Purpose**: View and manage previous products, start a new one.
**Layout**: Top navigation with logo + "New Project" button. Grid layout for cards.
**States**: Empty state with illustration; Populated array of project cards showing thumbnail & stats.

### 12.2 New Project Form
**Purpose**: Define the prompt, structure, and parameters for AI script generation.
**Layout**: Single-column centered form module max-width 600px.
**Key Interactions**: Sliders for duration, styled toggle cards (9:16 vs 16:9), large text area. Submitting triggers the "Writing scripts" loading sequence, transitioning into the workspace.

### 12.3 Project Workspace (Core Flow)
**Purpose**: Edit scripts, attach references, and generate individual clips.
**Layout**: Top nav with global actions (Regen All, Preview, Assemble & Download). Collapsible Reference Banner. Vertical stacked timeline of identical "Clip Cards". Pinned Hook Section at top (unlocked later).
**Key Interactions**: Typing in scripts, dropping images into reference zones, selecting generation methods, triggering generating buttons. Drag and drop ordering.
**Responsive**: Condenses from 2-column cards to stacked cards.

### 12.4 Preview Modal
**Purpose**: Timeline preview of the assembled clips before final build.
**Layout**: Full viewport overlay. Centered massive video player matching selected aspect ratio. Timeline tick-marks at the bottom.

---

## 13. User Flow Specifications

### Flow 1: Create to Scripts
**Trigger**: Clicking "New Project" on Home.
1. User enters Title, Description, chooses 9:16, 6-second clips, requests 5 clips.
2. Clicks "Generate Scripts". UI disables. Shimmer loading state appears with encouraging tips.
3. Arrives at Project Workspace. 5 Clip Cards are mapped out sequentially with full prompt text on the left, empty video targets on the right.

### Flow 2: Generating a Video using References
**Trigger**: In Project Workspace.
1. User opens Reference Images Panel. Uploads a picture of "My Dog" to slot 1.
2. On Clip 1, user checks "My Dog" next to references.
3. User clicks "Generate Video".
4. Text changes to "Generating...", pulse animation kicks in, timer counts up.
5. Success ping! Video plays on loop in the right panel.

### Flow 3: Extending a Clip
**Trigger**: Clip 1 video generated, User wants 14 seconds from a 7 second clip.
1. User clicks "Extend Clip" below the Clip 1 video player.
2. A small inline modal asks "What happens next?"
3. User types "Dog smiles at camera and winks". Clicks "Confirm".
4. Clip 1 re-enters loading state locking UI for that specific clip, retaining interactivity for Clip 2-5.

---

## 14. Dark Mode Specifications

- As established, Dark Mode is the native and primary palette (Section 2.4). Light mode does not exist for this product. The vibrant neon palette specifically relies on the deep Slate dark canvas (Neutral 900) to communicate a "creative studio" feeling without eye strain during heavy editing sessions.

---

## 15. Content & Copy Guidelines

### 15.1 Voice & Tone
- Confident, encouraging, and highly technical yet accessible. We guide creators without sounding patronizing.
- "Generate Scripts", "Extend Clip", "Assemble Reel".

### 15.2 Button Labels
- Always verb-led. No "OK" or "Submit".
- Example: "Create Project", "Regenerate Script", "Upload Reference".

### 15.3 Error & Loading Messages
- Never technical strings (no `HTTP 500 error`).
- Generation error: "We couldn't generate this video. The prompt might be too complex or flagged. Try adjusting the script and click Regenerate."
- Loading (Short): "Writing scripts..."
- Loading (Long): "Rendering your vision... This might take a moment."

### 15.4 Empty States
- Project Dashboard: "No projects yet. Forge your first reel to get started."
- Reference Images: "Add character or style references to keep clips consistent."

---

## 16. Design Tokens Summary

### Colors (Dark Theme Native)
- `color-primary-500`: #A855F7
- `color-primary-600`: #9333EA
- `color-secondary-500`: #EC4899
- `color-accent-500`: #06B6D4
- `color-surface-bg`: #0F172A
- `color-surface-card`: #1E293B
- `color-text-primary`: #F8FAFC
- `color-text-secondary`: #CBD5E1

### Typography
- `font-heading`: Quicksand, sans-serif
- `font-body`: Inter, sans-serif
- `text-base`: 16px / 1.5rem line-height

### Spacing & Borders
- `space-4`: 16px (1rem)
- `space-6`: 24px (1.5rem)
- `radius-lg`: 16px
- `radius-xl`: 24px
- `border-width-default`: 2px

### Z-Index Scale
- `z-base`: 0 (Page content)
- `z-sticky`: 10 (Header nav)
- `z-dropdown`: 40 (Method dropdowns, tooltips)
- `z-overlay`: 50 (Modal backdrop)
- `z-modal`: 60 (Modals, Preview fullscreen)
- `z-toast`: 100 (Success notifications)

---

## 17. Feature-to-Design Mapping

**1. Project Dashboard**
- Components: Typography (Headers), Neutral Cards, Primary Action Buttons.
- Covered in Section 12.1.

**2. Script Parameter Form**
- Components: Inputs, Textareas, Select Lists, Large Action Buttons.
- Covered in Section 12.2.

**3. Workspace Clip Sequence & Video Generation**
- Components: Layout Cards, Video Placeholders, Button groups, Textareas, Checkboxes (Reference targeting). Drag handles.
- Covered in Section 12.3 & 7.3.

**4. Continuous Flow / Interpolation**
- Components: Accent 500 lines connecting cards, ghost circular buttons.
- Covered in Section 7.6.

**5. Hook Generation (Pinned Banner)**
- Components: Full width banner card tinted with Secondary Pink (#EC4899) borders to differentiate from standard purple flows. Same internal split panel as a clip card.
- Interaction: Toggle switch to prepend onto final reel. 

**6. Final Assembly & Download**
- Components: Primary disabled button in Top Nav that turns Active. Progress Modal overlay.
- Covered in Section 7.7 and Flow design.

---

## 18. Anti-Patterns — Never Do These

- **Alerts/Confirms:** Never use native browser `alert()` or `confirm()`. Any deletion (Delete Project, Delete Clip) must use the Custom Z-60 Modals defined with Danger buttons.
- **Color reliance:** Never communicate clip success or error based purely on Teal/Red coloring. Success must include a checkmark icon, error must include an exclamation icon + specific text message.
- **Infinite scrolls on dashboard:** Only load pages of projects via typical pagination when passing 20 cards. Avoid endless un-footer'd loads.
- **Overwhelming buttons:** No clip should have 6 primary colored buttons. "Generate Video" is the ONLY primary button in a clip card; others like "Regenerate" and "Extend" must be Ghost or Secondary.
- **Disappearing tools:** Do not hide the "Extend Clip" or "Regenerate" tools behind a hover state. Mobile users cannot hover.
- **Auto-playing media:** Do not auto-play generated videos with SOUND ON. Videos might auto-play silently (muted loop) for visual feedback, but sound defaults strictly to off, respecting user context.
- **Losing user input:** If video generation API times out, the script input and parameter setups MUST NOT be cleared. Keep user texts immutable on error.