# Provenance UI spec v2: "Dispatch"

Direction: light, tactile, built from the vocabulary of a packing bench (label stock, hazard tape, beacon lights, tape measures, pallet wrap) instead of a generic dark dashboard. One bold move: the status band is a full-bleed solid color block readable from across the room. Everything else stays quiet.

What was removed from v1 and why: blue-black slate surfaces, Tailwind emerald/red/amber hues, blue focus ring, glow shadows on ticks, one 12px radius on everything, uppercase tracked labels everywhere, tinted translucent banners.

All contrast ratios below are computed WCAG 2.x values, not estimates.

---

## A. Core Design Tokens (CSS Variables)

| Token | Light | Dark | Role |
|---|---|---|---|
| `--canvas` | `#E4E7E9` | `#111214` | App background. Galvanized steel gray, no cream, no navy |
| `--surface` | `#F6F7F7` | `#1B1C1F` | Cards, panels, header, modals (thermal label white) |
| `--recess` | `#D9DDE0` | `#252629` | Inset areas: table header, source switcher, clip rows, ribbon track |
| `--hover` | `#CED3D7` | `#2F3034` | Hover on rows, secondary buttons, chips |
| `--press` | `#C0C6CB` | `#3A3B40` | Pressed state, active segment |
| `--line` | `#C9CED2` | `#34353A` | Default 1px borders on cards and rows |
| `--line-strong` | `#7B838A` | `#6F7177` | Input borders, secondary button edges (3.5:1 on surface) |
| `--ink` | `#17181A` | `#F1F2F3` | Primary text, primary button fill, heavy frame borders (16.5:1 on surface) |
| `--ink-2` | `#3F454C` | `#BCBFC4` | Table cell text, descriptions (9.0:1) |
| `--ink-3` | `#565E66` | `#8E9197` | Timestamps, placeholders, hour labels (6.1:1 on surface, 4.8:1 on recess) |
| `--focus-halo` | `rgba(245,196,0,.5)` | `rgba(245,196,0,.45)` | Scanner-yellow halo around the focused barcode input |

## B. Semantic State Palettes

Each state has a solid (fills and large text), a tint, and an ink that is safe for small text on that tint. Status is never color alone: every state also carries a distinct icon and a word.

**Beacon (orange): recording, live**
- Solid `#C45500` (white text 4.5:1). Dark-mode text/dot variant `#FF8A3D`
- Tint `#FADFCB`, ink on tint `#8F3C00` (5.9:1)

**Pallet (blue): saved, completed, playback, stream OK**
- Solid `#0B5CAB` (white text 6.7:1). Dark-mode text variant `#5AA2F0`
- Tint `#DCE8F5`, ink on tint `#084A8C` (7.1:1)

**Hi-vis (yellow): warning, timeout, input-ready halo**
- Solid `#F5C400` (ink text 10.8:1). Never use white text on it
- Tint `#FBEFB8`, ink on tint `#5C4300` (8.0:1)
- Timeline mark for abnormal parcels uses `#8A6200` (4.0:1 on recess, graphics only)

**Cochineal (crimson): camera offline, delete, failure**
- Solid `#B0123F` (white text 7.0:1). Dark-mode text variant `#FF6B8E`
- Tint `#F6DDE3`, ink on tint `#8F0F33` (7.2:1)

Why these hues: recording orange and saved blue sit on opposite sides of the color-vision-deficiency confusion axis, so the two most common states never rely on a red/green distinction. Danger is a blue-leaning crimson so it cannot be mistaken for the orange recording state.

## C. Type, Shape, Depth, Motion

**Type**
- Display and numerals: Barlow Condensed (600/700). Modeled on highway signage, reads at distance. Used for status titles, timer, clock, metrics, wordmark.
- UI text: Atkinson Hyperlegible Next (400/600). Built to separate look-alike characters.
- Barcodes and order IDs only: Atkinson Hyperlegible Mono (500/600). Do not use mono for timestamps or generic labels.
- All numerals: `font-variant-numeric: tabular-nums`.
- Sentence case everywhere except the four status titles, which are uppercase because they are signage.
- Scale: 12 / 14 / 16 / 20 / 28 / 36 / 48. Body 14, table 14, input 20, timer 48.

**Shape: radius depends on size, never one value for all**
- `--r-xs` 3px: ticks, chips, checkboxes
- `--r-sm` 6px: buttons, inputs, tabs, source segments
- `--r-md` 8px: clip rows, table inner controls, toasts at 10px
- `--r-lg` 16px: cards, viewport, ribbon, modals
- Nested radius equals parent radius minus padding.

**Depth**
- No glows, no colored shadows, no blur, no gradients as decoration.
- Primary buttons are tactile keycaps: inset bottom edge `inset 0 -3px 0 rgba(255,255,255,.14)`. Pressed: `translateY(1px)` and the inset edge drops to 1px.
- Secondary buttons: `0 2px 0 var(--line-strong)`. Pressed: `translateY(2px)`, shadow 0.
- Heavy 1.5px `--ink` borders only on structural anchors: header bottom edge, status band, viewport frame, dialog shell. Everything else uses 1px `--line`.
- The only pattern allowed is the hazard stripe (see offline state).

**Motion**
- Hover and focus: 120ms ease-out.
- Status band color change: 180ms fill transition, no slide.
- Scan accepted: barcode pill scales 1 to 0.97 to 1 over 160ms and the input flashes `--pallet-tint` for 400ms.
- Recording dot and playhead: 1s opacity pulse (1 to 0.35). No glow.
- Respect `prefers-reduced-motion`: drop pulse and scale, keep color changes.

**Icons**: Phosphor Icons, bold weight, 20px, 1.5px optical stroke. Not Lucide.

---

## D. Element-by-Element Styling Breakdown

### 1. Application Frame and Top Header
- Header bar: `--surface`, bottom border 1.5px `--ink`, height 60px.
- Brand: 24px label-corner mark (ink square with the top-right corner clipped 6px, white "P" in Barlow Condensed 700). Wordmark "Provenance" in Barlow Condensed 700, 22px, `--ink`, tracking 0.02em, sentence case.
- Station tag: `--recess` fill, 1px `--line`, text `--ink-2`, 12px/600, radius `--r-xs`. Reads "Station 1".
- Navigation tabs (Station, Clips archive, Settings): 15px/600, height 40px, radius `--r-sm`.
  - Inactive: transparent, text `--ink-2`, hover `--hover`.
  - Active: `--ink` fill, `--surface` text, no border, no shadow. Inverted, not outlined.
- Clock: Barlow Condensed 600, 22px, `--ink`, tabular. Open folder: secondary button with folder icon.

### 2. Live Station Status Band (solid color block above the CCTV)
Height 96px, radius `--r-lg`, 1.5px `--ink` border. Left: 48px icon tile (radius `--r-sm`, 18% white overlay on colored states). Title in Barlow Condensed 700, 36px, uppercase. Right: timer in Barlow Condensed 600, 48px, tabular.
- **Idle:** fill `--surface`, title "READY TO SCAN" in `--ink`, hollow ring icon `--ink-3`, timer "00:00" `--ink-3`.
- **Recording:** fill Beacon solid `#C45500`, all text `#FFFFFF`, pulsing dot icon, title "RECORDING". Barcode pill: fill `rgba(0,0,0,.25)`, white Mono text, radius `--r-xs`.
- **Saved:** fill Pallet solid `#0B5CAB`, white text, check icon, title "CLIP SAVED", shows barcode and final duration. Returns to idle after 2.5s.
- **Camera offline:** fill Cochineal tint `#F6DDE3`, 1.5px border `#B0123F`, title "CAMERA FEED OFFLINE" in `#8F0F33`, slashed-camera icon, a 10px hazard-stripe strip along the top edge (`repeating-linear-gradient(135deg, #F5C400 0 12px, #17181A 12px 24px)`), and a "Retry" secondary button on the right.

### 3. CCTV Camera Viewport and Quick Bar
- Outer frame: fill `#0D0E10`, border 1.5px `--ink`, radius `--r-lg`, overflow hidden.
- Live tally (top right of video): "REC" pill, fill `#C45500`, white text 12px/700, 8px white dot with the 1s opacity pulse. Hidden when not recording.
- Quick bar: `--recess`, top border 1px `--line`, padding 8px 12px.
- Source switcher (Webcam, CCTV RTSP): one segmented control. Track `--recess` with 1px `--line`, radius `--r-sm`, padding 3px. Active segment: `--surface` fill, 1px `--line-strong`, `0 1px 0 var(--line-strong)`, text `--ink`. Inactive: transparent, `--ink-2`.
- Telemetry: plain text, no chip. 8px Pallet dot, then "1920x1080" and "30.4 fps" in `--ink-2`, 13px, tabular, separated by a 1px `--line-strong` vertical rule. Dot turns Cochineal and values go `--ink-3` when the stream drops.

### 4. Shift Activity and Pacing Ribbon (the time tape)
- Card: `--surface`, 1px `--line`, radius `--r-lg`, padding 12px 16px.
- Metrics: total parcels in Barlow Condensed 28px `--ink` with a 13px `--ink-2` unit; average duration `--ink-2`; pacing rate in `#084A8C` with an up or down arrow icon so direction is not color-coded.
- Track: styled like a tape measure. Fill `--recess`, 1px `--line`, radius `--r-md`, height 40px. Hour majors are 1px `--line-strong` full-height rules with 10px `--ink-3` tabular numerals at the bottom.
- Normal parcel tick: 2px by 16px `--ink-3`, radius 1px, like a pencil mark.
- Abnormal parcel tick: 2px by 26px `#8A6200` with a 6px square cap on top.
- Hover on any tick: tick becomes `--ink` at 3px width, and a tooltip chip appears (`--ink` fill, white text, radius `--r-xs`) with barcode and duration. No glow.
- Live playhead: 2px `#C45500` line with an 8px square pip on top, 1s opacity pulse while recording.

### 5. Operator Bench Control Panel (Right Column)
- Barcode card: `--surface`, 1px `--line`, radius `--r-lg`, padding 20px. Label "Barcode" 13px/600 `--ink-2`.
- Barcode input: height 56px, fill `#FFFFFF`, 1.5px `--line-strong`, radius `--r-sm`, Atkinson Mono 600 at 20px, `--ink`. Focus: border `--ink` plus `0 0 0 4px var(--focus-halo)`. Scan accepted: fill flashes `--pallet-tint` for 400ms.
- Start scan: height 56px, fill `--ink`, text `--surface`, keycap inset edge, radius `--r-sm`. Hover: fill `#2B2D30`. Disabled while recording: fill `--recess`, text `--ink-3`.
- Finish: height 56px. Active (recording): fill `--ink`, text `--surface`, with a small "Enter" keycap chip inside (fill `#3A3C40`, radius `--r-xs`). Inactive (idle): transparent, 1.5px dashed `--line-strong`, text `--ink-3`.
- Demo quick chips: `--recess`, 1px `--line`, text `--ink-2`, radius `--r-sm`, hover `--hover`. Prefix label "Try".

### 6. Recent Finished Clips Card
- Container: `--surface`, 1px `--line`, radius `--r-lg`.
- Clip row: `--recess`, 1px `--line`, radius `--r-md`, hover `--hover`.
- Barcode: Atkinson Mono 600, `--ink`. Order tag: 12px chip, 1px `--line-strong` outline, transparent fill, `--ink-2`, radius `--r-xs`.
- Timestamp `--ink-2`, duration `--ink-3`, both tabular.
- Timeout tag: fill `#FBEFB8`, text `#5C4300`, 1px `#D9B000`, with a clock icon.
- Proof button: secondary style, text `--ink-2`, hover text `--ink` and border `--ink`.

### 7. Clips Archive and Dispute Search Table
- Container: `--surface`, 1px `--line`, radius `--r-lg`, overflow hidden.
- Header row: `--recess`, bottom border 2px `--ink`, text `--ink-2`, 12px/600, sentence case (no uppercase, no tracking).
- Data rows: bottom border 1px `--line`, text `--ink-2`, hover `--hover`. Selected row: `--hover` fill plus a 3px `--ink` bar on the left edge.
- Checkboxes: 18px, radius `--r-xs`, checked fill `--ink` with a white tick.
- Row actions:
  - View proof: primary-small, fill `--ink`, text `--surface`.
  - Edit: secondary, text `--ink`.
  - MP4: secondary, text `--ink-2`, download icon.
  - Delete: transparent, 1px `rgba(176,18,63,.45)` border, text `#B0123F`, hover fill `#F6DDE3`.

### 8. Modals (Video Proof Player, Edit Metadata, Delete Confirmation)
- Backdrop: `rgba(23,24,26,.6)`, no blur.
- Dialog shell: `--surface`, 1.5px `--ink` border, radius `--r-lg`, shadow `0 24px 48px -16px rgba(23,24,26,.45)` (the only soft shadow in the system).
- Player canvas: `#000000`. Scrubber: track `--hover`, 6px high, radius 3px; fill `--ink`; thumb 14px circle `--ink` with a 2px `--surface` ring. Event markers on the track are 2px `#8A6200` ticks.
- Metadata card: `--recess`, 1px `--line`, labels `--ink-3` 12px, values `--ink` 600.
- Form inputs: fill `#FFFFFF`, 1.5px `--line-strong`, text `--ink`, same focus halo as the barcode input.
- Dialog buttons: Save fill `--ink`; Delete fill `#B0123F` with white text; Cancel secondary.

### 9. Toast Notifications
Bottom center, `--ink` fill, white text, radius 10px, 4px colored left stripe, icon matches the stripe. Enter: 8px rise plus fade, 160ms. Auto-dismiss 3.2s.
- Success: stripe and icon `#5AA2F0`.
- Warning: stripe and icon `#F5C400`.
- Danger: stripe and icon `#FF6B8E`.

---

## E. Rules to keep it from drifting back to generic

1. No gradients except the hazard stripe. No glows. No blur. One soft shadow in the whole system (modals).
2. Never one radius for everything. Follow the scale in section C.
3. Uppercase only for the four status titles. Table headers, labels, tabs are sentence case.
4. Mono only for barcodes and order IDs.
5. Orange means recording and nothing else. Yellow means attention and nothing else. Blue means done. Crimson means broken or destructive.
6. Primary action is ink, not a brand color. Color is reserved for state.
7. Minimum 48px hit area on bench controls (gloves, scanner in the other hand).
8. If a new screen needs a color, it needs a new meaning first.

## F. Dark mode notes
Dark mode swaps only the neutral tokens and uses the lighter text variants for state colors. Banner fills (Beacon, Pallet) keep their light-mode solids with white text. The primary button inverts: fill `--ink` (now `#F1F2F3`) with text `#17181A`. Hi-vis stays `#F5C400` in both themes.
