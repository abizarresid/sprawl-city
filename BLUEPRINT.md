# Sprawl City: Blueprint (single-player, third person)

An open-world 3D crime sandbox that runs in the browser with an over-the-shoulder camera. Everything lives in `index.html`. Multiplayer is intentionally out of scope.

**Run it:** serve the folder and open it in a browser. ES modules don't load from `file://`.

```bash
python3 serve.py
```

`serve.py` is a plain file server on port 8123 with browser caching turned off, so a reload always picks up the newest build. (`python3 -m http.server 8123` also works, but Chrome may keep showing an older cached copy.) The start screen shows the build number.

Then open <http://localhost:8123>, or <http://localhost:8123/?mute> to start with sound off. Three.js comes from a CDN, so the first load needs internet. Click to play: the mouse is captured for looking around, and **Esc** pauses.

**Controls** (defaults; every key can be rebound in the pause menu, and bindings are saved in this browser)

| Input | On foot | In a vehicle |
|---|---|---|
| WASD / arrows | Move (relative to the camera), Shift to sprint | Drive, Shift for nitro |
| Mouse | Look (sensitivity and invert-Y in the pause menu) | Free look; recentres after 1.6 s |
| Left mouse | Shoot / punch | Drive-by |
| Right mouse | Aim. Lock-on snaps to the nearest target; flick the mouse to switch. Sniper: scope. With fists: block | – |
| Space | Jump; next to a car or low wall: vault over it | Handbrake drift |
| C | Crouch / sneak (badge shows hidden / seen). Behind someone unaware: LMB silent takedown. Next to a car or wall: cover (RMB pops up to aim, LMB blind-fires). While sprinting: slide | – |
| Z / V | Dodge roll / kick: front kick standing, roundhouse while moving, sweep crouched, flying kick in the air, spinning back kick after punches | – |
| Sprint + left mouse (fists) | Diving tackle | – |
| F | Enter / steal vehicle | Exit |
| 1–9, −, =, `, Q (hold: drop it), scroll | Fists, bat, knife, pistol, SMG, shotgun, carbine, sniper, RPG, revolver, assault rifle, throwing knives | – |
| Tab (hold) | Weapon wheel, time slows | – |
| R / G | Reload / grenade (hold to aim, release) | – |
| E | Hold up a pedestrian; hold at a shop counter to rob it; buy at any of the four gun shops (A/D switches tab) | – |
| T / M | Phone jobs / full map (scroll to zoom, click to set a waypoint) | – |
| U / X | First-person view / mask on or off | First-person (driver's seat) / – |
| E / B / Y | Over a body or a knocked-out person: E drags (E again lets go), Space while dragging lifts it onto your shoulder, E puts it down, B bags it. Y shoves (off a subway platform, too) | – |
| L / ; / ' / 0 / O / I | L: a remote charge on whatever's in front of you · ;: a tracker on a VIP or their car · ': a warning shot in a shop · 0 detonates · gloves · utility | – |
| E (homes, lifts) | Open or close a front door / call a lift, then E inside for its buttons; smash a window, climb through it, jump out of an upstairs one; climb a drainpipe | – |
| H (on foot) | Hail a taxi | Horn |
| E at a stair door / Hold E (homes, trucks, bank, delivery trucks) | Pick a locked door, take loot, crack a safe, disarm a burglar alarm; plant a charge on a stopped armoured truck | – |
| LMB / Y with a body on your shoulder | Throw it | – |
| Shift (jet) | – | Afterburner |
| N / H | – | Radio station / horn |
| P or Esc / K | Pause and controls / mute | – |

---

## 2zz18. Latest update (build 100): the shadow map was redrawn every frame, plus cheaper glow and HUD prompts

A profiling pass on an M5 (10 cores): game logic about 4 ms per frame and draw preparation about 4.6 ms, both on the page's one thread, and about 9 ms of GPU time in a 1331×998 window. Spreading the logic over Web Workers would save at most 2–3 ms of main-thread time and means untangling systems that write straight into the scene, so this build cuts the GPU work instead.

- **Shadows (`shadowStep`):** the sun moves a hair every frame with the time of day, and that counted as "moved", so the every-third-frame shadow saving never applied. The shadow map was redrawn every frame (about 2.6 ms of GPU). Now it's redrawn when the shadow camera steps to a new texel, when the sun has turned more than about 0.1° since the last redraw, while the player runs (over 3 m/s), drives (over 4 m/s) or flies, and otherwise every second frame.
- **Glow (`bloom.setSize`):** the bloom chain runs at a quarter of the screen resolution instead of half. Day scenes are pixel-identical; at night 0.4% of pixels differ, around lights.
- **HUD prompt (`computePrompt`):** it scanned everything nearby every frame (0.64 ms, nearly all of `updateHUD`). It's now worked out 10 times a second, and straight away when you get in or out of a vehicle or plane, die, or start a robbery. `updateHUD` went from 0.67 ms to 0.14 ms.
- **Looked at, not changed:** the 0.9 ms under `updateHeists` is about 70 small systems chained build after build (doors, homes, burglary, sleepers…), none over 0.1 ms. Many read one-frame key presses, so running them at a lower rate isn't safe.

**Measured:** median GPU time per frame 8.55 → 7.05 ms, alternating old and new behaviour five times each on the same page.

## 2zz17. Update (build 99): a battery saver that switches itself on, and fixes from a glitch-hunt playtest

**Battery saver (`BATT99`):** when the laptop is unplugged, the frame rate drops to the "When unplugged" setting: 30 fps, 40 fps (the default) or no limit. It shows a short notice when it kicks in. It uses `navigator.getBattery()`, so it works in Chrome and Edge. Safari doesn't report the battery; the settings row says so and points to the 40 fps checkbox. The setting is wired once the page has loaded (`wireBatt99`), so it also works from the start screen.

**From the build-98 playtest:**
- **Far city at night:** the night glow on the simplified buildings covered the whole far mesh, so the far ground lit up as a flat tan sheet. Now only the walls glow: an `aGlow` vertex attribute masks `totalEmissiveRadiance` in the shader. The glow is also dimmer (0.11/0.09/0.055 × `nightK`).
- **Half buildings at the detail switch:** 507 buildings straddle a 176 m tile edge. Each far box now carries the tiles of its footprint corners (`aTiles`) and is only dropped when all of them are in full detail. Where only part of a building's detailed pieces are drawn, the box fills in the rest.
- **A road out west vanished while you stood on it:** a merged chunk running from x −875 to −230 and z 20 to 1133 had its middle inside the city and was swapped by a city tile. Chunks over 300 m across, or reaching more than 60 m past the sea wall, now keep the old fog cull.
- **Roads that weren't there:** the far ground used to lay asphalt everywhere. Now each block cell is asphalt plus pavement for normal blocks, grass for wild blocks (no roads through open land) and sand for beach blocks. The strip between the last road and the sea wall is paving.
- **Westbrook houses inside the plaza shops, with their driveway cars inside the Mart and the pharmacy:** the plaza skip was on the wrong side of the street (`side > 0` for the z = −110 street). Fixed. The houses' seeded layout shifts as a result.
- **Spawn:** the player now starts at x = 16 instead of 9, so the corner street-sign pole isn't between the camera and the player.
- **Not changed:** the sky sphere doesn't follow the debug-only `game.cam()` override.

**Measured:** street 621 draw calls / 2.5M triangles; air 1,152 calls / 3.2M triangles; game logic 2.8 ms per frame.

## 2zz16. Update (build 98): why a low-poly game ran hot, a profiler, and simplified far buildings

**Why it ran hot (measured with a per-system profiler, a GPU timer query, and heap readings):** the GPU was not the problem. Under steady load it needed about 4 ms a frame at pixel ratio 1.3, and bloom plus the grade pass cost under 0.5 ms. The heat came from the CPU, on the main thread:
- **Simulating the whole map every frame.** Around 240 people and 220 cars were updated 60 times a second, wherever they were. Some of it was done the slow way:
  - `hitSkyline` scanned all 2,700 buildings linearly, about 150 times a frame (1.5 ms; mostly the car-in-a-building guard `carGuard80`);
  - `separateChars` tested every pair of people (29,000 pairs);
  - `carCharCollisions` tested every car against every person (50,000 pairs);
  - parked cars nobody had touched re-ran ground sampling and pose every frame;
  - traffic-light colours were recomputed every frame (3,500 calls);
  - `obsIn` allocated a new array on each of its ~1,400 calls a frame.
- **Transforms.** The scene had 22,000 objects, and three.js recomputed every one each frame, hidden or not (2.3 ms). That includes about 8,000 hidden rig parts on distant people drawn as stand-ins.
- **Draw calls.** About 900 at street level and 1,600 in the air, each costing far more CPU through WebGL (ANGLE → Metal) than in a native engine. About 190 were the one-mesh stand-ins for distant people, and about 270 were small props hundreds of metres away.
- **Memory.** The city's merged geometry was 42 million unindexed vertices, all 32-bit floats: 1.74 GB in JavaScript plus a GPU copy. The tab also sat on 4–6 GB of load-time scratch arrays that the browser didn't collect.
- **Why other games run cooler:** native engines simulate only what's near you, spread work across threads, use draw-call-cheap APIs, and stream LOD meshes. A single-threaded browser game that simulates and draws a whole city at 60 fps keeps one core and the GPU process busy the whole time.

**What changed:**
- **Profiler (`PROF98`):** times update, render, overlay, minimap, HUD and camera per frame. It also reads a GPU timer (`EXT_disjoint_timer_query_webgl2`, only while F3 is up) and the JS garbage rate. F3 shows it all.
- **Simplified far buildings (`LOD98`):**
  - Static city geometry now merges into 176 m tiles (`PIECE_TILE` 1).
  - `cullChunks` draws a city tile in full only within 300 m (medium; low 220, high 420; in the air 340/260/480). Past that, one merged mesh of plain boxes takes over: walls and roofs in facade colours, plus an asphalt grid and pavement, sand or grass blocks. It's a single draw call.
  - A 96×96 tile texture tells the box mesh's vertex shader which tiles to drop where the full detail is showing.
  - Rebuilt when a building collapses. Havenport and everything outside the city keep their own culling.
- **CPU:**
  - A 32 m grid for `hitSkyline`, checked identical to the linear scan on 44,000 samples and about 70× faster.
  - Sort-and-sweep for `separateChars`, and a binary-searched sorted list for `carCharCollisions`.
  - Settled parked cars refresh their visuals every 8th frame.
  - Traffic lights update every 4th frame.
  - `obsIn` reuses a ring of 32 arrays; the one caller that keeps its result (the ruin snapshot) copies it.
  - People more than ~140 m away who are just walking think at 20 Hz (`pedTick98`).
  - The corner minimap draws at 30 Hz.
  - The hurt vignette writes its style only when it changes.
- **Transforms:** during the renderer's scene update, hidden subtrees are skipped (`skipHid98`). The game's own reads, such as ragdoll start and wound raycasts, still call `updateMatrixWorld(true)` and get full updates. City chunks have `matrixAutoUpdate` off.
- **Stand-ins:** all distant people are drawn as one `InstancedMesh` (`SI98`), with per-instance clothes, skin and hair colours chosen in the vertex shader by part.
- **Props:** `farCull` also hides small props: under 3 m across past 250 m, under 10 m past 450 m (×1.4 on high, ×0.75 on low). Anything that glows is kept.
- **Memory:** chunk colours are stored as 16-bit and normals as 8-bit normalized attributes, as each chunk is merged (−523 MB). A short garbage nudge while the menu is up gets the browser to release the load-time scratch arrays; the tab drops from ~4.5–5.8 GB to ~1.5 GB.
- **Results (same spots, build 97 → 98):**
  - game logic per frame: street 5.5 → 2.9 ms; air 2.1 → 1.5 ms;
  - transforms: 2.3 → ~0.3–1.2 ms;
  - render CPU: 5.1 → 3.1–3.7 ms;
  - triangles: street 3.6M → 2.5M; air 6.3M → 3.2M;
  - draw calls: street ~906 → 730–810; air 1,596 → 1,051.
  - The per-system costs that were fixed dropped 70–97%: `carGuard80` 1.46 → 0.04 ms, `carCharCollisions` 0.82 → 0.12, the heists/homes chain 2.29 → 0.72.

## 2zz15. Update (build 97): why it ran hot and looked blurry, gore on bodies, contracts rewritten

**Performance investigation** (measured with `renderer.info` at the start position):
- **Before:**
  - about 1,780 draw calls and 6.2M triangles on frames where the shadow map redrew (every 2nd frame);
  - 1,230 calls and 4.3M triangles otherwise.
- **Where it went:**
  - city chunks: 2.3M triangles, 273 calls;
  - standalone meshes: 0.7M;
  - instanced props: 0.7M;
  - characters: 302 calls;
  - cars: 198 calls.
- Static geometry merges into 352 m tiles, so distance culling is coarse. Fog (and therefore the draw distance) reached 1,300 m.
- **Blur:** medium quality rendered at pixel ratio 1.0 on a 2× Retina screen, with dynamic resolution allowed down to 0.75. The game ran at 0.75× and was upscaled about 2.7×.

**What changed:**
- **Draw distance:** fog and draw distance capped by quality (`drawDist97`: low 600, medium 850, high 1250 m; +1600 in the air).
- **Shadows:**
  - detail chunks never cast shadows, and other chunks only within 240 m (`updatePerf97`);
  - static shadows redraw every 3rd frame instead of every 2nd;
  - detail chunks are drawn out to 200 m on medium (was 320).
- **Characters:** full detail out to 34 m (peds) / 42 m (others), was 48/56; the stand-in takes over past that.
- **Resolution:**
  - medium: pixel ratio 1.3, floor 1.0, no MSAA;
  - high: 2.0, floor 1.25, MSAA 2;
  - low: 1.0, floor 0.85.
  - A light 4-tap sharpen in the grade pass (`uSharp` 0.2, 0.12 on low).
- **Battery saver:** a new setting caps the game at 40 fps (`settings.cool97`).
- **After:** about 1,420 calls / 5.3M (shadow frames) and 1,000 calls / 3.7M otherwise; averages 1,150 calls and 4.2M triangles per frame, down 24% and 20%. The sharper resolution adds pixel work back, so the battery saver is the strongest cooling lever.
- **Deeper fix still open:** simplified far versions of the city chunks (LOD), since building geometry is the bulk of what's drawn.

**Gore on bodies already down (`corpseGore97`):**
- Melee swings at a body (knife, katana, machete or chainsaw strongest; bat; fists lightest) when nobody alive is in front of you.
- Cars running over or shoving a body.
- Every blast within 90% of its radius (heavy ones dismember).
- Aimed shots catch a body from further away (6 m) and higher (1.25 m aim height).
- Each hit adds a blood spray and a pool, and severs limbs above power 0.5.

**Street contracts (`SC97`, replacing SC90):**
- **Pace:** a new offer every 7–12 game hours, at most 2 waiting. The old instant-refill kind is gone.
- **Writing:** a fixer's terse brief (name, reason, routine, the condition, the disposal, the fee).
- **Targets live a day (`routineAnchor97`):**
  - out on foot near their day area (8:00–19:00);
  - on their own doorstep smoking (19:00–23:00);
  - inside their house (23:00–8:00).
  - They spawn only out of sight and keep their routine. Scared, they run (no teleporting home). If they run off and get culled, they're back on their routine an hour later.
- **Disposal is required.** Each contract names a person (Rudy behind the chop shop, Dutch at Havenport's container quay, Marco in the alley behind a bar) or a place (the crusher at Kessler Salvage, the end of Havenport's middle pier, the hunters' cabin fireplace).
  - Drop the body within 4.5 m of the person (9 m of the place), or stop a car with it in the trunk there for 1.5 s.
  - Destroying the body any other way also counts.
- **Pay:** 3,000–5,500 base, up to 2.6× for distance (far jobs pay more); 1.5× if the condition is met; half if the body is found first or left for a game day.

## 2zz14. Update (build 96): exits that fit the moment, a gentler airliner rule, a little less acceleration

**Getting out of things (`EX96`, `exitCar` / `exitPlane` wrappers; the last move is in `EX96.last`):**

| Situation | What happens |
|---|---|
| Car, under 6 m/s | Ordinary exit |
| Car, 6–24 m/s | Dive and roll: the base fall is cancelled; a longer roll along your heading with a small hop; up to 18 damage |
| Car, over 24 m/s | Tumble: launched with the car's speed, down 1.8 s, the base damage |
| Bike, over 7 m/s | Over the handlebars: thrown forward from the front of the bike |
| Car on its roof | Crawl out, crouched; short down time |
| Burning car | Scramble out away from it; 35% chance your clothes catch |
| Car explodes, health over 40 | Blown clear: pushed 2.5 m out, launched, on fire. That frame's damage is capped at 52 in total (`blastAt`), so you live. At 40 or less you die |
| Helicopter hovering 2.4–8 m up | Hang and drop: you fall, roll on landing, and take damage above 4 m |
| Helicopter or prop plane, up high | Hold F: the door slides open (0.7 s, rotor wash), then you jump and skydive |
| Fighter jet | Ejection seat: the canopy flies off, you're shot about 26 m/s upward with a flame trail, then skydive |
| Airliner passenger, up high | Hold F: unbuckle, step into the aisle, walk forward to the door (the cabin view follows), the door bursts open, you jump |
| Aircraft blows up, under 30 m, health over 60 | Thrown clear, 45 damage, on fire. Otherwise you die; this applies to shuttle passengers too |

**The shuttle**
- The cabin view is the default when you board (U switches to outside).
- The cabin is lit by the spare headlight spot, so no new light and no shader recompile. Windows go dark at night.

**Taking the airliner (toned down at the user's request)**
- Storming the cockpit in flight was removed entirely; it was too close to real events.
- New setting "Let me take the shuttle airliner", off by default (`settings.planeTake96`).
- **Off:** the shuttle can't be taken ("in service").
- **On, at the stand only:** two crew step down to block the stairs. Knock one down and the other backs off, then F takes it, and the stolen-plane chase applies.

**Cars:** acceleration is down 16% for every type except tanks and boats (`CAR_TYPES.*.accel ×0.84`, once). Top speeds are unchanged.

**Playtest:** every exit move fired as described. Survived being blown clear on 48 health. Ejected and rose 11 m. Walked the aisle to the door. The setting worked both ways. No errors; about 2.2 ms per frame.

## 2zz13. Update (builds 94–95): unarmed civilian aircraft, real passengers, Seattle-style Havenport, an island airport and a shuttle

**Build 94**
- **Civilian aircraft are unarmed.** `armPlane80` gives guns and flares only to the jet and the attack helicopter, bombs only to those two (8 and 4), and missiles only to the jet. The controls panel lists only what the aircraft really has. B in a civilian aircraft does nothing.
- **Pilots (`PIL94`):** any aircraft flown by AI (scripted airliners and props, private helicopter flights, military jets, the shuttle) gets seated puppets at the controls while within 160 m of the camera (`SEAT94` offsets per type).
- **Buses:** every seat becomes a full puppet within 65 m, up to 6 made per tick, so they're all real people up close. Low-detail stand-ins are only used beyond 75 m.
- **Stairwell handrail:** each segment now spans its step's rise, so the rail is continuous, with a post every 3 steps. Previously it was a floating dash per step.
- **Papers scenes:** when Doris, Mo or others open papers, the camera turns to face them.
- **Car acceleration:** not changed. The playtest measured about 2.3 s from 0 to 53 mph, which is quicker than most real road cars.

**Build 95: Havenport and Havenport International**
- **Havenport is laid out like Seattle (`havenType`):**
  - towers on the waterfront (i 1–5, j 4–8; i = 0 is waterfront commercial);
  - a 'PIER MARKET' shop on the water at 1,6;
  - port and rail yards to the south (j ≥ 11 with i ≤ 7, and the south waterfront);
  - apartments and shops on the slope above downtown (i ≤ 8, j 2–10);
  - houses on the hills to the east and north;
  - parks at 5,1 (a "Seattle Center"), 10,3, 10,10 and 12,6.
- **Waterfront:**
  - three finger piers (plank decks, pilings, a shed at each outer end) running about 150 m into the bay;
  - three yellow container cranes on the south quay, with about 70 stacked containers.
- **Reclaimed land (`reclaim95`):** called in the heightmap right after the bay is dug; literals only, since it can run before the mods block.
  - the airport island: x −4770…−4470, z −540…560, at 4 m;
  - a causeway at z 246;
  - the pier bases.
  - `isle95` keeps trees, rocks and grass off it.
- **Havenport International (`HVA95`):**
  - a 940 m north–south runway at x −4660 with centreline and threshold markings;
  - a parallel taxiway at x −4592 with three links;
  - an apron;
  - a 160 m glass terminal with the name on it, and a control tower;
  - a road to the causeway;
  - map markers for the airport and Sprawl's shuttle stand.
- **The shuttle (`FLT95`):** one airliner flies between Sprawl International (a stand east of the gates at cx−40, cz+12, airstairs) and Havenport International (a stand at −4555, 50).
  - It's kinematic and follows a node path (`routeOut95`): pushback, taxi, a take-off roll lifting at 60 m/s, cruise at about 460 m, an approach stepping down to 50 m before the threshold, landing and rollout, then taxi to the stand.
  - It waits 75 s at each stand. Passengers walk off to the terminal, then others walk out and board.
  - **Boarding:** E at the foot of the stairs buys a $180 ticket. Crouch + E sneaks on; if someone sees you, there's a 50% chance it's reported, and a 30% chance the airport police spot you on arrival.
  - **On board:** you ride as a passenger (`P.inPlane` with no driver). Hold Space to doze (time ×4, not during the roll or landing); U toggles a cabin view with 27 rows, 22 seated puppets near your row, and low-detail figures in the other seats; hold F to jump out (a skydive in the air).
  - Taking the controls with F still steals it, and the airline sends another plane.
  - Passengers are exempt from the stolen-plane chase. The Sprawl shuttle stand corridor (`gate95`) isn't treated as restricted airside.
- **Playtest:**
  - two round trips with tickets and one as a stowaway, with 0 stars on legit flights;
  - the approach reached 50 m above ground before the threshold;
  - no errors; about 1 ms per frame in Havenport and 1.9 ms in the city.

## 2zz12. Update (build 93): fixes from the playtest

- **Checkpoint**
  - It isn't taken in the minute after any crime (`reportCrime` or a kill by you), nor while a witness is on the phone (`state === 'call'`). That stops an unseen spree being baked into the baseline (`CK93`).
  - On a rewind, the erased timeline is cleared:
    - `NEWS.q`, `NEWS.bodies`, `NEWSQ.list` and the notice queue are emptied;
    - phone news entries stamped after the checkpoint (`g93` > `snap.clock93`) are removed;
    - press tension is restored.
  - Cases already rewind through `CKPT80`.
- **Hospital bill:** it's now really charged after the checkpoint restore: 10% of the cash you had when you died, matching the message.
- **Notices:** anything waiting more than 6 s in the queue is dropped as stale.
- **Camera**
  - The boom ignores thin tall obstacles under 0.9 m on both sides (poles, trunks, signals) via `camRay93`.
  - If the camera ends up inside a street tree's canopy (radius 2.2·s, 2–7·s above the ground), it slides in along the boom until it's out.
- **Police search:** a cop more than 45 m from you with no sight of you walks to a random point within 28 m of `lastSeen`, re-picking every 8–14 s ("Check the alley").
- **Knife, katana and machete:** LMB finishes a knocked-out, injured or downed person within 1.9 m in front of you. The KO-on-melee rule is avoided by keeping `ko` set and forcing the kill.
- **Quieter in the air:**
  - `curHome()` returns nothing in a plane, under a chute, or more than 5 m above the ground off a level, so there are no burglary, "asleep" or alarm prompts from the sky.
  - `computePrompt` is empty in aircraft.
  - Stakeouts need a civilian car and 0★.
- **Units:** aircraft speed is now in mph, like the label.
- **Names:** the alias surname "Garner" became "Gartside". The detective log lowercases the article ("Talked to a man in a suit").
- **News street names:** body news uses the kill position, so it names the same street as the case.
- **Radio line:** the dispatch line drops below the news ticker while a story is showing.
- **Removed export:** `game.enterStairs` (it broke `locationName`).
- **Helicopter:** it can't slide along the ground. Horizontal speed is capped at 3 m/s below 1.5 m above ground, reaching full speed by about 8.5 m.
- **Planes:** the Mallard climbs at no more than 6.5 m/s, the airliner 12.
- **Not changed:**
  - civilian aircraft weapons (you asked for guns and bombs on planes in build 81);
  - car acceleration and melee tuning;
  - the uncertain lobby hang;
  - the stairwell handrail dashes;
  - the diner camera.

## 2zz11. Update (builds 87–92): the roadmap shortlist

Built from the ideas page shortlist. Several items extend systems that already existed (human shields and disarms since build 74, contracts since 37, respray since 64, the city rhythm since 64). Each build is a separate mods block inserted before `const ARM`, and each is chained into `updateBuild86`.

**Load-order rule (the build 87 crash):** never run code at the top level of a mods block that touches anything declared later in the file (`WEAPONS`, `CAR_TYPES`, `mat()`…). Do it lazily on first update instead, e.g. `penInit87()`, `IMPG87f()`, `rigType92()`.

**Build 87: combat**
- **Penetration (`pen87`, called at the end of `fire`):**
  - Strength by weapon (`PENK87`): pistol and SMG 1, revolver, carbine and AR 2, sniper 3.
  - Car bodies and thin walls (under 0.45 m) cost 1; brick and concrete cost 3.
  - Rounds that get through do 55–60% damage (30% through brick). Tanks, armoured trucks and boats stop everything.
- **Improvised weapons (`IMP87`):**
  - Bottles, bricks and pipes lie by 90 bins and respawn after 150 s. E picks one up; it attaches to the right hand.
  - LMB swings it: bottle 20 then smashes into a broken bottle (26, causes bleeding), brick 30 (3 hits), pipe 33 (14 hits).
  - G throws it with an arc. It hits people (knockdown on a headshot), cracks windscreens and breaks windows. A thrown bottle shatters and distracts nearby peds.
  - At a gas station: a bottle plus $5 makes a Molotov.
- **Fire (`FIRE87`):**
  - Fire zones set people alight (12 hp/s for NPCs, 7 for you); NPCs flee and scream.
  - Rolling puts you out 4× faster; water puts you out at once.
  - Fire damages cars, sets off barrels, and creeps over grass outside the city (up to 14 zones).
  - Explosions ignite people within half the radius, and burning cars ignite people close by.
  - Burnt bodies are charred (`char87`), and the prints are lost. Charring is undone if the checkpoint revives them.
- **Close quarters (`SHIELD87`):**
  - A hostage builds a struggle meter (time, every shot you fire, every hit you take) and elbows free at 1.
  - At 3★ a marksman may take a 34-damage shot past the hostage if you stand still.
  - Unarmed fighters within 1 m in front of you can grab your gun when you haven't fired in 0.7 s (25%, or 45% for tough or gang). The gun drops on the ground.

**Build 88: wounds and bodies**
- **Gunshot wounds:**
  - A gunshot to a limb (`INJ88.gsw`) caps that limb at 45 until treated: you limp, or your aim shakes.
  - A body hit can start bleeding (levels 1–3). Level 1 stops after 120 s; level 2 or more can kill.
  - A health pack bandages one level of bleeding.
  - Treatment: the ER beside the hospital ($250; it reports the gunshot, adding +10 to an open case and heat if you're wanted), or a back-alley doctor shown on the map ($900, no report).
- **Blood trail:** you drop blood every 1.4 m while bleeding, and searching cops follow it by updating `lastSeen`.
- **Shattered legs:** NPCs go down crawling.
- **Bodies over time (`ROT88`):** flies after 100 s; after 300 s the smell means anyone within 35 m (50 m after 600 s) finds the body.
- **Bleach (`BLEACH88`):** $15 at gas stations. E at an unfound body's spot clears blood decals within 3.2 m, removes prints, and the case records "scene was cleaned".
- **On screen:** an injury line and a red pulse while bleeding.

**Build 89: plates and pursuit**
- **Plates (`plate89`):** a car you take gets reported stolen 45–240 s later (at once for police cars). A car the police see you in within 32 m becomes WANTED. Your plate and its status show above the speedometer.
- **Plate cameras (`PL89.cams`):** 22 at junctions, plus the bridge and causeway ends, all on the map. A hot plate passing within 24 m in line of sight gives 1★ (or refreshes `lastSeen`). Each camera rearms after 25 s.
- **Chop shops:** the existing Port Sprawl chop shop (`landmarks.chop`) and Kessler Salvage near Pinewood. Stop in a car and press E to open the garage menu (through the shop UI):
  - swap plates $300 (clears hot);
  - respray $450;
  - engine tune $1,500 (+15% speed, +25% acceleration);
  - armour plating $2,500 (1.9× hp; occupants are safe from pistol rounds);
  - repair $200;
  - strip it for parts (cash by type and condition; stolen cars only).
- **Pursuit (`PUR89`):**
  - When the police lose sight of you at 2★ or more in the city, up to 4 cruisers block the junctions 2 blocks out (`block84`).
  - PIT manoeuvre: a cruiser at your rear quarter, same heading, both over 10 m/s, spins you out.
  - Boxed in: 2 or more cruisers within 6.5 m while you're slow, and your speed is choked.
  - At 2★ or less, 12 s over 30 m/s past 6 or more pedestrians calls off the ground pursuit. Ground units go to the last spot and park; the helicopter stays on you.

**Build 90: standoffs and contracts**
- **Standoff (`ST90`):**
  - Starts after 12 s holed up indoors (or holding a hostage) at 2★ or more with 3 or more cops within 45 m.
  - Cops ring the spot at 15–20 m and hold fire. A negotiator calls (number keys; weapon keys are off during the call) with a 150 s clock.
  - Options: let the hostage go (+time, −1★); demand a car (needs a hostage or goodwill; a sedan arrives in 40 s); demand they pull back (needs a hostage; ring at 30 m for 60 s); come out (arrest); hang up (25 s left).
  - When time runs out: a flashbang (white screen, you're stunned) and 4 SWAT (140 hp, rifles).
  - Your shooting, leaving more than 28 m, or getting in a car ends it.
- **Street contracts (`SC90`):**
  - Up to 2 generated hits in Contracts, with a name, a reason, a day spot and an evening spot (their front door after 7 pm), shown on the map.
  - Each has one condition (no witnesses, an accident by car/fall/fire, a blade, or no prints and no face on camera) worth +50%.

**Build 91: events and the clock**
- **Events (`EV91`):** one every 18–40 game hours, warned an hour ahead in the news and by phone.
  - Blackout (night only): lights, signs and window glow off; alarms, plate cameras and case or heist camera evidence are dead.
  - Storm: heavy rain; Coral Key evacuated (no island peds or traffic); police ETA ×1.5.
  - Wildfire: a fire front creeping west of Pinewood with smoke columns; county ETA ×1.8.
- **Clock (`rhythm` wrapper):**
  - Weekends have no commute.
  - Friday and Saturday nights are busier.
  - Heavy rain halves pedestrians.
  - Rush-hour traffic cruises at 62%.
- **Closing time:** bars empty at 1:48–2:24 with wobbly drunks.

**Build 92: trains and rigs**
- **Freight line (`RAIL92`):** x = −1100 from z = −1050 to 650, past Pinewood, with a trestle over the river. Ties, rails and ballast are merged meshes; trees on the line are cleared.
- **The train (`TR92`):** a locomotive and 8 boxcars at up to 17 m/s.
  - It kills people on the line and smashes cars.
  - A heavy vehicle on the line, or a blast of 120 dmg or more at the engine, derails it: tilted and rolled cars, explosions, news.
  - It waits at each end and turns round when you're more than 260 m away.
  - F rides the roof when it's under 9 m/s (F again to jump off; you take damage if it's going fast).
  - E loots a stopped boxcar's cargo ($300–1,600, 1★+).
  - After a derailment it's back in service 10 minutes later.
- **Big rigs (`RIG92`):**
  - `semi92` cab (lazy `CAR_TYPES` entry) plus a 12.6 m trailer mesh, up to 2 in city traffic.
  - The trailer's rear axle follows the hitch; it jackknifes past 1.25 rad and pushes and damages people and cars it sweeps.
  - Cargo (TVs, cigarettes, pharmaceuticals…, $2.5k–14k) sells at a chop shop ("Sell the load").

**Playtest agent report (on build 86):**
- Overall score 6/10. Strongest: the investigation layer, the papers/lease flow and the jet HUD.
- Still open:
  - the rewind keeps cases and news from the erased timeline;
  - the hospital bill is announced but not charged;
  - the camera inside tree canopies and behind poles;
  - police idle instead of searching;
  - aircraft speed reads km/h labelled MPH;
  - the knife can't finish a knocked-out person;
  - burglary and stakeout prompts show in aircraft and tanks;
  - the news and case street names differ;
  - notices lag;
  - "A man" capitalised in the detective log.

## 2zz10. Update (build 86): identification takes real police work; destroyed bodies stay gone

**Before:**
- Chainsawing a body (`destroyBody`) or burning it in a fireplace (`burnBody`) set `found = true` as well as `remove`, so `updateCases` opened a case on it and the news counted it.
- Prints were "left" on every kill without gloves, gun kills from 30 m included, and always gave a name (55 points).
- Unmasked witnesses "picked your face out of a photo line-up" (42 points).
- One bare-handed street kill with a witness reached a warrant within about 4–7 minutes.
- Unfound bodies were found within 30–70 s anywhere.

**Now:**
- **Destroyed bodies:** they get `destroyed86` instead of `found`. No case opens, and the news only ever reports them missing.
- **Where prints come from:** only from a melee kill, or a body you dragged or carried bare-handed (`handled86`). A shooting leaves "shell casings at the scene: no prints on them" (2 points).
- **On file (`onFile86`):** you're on file once you've been arrested this playthrough (`REC86.arrests`) or named in a warrant (`REC86.named`, saved with the checkpoint). Both are cleared by a page reload, a fresh start. `STATS.busted` stays as the saved lifetime count for the stats screen only. An arrest can't be undone by dying, because walking out of the station at 0 stars sets a new checkpoint straight away.
- **Not on file:**
  - Prints come back "no match on file" (8 points, 4–9 game hours).
  - A clear face on camera is "nobody knows who it is" (18 points).
  - An unmasked witness gives a description, not a name (20 points). Masked witnesses are unchanged.
- **On file:** the old weights apply (prints 55, face 35, witness 42).
- **Getting arrested:** at booking, earlier "no match" prints in open cases become a match (+47) and unnamed faces get matched to your booking photo (+17).
- **The slow route to a name:** without a record, the detective is the way to get named (the detective starts at 25%, and `DET.sus` builds to a warrant).
- **The old 45-second prints check in `updateForensics`** (which added 2 stars and "police have a name") is turned off; the case file handles prints.
- **Discovery times (`findDelay86`):**

  | Where | Before | Now |
  |---|---|---|
  | Street | 30–70 s | 90–220 s |
  | Inside a building | 35–80 s | 120–300 s |
  | Inside a home | 120–220 s | 400–900 s |
  | Subway | 15–35 s | 60–150 s |
  | Bagged | 240–360 s | 600–1200 s |

  - Multipliers: ×4 on a street with fewer than 4 people within 150 m, ×2.5 in woods, ×1.5 at night.
  - Anyone who walks within sight still finds a body straight away, as before.
- **Playtest:**

  | Scenario | Result |
  |---|---|
  | Pistol kill with a witness | 31% (it used to reach a warrant) |
  | Bare-handed kill | Prints "no match", 17% |
  | Arrested afterwards | That case jumped to 84% with "a match, from your booking" |
  | Chainsawed body | Never found, no case |
  | Bare-handed kill after being arrested | Prints weighted 55 again |

## 2zz9. Update (build 85): a checkpoint that rewinds the world, jet-only missiles, sights, chain reactions

**Checkpoint (`CK85`, the `updateCkpt80` replacement, `ck85Restore`):**
- **When it's taken:** every second while you have no stars, on foot or in a car. Not while you're upstairs, on a roof, flying, skydiving, swimming or in a boat; then the last street spot stands.
- **Where you land:** a safe spot found with `safeSpot85`: dry, not inside anything, and beside the car if you were driving. Your camera faces the way it did then.
- **What's undone:** everything that happened to the world since that checkpoint. Taking a new checkpoint (`ck85Commit`) makes the current world the new baseline.
  - **People:** everyone killed since, except cops and soldiers. `revive85` stands them back up where they died: limbs and wounds fixed, out of trunks and bags, back in the house they live in, calm. Cops still get cleared on respawn as before.
  - **Buildings:**
    - Buildings that collapsed are restored by `unruin85`, newest first. The saved vertex and normal arrays of their chunks are put back, the rubble heap is removed, and the building's height and rooftop units, any stacked tower sections, the stairs and lobby doors, walls, rooms, windows, the walkable rubble (`RUIN82`) and the minimap paint are all restored.
    - Damage and smoke on buildings that didn't fall are reset too.
  - **Everything else:** broken windows, knocked-over street furniture, wall craters and ground decals are put back, and wrecks are removed.
  - **Aircraft you took or blew up:** back on their stand or helipad, unburnt.
- A message says how many people and buildings came back.

**Missiles (fighter jet only):**
- `armPlane80` gives every aircraft guns, bombs and flares, but missiles only on the F-29 jet. Helicopters, including the attack helicopter, and prop planes no longer have them. The controls panel and the enter-plane hint match.
- **Seeker (`pickTarget`):** it holds the target it has (a 2.4× wider cone and much stronger preference once locked, out to 1150 m), so it no longer flips between targets.
- **The player's jet missiles (`homeRocket`, tagged `pn85`):**
  - They estimate the target's velocity and steer at the point where they'll meet it.
  - They turn at most 3.6 rad/s after a quarter-second to clear the jet, and speed up to about 150 m/s.
  - A proximity fuse goes off within 6 m. If a missile overshoots past about 110°, it goes ballistic.
- **Camera feeds (`renderPip`):** the targeting-pod and missile-camera feeds render at ≤1× pixel ratio, sharing about 30 renders a second between them. This was the main source of lag on a high-res, high-refresh display.

**Sights (`AIM85`, `drawAim85`):**
- **Gun:** the gunsight sits where the rounds actually land: the first ground or building along the gun line, up to 280 m, with the range shown. The cannon itself now stops at buildings too.
- **Bombs:** whenever you have bombs and are airborne, a dashed red ring the size of the blast (16 m) and an X mark where they'll land, with the time to impact. The fall is simulated the same way as `updateBombs80`.
- **Tank:** a reticle where the main gun's shell will land from where the turret points right now, with range and loading state. Yellow while the turret is still swinging toward your view, green when it's lined up. A small cross marks where you're looking.

**Chain reactions (`explodeAt` and `crashPlane` wrappers):**
- **Any blast:**
  - Cars within 65% of its radius catch fire and go up 0.15–0.5 s later (not tanks or boats). Their explosions set off the next ones.
  - Parked aircraft within reach explode.
  - Street furniture within 75% of the radius is knocked flying (not the airport barrier).
  - Windows within 80% of the radius blow out.
- **Any aircraft crash** is a fireball, slow ones included. A fast crash into a building brings it down: up to 60 m tall for helicopters and prop planes, up to 170 m for jets and airliners.
- **Cars:** a really hard wall hit (impact above 42) sets the car on fire, and it explodes a few seconds later.

## 2zz8. Update (build 84): roadblock tiers, rooftop helipads

**Roadblocks by star level (`roadblockTick84`):**
- **2★, patrol cars only (`patrolBlock84`, `blockAI84`):** in the city, while you drive fast (over 12 m/s), up to two patrol cars already chasing you peel off to block the road about 2.6 blocks ahead. The closest car keeps tailing you. A car is only picked if it can get there before you (its drive at 17 m/s is no more than 1.5 s longer than yours), it isn't behind you, and it's within 520 m of the spot. At the spot it brakes, swings across the lane, and an officer steps out on the far side. Then it becomes a normal parked roadblock. A car that hasn't made it after 30 s gives up and goes back to chasing. You see "Patrol cars are blocking the road ahead!". No new units and no spike strips at 2★.
- **3★ and up:** new units come out with roadblocks (`spawnRoadblock`; country roads use `countryRoadblock`). Spike strips (`spikeAhead`/`spikesAhead`) and the bridge/causeway gates also start at 3★ (spikes used to start at 2★).

**Rooftop helipads (`PADS84`, `padsSetup84`):**
- Up to 8 pads on stair-tower roofs, at least 140 m apart. A roof is skipped if a taller part of the building hangs over it, if a rooftop unit is within 5 m, or if there's less than 4.8 m clearance.
- Each pad is a dark disc with a yellow ring, an H and green edge lights, with a privately owned helicopter in one of several paint schemes (`padHeli84`).
- **Owners (`padOwner84`, `updatePads84`):** every 70–130 s, if you're within 400 m, a business owner comes out of the stair hut and walks to their helicopter. Only one owner per pad at a time.
- **Owner flights (`heliFly84`):**
  - Phases: up 40 m → cruise at 34 m/s → straight down at 5 m/s onto another free pad (half the time), or off out of town, where it's removed.
  - The cruise height is set once; when a taller tower is ahead it climbs over it before carrying on.
  - Away pads get a helicopter back after 200–400 s (it flies in from 900 m), and the owner then walks back to the hut.
- **Stealing one:** you can take a parked rooftop helicopter (not one an owner is flying).
  - A tap of F on the roof climbs back out onto it (`exitPlane` and `bail80` wrappers).
  - Helicopters now rest on their skids on roofs: the roof check runs at skid height while descending, so they no longer sink and bounce, and roof exit works every time.
  - A pad whose helicopter is taken or destroyed gets a new one later.

## 2zz7. Update (build 83): police take as long as the drive does

**Before:** new units appeared out of sight but close. The officer on foot at 1 star came from 35–60 m, patrol cars from 150–260 m (80 m out of town), and the helicopter from 140 m. Normal traffic also kept creating fresh patrol cars near you, which joined the chase within seconds.

**Dispatch (`DISP83`, `dispatchStart83`):** the moment you're wanted, the game works out who's coming and when.
- **From a station:** the nearest one by driving distance: the Sprawl PD station, the county sheriff's office in Pinewood, or the Havenport PD station. To Coral Key they come over the bridge.
- **Or a patrol already close:** a unit that was already within 450 m when it happened gets there first.
- **The arrival time:** a call delay (6–12 s; about 1 s if police saw it) plus the drive (city about 14 m/s on a winding route, country about 16 m/s). City arrivals take 15–95 s, country 30–210 s.
- **On screen:** a notice says where they're coming from, and a line at the bottom counts down ("Police en route from … · ~40 s") until someone's within 120 m.

**Until it's plausible that someone could be close (15 s before the arrival time):**
- **New patrol cars:** they set off from the station itself and drive the whole way (`postSpawn83`).
- **Officer on foot:** none before the arrival time.
- **Blocks:** no roadblocks, spike strips or country roadblocks until 10 s after that.
- **Havenport:** its loop patrols don't spawn.
- **Traffic:** no new police cars appear in city or highway traffic at all while you're wanted. Patrols only join the chase if they were already on the road before the call (`born83`).

**The helicopter:** it starts 450–1,400 m out, in the direction of the station, and says so ("on its way from the Sprawl PD station").

**Out of town:** highway patrol backup appears 260–520 m away (was 80–220).

**Tested** (sound off, stepped):

| Where | Estimate | What happened |
|---|---|---|
| City, 450 m from the station | 57 s | First car within 100 m at 48 s, closing |
| Countryside, 1 km from Pinewood | 65 s at first; formula corrected | Sheriff's car drove the whole way |
| Near an existing patrol | 16 s | That patrol responded |

No console errors.

**Rebuild:** `cp backup_b82.html index.html; python3 p102.py`.

---

## 2zz6. Update (build 82): a heist in every town, grass kept out of everything, more country roads, rubble you can climb, jumping up onto things, a proper drag

**A heist in every town (`VAULT82`, `vaultSetup82`, `updateVault82`):** each of the seven towns has a safe job on the phone's heist board (Contracts), with the usual prep: scout it, tools, a getaway car.

| Town | Where the safe is |
|---|---|
| Havenport | HARBOR 24/7 |
| Pinewood | General Store |
| Westbrook | West Pharmacy |
| Sprawl City | Lucky Mart |
| Cedar Falls | Cedar Savings & Loan (new) |
| Snowcrest | Snowcrest Trading Post (new) |
| Coral Key | Coral Cash & Carry (new) |

- **New shops:** the last three towns had no building you could walk into, so each now has a real shop with a counter and a clerk (`townShops82`, placed on the first free, flat, roadless spot).
- **The safe:** a steel safe with a dial at the back. During opening hours a guard stands inside the door.
- **Scouting:** 8 s inside in opening hours.
- **Cracking:**
  - **Stethoscope:** quiet, 16 s, as long as nobody sees you.
  - **Thermite:** 8 s, and it sets off the alarm and brings 3 stars.
- **The take:** about $4,000–9,000 in a bag, which goes to Sal as before.
- Tested at Coral Key: planned, cracked quietly, $6,283 in the bag, no stars.

**Grass out of everything (`capture82`, `GRASS82`):** while the city's pieces are merged, everything outside the city that sits on the ground marks its patch at a 1 m grain. That covers buildings, porches, pads, paths, fences, piles, signs and camp pitches; small things by their footprint, large things triangle by triangle. Grass can't grow there. About 530,000 cells are marked.

**More country roads (`ROADS82`, `GRAVEL82`):**

| Road | Type | Runs |
|---|---|---|
| Pine Hollow Road | Paved | Valley Road → Kessler Back Road, south of the base (1.7 km) |
| Quarry Road | Paved | Havenport Road → North Pass Road (0.5 km) |
| Orchard Road | Paved | Cedar Falls road → Valley Road (0.6 km) |
| FS Road 21, 7, 12, Logging Road | Gravel, 6 m | Off the paved roads into the woods |

- **Paved roads:** graded into the land like the others, with traffic paths and place names.
- **Gravel roads:** no pines or grass grow on them.
- **Dirt tracks:** the camp trails from build 81 are still there.

**Rubble you can climb (`RUIN82`, `ruinY82`):** when a building comes down, its walls and everything inside stop being walls. You can walk onto the heap and across it: the ground follows a mound that's highest in the middle, with a ramp at the edges. Its rooms stop counting as indoors, and a house's window glass goes too (it used to float in the air).

**Jumping up onto things (`mantle82`, `surfAt82`):** press jump facing something 0.45–2.25 m high and you climb up onto it.
- **What counts:** anything solid on the ground (walls, planters, containers, crates, hut roofs, rubble), plus benches, bins, news boxes and mailboxes, and parked or stopped cars.
- **A car roof:** it carries you if it moves. If it speeds off you're thrown.
- **Moving about:** walk across to the next thing at about the same height, or step off the edge and drop. While up there, walls still stop you, but the thing you're standing on doesn't.
- About 29,000 climbable surfaces.

**Dragging a body (`poseDragged` rewritten):** you face the body, bent over with your hands under its arms, and walk backwards. Its upper body is lifted about 30°, its head lolls back, its arms hang out to the sides, and its heels scrape behind with dust and the odd smear.

**Tested** (sound off, stepped):
- Climbed onto a parked police car, walked along the roof and dropped off the end.
- Blew up a house and walked up onto the rubble heap (height following the mound).
- A town heist from plan to bag.
- Grass stops short of houses and paths in Cedar Falls.
- Drove onto Pine Hollow Road.
- The drag, from the front and the side.
- **Frame cost:** game update about 2–3 ms per frame, with no console errors.

**Rebuild:** `cp backup_b81.html index.html; python3 p101.py` (p101.py applies p101mods.js).

---

## 2zz5. Update (build 81): police on the stairs, aiming at the ground, armed planes, launchers you can see, interceptors, checkpoints, a manhunt that has to find you, wider country roads, camps and trails, front yards, shop robberies everywhere, a new Coral Key

**Police on the stairs (`copBld79` rewritten, `climbPath80`):**
- **Walk-in buildings:** officers used to jump from floor to floor at the stair door, and pop through the front door. Now they walk in through the doorway and climb every flight and landing, with their height following the steps. They also walk out onto the roof, and back down the same way.
- **Houses:** coming down from the upstairs landing, they now step straight onto the top of the stairs instead of jumping a metre down them.

**Aiming:**
- **The ground:** aim at the ground and the round goes into it, where the crosshair meets the ground (`groundT80`), with dust and a mark. The crosshair's aim point stops there too.
- **RPG:** it now flies at the point under the crosshair, in 3D; it no longer locks on by itself. Hold aim (right mouse) on a car, helicopter or plane for 0.9 s and the seeker locks: a box closes in and turns red at "LOCKED". The next rocket then homes in (`rpgSeek80`).

**Planes (`planeHud80`, `armPlane80`, `dropBomb80`, `bombBlast80`):**
- **Controls on screen:** a controls panel shows whenever you're flying.
- **Bailing out:** the bail-out key has to be held for 0.8 s in the air (a tap still climbs out on the ground).
- **Weapons:** every aircraft you take has a cannon (left mouse), missiles (right mouse), flares (E, helicopters too) and bombs (B; 6, or 8 in a jet).
- **Bombs:** a bomb blast (radius 16) can bring down any building, the big towers included. Two bring down most; one is enough for a house.
- **An abandoned plane:** jump out and it noses down and comes down hard, with the same kind of blast. That makes bailing out over a target a manoeuvre.

**Fort Kessler's launchers (`samTick`):**
- **Visible:** launches show smoke, a flash and the rack lifting.
- **Line of sight:** they only fire with a clear line over the hills.
- **Warnings:** you're told the launch came from the Fort Kessler launcher, how far away and which direction. Red circles at the edge of the screen point at each missile coming for you, with its distance. The launchers are boxed "SAM" on screen.

**The police helicopter:**
- **Look:** a glass band all round the cabin, a pilot inside, and a gunner at the open left door. Its rounds come from the door.
- **Plane chase:** it can follow you into the air, side-on so the gunner faces you.

**A stolen plane in the air:**
- **Stars:** you're at 3 stars and the chopper comes up after you.
- **The air force:** after 55 s (or if the chopper's shot down) an interceptor jet takes off from Fort Kessler (`jetSpawn80`, `jetFly80`). It leads its aim, keeps off the ground, uses guns up close and fires a missile every 7–10 s from range; flares break the missiles.
- **A second jet** follows at 140 s.

**Checkpoints (`CKPT80`):** while you have no stars, your position, cash, gear and the police files are saved every 4 s. Dying puts you back there as it was, instead of a hospital bill and a wiped record. Busted is unchanged. Reloading the page is still a fresh start.

**Gloves** last about 40 minutes of wear (was 16), and blows tear them a third as fast.

**The manhunt has to find you:**
- **The police chopper:** it used to circle your real position even when nobody had seen you. Now it searches round where you were last seen (`lastSeen`), in a widening circle.
- **Being seen:** police on foot, in cars and in the air need a real line of sight. Out of town, hills block it, and in the woods you can't be seen beyond about 22 m on foot (`sightOK80`, `terrainLOS80`, `inForest80`).
- **After a five-star escape (`SEARCH80`):**
  1. **The sheriff's helicopter** (tan, with a sweeping spotlight) flies a widening spiral over where they lost you. It only spots you in the open, within 75 m, with a clear line, and only if you still match what they're looking for: the same top, the mask on or off as before, or the same car.
  2. **The satellite:** after 2.5 minutes they ask the military for a satellite pass. You get 30 s on screen, with a line saying whether you're covered or match.
  3. **The scan:** if you're in the open and match, the stars come back. If it sees the car you fled in parked outside, two units drive there.
  - **Cover:** indoors, under trees, under a bridge or overhang, or underground.

**Wider country roads:** the highway is 15 m (was 12) and side roads 10 m (was 8). The ground is flattened to match, the edge lines, guard rails and junction trims have moved out, and highway traffic drives 3.6 m off the centre.

**Buses (and anything long) in houses (`carGuard80`):** each AI vehicle's front, middle and back are checked every frame. If any is inside a house or a building, it's put back where it last was clear. If it stays stuck for 2.5 s out of your sight, it restarts on the nearest road.

**Map scan (all 1,891 houses):**
- **Ground through floors:** none.
- **Trees in houses:** none.
- **On slopes:** 31 houses on steep ground out west stand up to 6.7 m above their low corner. They rest on their own foundation walls, so they were left as they are.

**Camps and trails (`CAMP80`):** modelled on US Forest Service campgrounds near Bend, Oregon, in the Deschutes National Forest. Each site there has a picnic table and fire ring, and China Hat campground is built around off-road trails.
- **Where:** four camps: Pine Lake, Silver Lake, Mirror Lake and the Kessler OHV camp.
- **The camp:** a gravel loop with 6–10 numbered sites. Each site has a pad, a tent or camper trailer, a picnic table and a stone fire ring with embers and smoke. There's a vault toilet and a sign at the entrance. Campers stand round the fires when you're near.
- **Trails:** dirt trails run from each camp out to the nearest road, and a loop runs through the woods round each one (wider at the OHV camp). No pines or grass grow on them.

**Front yards (`yards80`):** every home gets a mailbox with its flag up at the path, two bins by the side, potted plants and a mat at the door, and a porch light. That covers about 1,880 homes in every town.

**Robberies everywhere (`ROB80`):** every 2–4 minutes (more often at night), a masked man robs a shop near you, in any town. He walks in, holds up the clerk ("Empty the register!"), runs off after 7 s, and a patrol is sent. Stop him and you're a hero; let him go and it makes the news. Tested at Westbrook Mart.

**Coral Key (`coralStreets80`):** the villas used to sit scattered on a bare lawn. Now there are two residential streets with pavements and links to the main road. Each house faces the street with a front yard, a driveway, hedges, a mailbox and a pool out back, and there are palms, street lamps and some cars in the drives.

**Tested** (sound off, stepped):
- An officer walked in and climbed two floors.
- A round went into the ground 2.7 m ahead.
- A bomb dropped, and a building came down to two bombs.
- An interceptor came from the base and attacked.
- Bail-out took a 0.8 s hold; the empty plane dove and crashed within 3.5 s.
- The sheriff's helicopter spotted me in the open (3 stars), and the satellite found me in the open (4 stars).
- All four camps built, with campers.
- A robbery ran from start to escape.
- **Frame cost:** game update about 4.5 ms per frame, with no console errors.

**Rebuild:** `cp backup_b80.html index.html; python3 p100.py` (p100.py applies p100mods.js and p100b.js).

---

## 2zz4. Update (build 80): a cooler-running city

The Mac (a fanless MacBook Air) was reaching 101 °C with the game open.

**Measured at the start spot, one frame:**

| | Before | After |
|---|---|---|
| Triangles, main pass | 5.58 M | 4.02 M |
| Triangles, with the shadow pass | 8.42 M | 5.63 M |
| Draw calls | 869 | 1,047 |

Most of the cost was merged static scenery drawn right out to the fog line.

**What changed:**
- **Details split out:** small static pieces (anything under 2.6 m: signs, bollards, kerb stones, house furniture, rooftop clutter) now merge into their own 176 m tiles. They're drawn only within about 320 m (420 m from a plane), where they're more than a few pixels. Buildings, roads and the land still draw to the fog. Draw calls are up a little; triangles are down about a third.
- **Shadows:** the shadow pass draws far fewer triangles, since the details near you are in small tiles.
- **Medium quality:** render scale 1.0 (was 1.1) and 2× anti-aliasing (was 4×).
- **Title screen:** idles at 20 fps (was 30).
- **Unchanged:** gameplay stays capped at 60 fps.

**Outside the game:** a 4K external monitor at 240 Hz keeps the GPU and WindowServer busy all the time. Dropping it to 120 Hz or 60 Hz cools things noticeably, and the game is capped at 60 anyway.

**Rebuild:** `cp backup_b79.html index.html; python3 p99.py`.

---

## 2zz3. Update (build 79): insides with colour, a camera for halls and stairwells, police who follow you in, bodies that get found, witnesses with a day of their own, a subway you walk down into

**Walk-in buildings (`bldPal79`, `bldLit79`, `bldDecor79`):** they were drawn unlit in near-white, so every inside looked the same and too bright.
- **Colours:** each building gets its own wall paint, floor, dado, trim and ceiling tint, picked from palettes by use (flats, offices, lobbies, shops, gyms, clinics, storage). Flats and offices change floor by floor. About half get one feature wall in a stronger colour.
- **Light:** a room-light falloff (dimmer at the floor, brightest at eye height) and a warm or cool tint per building. Lamps, signs and screens keep their glow (`LIGHT79`).
- **Things in rooms:** framed pictures on the stairwell wall, rugs, plants, a water cooler in offices, painted lanes in storage. Flats also get a TV facing the sofa and a dining table with chairs.
- **People:** spots are nudged and turned so no two floors look staged the same. Desk workers often sit at their desks and residents on the sofa (they get up if anything happens). Some wander the floor on a path round the furniture (`bldGrid79`, `bldWay79`). Some stand in pairs talking; the rest have their own idle (arms crossed, hands in pockets, checking a watch, on the phone).
- **Stairs:** the flights and landing stood flush against the stairwell walls and flickered; they now stand clear by 1.5 cm, and the treads alternate shade.

**Camera:**
- **Stairwell:** no longer drops into first person (that snap was the "glitch"). It stays third person, centred, a little higher and looking down the flight, kept inside the stairwell.
- **Halls (`hallTight79`):** it measures how wide the space is either side of you. In a narrow hall it centres behind you, shortens the boom, lifts it slightly, widens the lens and tips down a touch. Two extra rays either side of the boom stop it jumping in and out at door frames (`boomSides79`).

**Stairs that floated:** City Hall's front steps were three slabs in the air; they're solid to the plaza now. The beach lifeguard towers' back steps stand on legs. The old subway entrance (a dark slab with steps hovering above the pavement) is gone (below).

**Police come in after you:**
- **Walk-in buildings (`copBld79`):** if they saw you go in (or you're at 3 stars), officers within 75 m go to the door and come in. On a different floor they take the stairs one floor at a time, out onto the roof if that's where you are. Once on your floor, the normal chase takes over. When you leave, they come back down and out.
- **Houses (`copHouse79`):** once inside, an officer goes straight to the foot of the stairs, climbs them and steps onto the landing; if you go back down, they follow.
- Tested: a cop climbed from the street to floor 2 of an office in about 4 s and opened fire. Another climbed a house's stairs and made the arrest upstairs.

**Bodies get found (`updateFind79`, `sendFinder79`):** your bodies used to vanish once you were 110 m away or after 30–100 s, before anyone found them, so the news came out as "missing".
- They now stay until someone finds them.
- If nobody happens by, someone comes: a passer-by from round the corner after 30–70 s outdoors, a co-worker on a building floor after 35–80 s, or a neighbour or family member coming in the front door after 2–4 minutes at a house. A bagged body takes 4–6 minutes.
- If you're far away (over 95 m), it's found off-screen.
- Who found them is recorded for the news.

**Witnesses (`WIT79`, `wit79Pick`, `updateWit79`):** at the moment of a killing, one person who saw it (if anyone's willing) becomes a witness and lives out a day:
1. **Flee:** they run (about 5.4 m/s) to a building 70–230 m away, the far side from you where they can.
2. **Hide:** they stay inside for 45–90 s. If it's a walk-in building and you go in, they're in the lobby, cowering.
3. **Go:** they come out and walk home (or to another building).
4. **Call:** they phone the police (on the phone, talking). That reports the body if nobody had found it yet.
5. **Wait:** they stand outside for 18–35 s.
6. **Picked up:** a patrol car (or the detective's unmarked car, if a detective has the case) drives to the kerb. The officer walks up, has a word, walks them back, and they both get in. The car drives off towards the station.
7. **Statement:** the case gets the witness's evidence, with a news story.
- Kill them at any point and they're silenced. Wanted and nearby? The pickup waits, and the officer turns cop on you.
- The phone's Cases app and the W map marker follow them through each step ("ran from the scene", "hiding inside a building on…", "waiting on … for the police", "being picked up by…").
- Away from you the whole thing runs on timings, and they reappear where they'd be when you come within about 110 m.
- Tested end to end: fled 228 m, hid, walked home, called, waited, picked up, statement.

**News:** stories now have a headline and a line under it (`bodyNews`, `newsHTML79`), e.g. "Businessman beaten to death on Ocean Ave · Channel 6 News: A businessman was found on Ocean Ave in Downtown this afternoon by a jogger. He has not yet been named. Officers are going door to door."
- **How:** shot dead, stabbed, beaten to death, run down, killed in a blast, struck by a train.
- **Where:** a home, a building, a station platform or a street.
- **Who:** the victim is named with their age about 60% of the time. Who found them is included.
- **Witness stories:** a witness's statement makes its own story.
- **Timing:** the reporter-on-scene delay is 45 s (was 80).

**The subway, walked into (`buildSubway` rebuilt, `sub79*`):**
- **The entrance:** at each of the four entrances a real stairwell opens in the pavement. Green railings, a glass canopy, the globe and sign. The land, paving and coast ground are cut away over it (`sub79CutGround`, `sub79CutTerrain`).
- **The stairs:** 26–28 solid steps go down 4.6–5 m between tiled walls, with the station's colour band, handrails and yellow nosings. A ceiling starts where there's headroom.
- **The doors:** at the foot, a small hall and a pair of steel doors that slide open as anyone comes up to them. Walk through and you're in the ticket hall: gates, a ticket machine, a low lit ceiling, then the platform.
  - How it works: the station is still built out of sight east of the map, so the street above never has to know. The doors are a seam: both sides look the same (the ticket hall is copied behind the street doors and the foot of the stairs behind the station doors). Walking through moves you, turned so the camera doesn't jump (`sub79Teleport`). The minimap keeps showing the station's place in the city.
  - No E to go down or up any more.
- **Trains:** walk in through an open door to ride to the next stop (E still works). Once you arrive there's a 5 s pause before the doors will take you again.
- **Police:** officers who saw you go down follow you down the stairs and through the doors, and come back up after you. With stars on you, transit police come in through the ticket hall doors every 9–14 s (up to 1 + stars). Patrol cars aim for your station's entrance rather than the far-off platform.
- **Light:** a soft light goes with you underground.
- Tested: walked down (y 1.65 → −2.95) and through to Pearl St's ticket hall, and back up the same way. A cop followed from the street into the station. Walked onto a train and arrived at the next station.

**Test hooks:** `window.game.B79` has `step(n)`, which runs n game frames and draws one; the hidden browser pane only runs about one frame a second. It also has `WIT79`, `SUB79`, `CAM79`, `roadNear79`, `copBld79`, `copHouse79` and others.

**Frame cost (hidden pane, stepped):** about 3–4.5 ms of game update and 5.6 ms to draw. No console errors.

**Rebuild:** `cp backup_b78.html index.html; python3 p98.py` (p98.py applies p98mods.js and p98sub.js).

---

## 2zz2. Update (build 78): roomier houses, shooting through windows

**Roomier houses:** the tight spots were the problem (measured across all 1,890 houses: a 1.0 m upstairs hall, 1.7 m downstairs toilets, a narrow kitchen doorway).
- **Footprint:** houses without a garage are about 0.6 m wider (capped at 11 m so neighbours' eaves stay clear) and 0.5 m deeper. The same random draws are used, so streets are otherwise unchanged.
- **Upstairs hall:** 1.45 m wide (was 1.0).
- **Downstairs toilet:** 2.1–2.2 m (was 1.7–1.9). Single-storey bathrooms 2.3–2.5 m (was 2.0–2.2).
- **Kitchen:** opens onto the living room through an arch up to 3.2 m wide (was at most 1.6), so the ground floor reads as one open space.
- **Typical rooms now:** living room 10.4 × 5.1 m, kitchen 6.5 × 4.1 m, bedrooms upstairs about 7 × 4.5 m.

**Shooting through windows** (`fireWallT`, `winOnWall`): before, a round fired upstairs stopped at the outside wall, and ground-floor windows were solid walls to bullets too.
- **Out:** a round that meets a window opening goes through it (breaking the glass) and carries on outside, upstairs or down. Solid wall still stops it.
- **Aiming:** the crosshair's aim point uses the same rules, so it locks onto people outside a window.
- **In:** when you're upstairs, a round from outside that meets your window comes in.
- **Being seen:** with a star or more, police outside can see you at an upstairs window (`losClear`), so they shoot back. With no stars, nobody notices you up there, so sneaking about isn't affected.
- **Wall thickness:** at an angle the round has further to go through the wall; that's accounted for (`passT`).

**Rebuild:** `cp backup_b77.html index.html; python3 p97.py`.

---

## 2zz. Update (build 77): steady ground, grass out of the walls, ragdolls that rest, E that does what's in front of you

**Ragdolls twitching up and down:** build 76 ran the self-collision and an extra bone-length pass *after* the solver, with "velocity-free" fixes. Those fought the bone lengths and the ground every step, so bodies never went to sleep and knees and feet bobbed through the floor.
- **One solver:** self-collision and the knee/elbow hinges now run inside the solver loop (`ragStepFixed` rewritten), as plain position fixes; the floor has the last word every pass.
- **Settling:** a body also sleeps once its hips and head have moved less than 5 cm in a second (`R.anc`), whatever the fingers do. A kick or shot wakes it as before.
- **Measured:** eight bodies thrown at once all come to rest; the worst limb overlap is 4 mm (was 3 cm).

**Bodies thrown indoors:**
- **Ceilings:** a body can't pass through the ceiling (`ragCeil`, from `room.ceil`; the stairwell is open). Before, a throw from the shoulder put the head half a metre into the floor above.
- **Walls:** limbs no longer get pushed through a wall after the wall check (the cause of "out through the wall, then back in").
- **Upstairs:** limbs stay inside the outer walls (they used to hang 0.5 m through them), stop at the inner walls, and land on beds and desks rather than being shoved off them. A body thrown into the stairwell falls down the stairs.

**Bodies through windows:**
- **Carrying a body, facing a window from inside:** E throws it through (it smashes the glass first). The prompt says so. Works upstairs and down; bagged bodies too.
- **Thrown (LMB / Y) at a downstairs window:** it goes through instead of bouncing off the wall beside it (`ragWinThrough` runs before the wall bounce; the old check ran a frame too late).

**E does what's in front of you** (`eForBody`): E is both interact and carry. It used to always mean the body if one was near, so you couldn't smash a window, open a door or take loot with a body at your feet.
- **Not holding anything:** whichever is closer and more in front of you wins: the body (drag) or the window / door / loot / drainpipe / lift / locker / display case.
- **Carrying:** at a window you face, throw it through; at a door, open the door; otherwise put it down (fireplace and trunk as before).
- **Prompt:** shows the action E will actually do. Inside a house, the "Smash the window" prompt now shows (the chain used to come back empty there).

**Police:** one kill used to bring six cars and four officers, because every patrol car within 150 m joined the moment you had a star, ignoring the cap.
- **Patrol cars** only join if the response for your stars isn't already there (`COP_CAR_WANT` = 0, 1, 2, 3, 4, 6 cars).
- **Caps:** at most 2 officers at one star, 3 at two, 5 at three (`COP_CAP`). One and two-star cars carry one officer.
- **Measured:** one star: 1 car, 1–2 officers. Two stars: 2 cars, 2 officers.

**Sleepers:**
- **Hitting them:** a sleeper's hit area was a circle at their feet, so a shot at the head missed and the bang woke them. Now the whole body, feet to head, can be hit, and where the round lands along it picks head, body or legs (`sleepRayT`).
- **Upstairs shots:** shots fired upstairs in a house were stopped by the ground floor's walls and furniture underneath. They now use the upstairs walls (`fireWallT`). This is why shooting Hale in bed did nothing.
- **Getting up:** anyone who wakes without the get-up animation (Hale, the mayor) now sits up and climbs out of bed over a second instead of jumping to the side of the bed (`sleepWake77`).

**Grass in the walls, ground flicker:**
- **Grass tufts** (the wind-blown ones outside the city) no longer grow within 0.55 m of walls, fences and porches, inside buildings, or on house lawns (`grassBlocked`). The roadside country houses had tufts growing into their walls and through their lawns.
- **Ground flicker:** the mountain terrain gives way in the depth test (polygon offset) to anything laid on it (lawns, drives, pads), so they no longer flicker against it from a distance.
- **Pinewood:** the boardwalk in front of every shop sat exactly in the plane of the shopfront, so the bottom of each wall flickered. It now stands 5 cm out.
- **Grass you could walk through:** the hedges in overgrown city lots, the long hedges at Silver Lake Estates and the shrubs behind the modern houses' front walls are now solid.

**Houses glitching as the camera closes in:** standing beside a house, the over-the-shoulder offset pushed the camera into the wall before the wall check, so you saw inside the siding.
- **Shoulder offset:** shortened when a wall is beside you (`camShoulder77`).
- **Safety check:** if the camera still ends up inside a wall, it slides back toward you until it's clear (`camFix77`).
- **Wall right behind you:** the camera rises a little and looks over your head, and your head is hidden while it's that close.

**Rebuild:** `cp backup_b76.html index.html; python3 p96.py` (or from build 73: `cp backup_b73.html index.html; python3 p93.py; python3 p94.py; python3 p95.py; python3 p96.py`).

---

## 2zy. Update (build 76): ragdolls that hold together, a proper grab, things carried in your hand

**Ragdolls:** the bodies are 15 particles joined by fixed-length links, so arms and legs used to pass straight through each other and through the torso.
- **Self-collision:** every physics step (`ragSelf`), capsules (torso, forearms, thighs, shins) and points (head, elbows, knees) push apart: forearms against the torso, the head, the other arm and both legs; shins against each other and the torso; the head against the legs.
- **Joints:** knees bend backwards only and elbows forwards only (`ragHinges`). A joint bent the wrong way is eased back straight. The check is skipped when the limb is swung out sideways, where the hinge axis no longer lines up with the hips.
- **No jitter:** the fixes move a particle's previous position along with it, so they add no velocity and bodies still settle and go to sleep.
- **Extra limits:** the head can't fold into the hips, and hands, feet and knees keep a little apart.
- **Measured:** the worst overlap on six thrown bodies was about 3 cm (forearms touching).

**The last red squares:** wounds on people in cars, and the far-away stand-ins, were flat 7 cm red boxes. They're now the wet wound splat (`WOUND_G` became a plane). Blood on car seats uses the spray texture instead of a flat 7-sided disc.

**Grabbing:**
- **Pull-in:** they're pulled in over 0.28 s to 0.36 m in front of you, against your chest. They're a ghost while held, so the push-apart between people doesn't shove them back out to arm's length.
- **Your pose:** your left forearm goes across their throat. With a pistol, revolver or SMG the muzzle goes to their temple (until you aim). A long gun is held low; with fists you grip their shoulder.
- **Their pose:** they claw at your arm, head back, and their heels drag in step as you walk.

**Carrying:**
- **Loot bags and the briefcase** hang from a free hand: the right hand with fists, the left when the right holds a gun. Anything else goes over your back. Aiming, fighting, grabbing, dragging, climbing or driving moves them to your back (`carryLayout`).
- **Hand pose:** the carrying arm hangs straight with less swing, and you lean away from the weight.
- **Bodies (fireman's carry):** the body sits on your right shoulder, the side your right arm holds it, instead of across your head.

**Rebuild:** `cp backup_b73.html index.html; python3 p93.py; python3 p94.py; python3 p95.py`.

---

## 2zx. Update (build 75): blood that looks like blood, no more floating red

**Floating red after respawn:** bullet and blade wounds were flat red squares placed at a fixed 0.168 m from the chest centre, about 4 cm off the actual body. They were also never removed.
- **Placement:** each wound is now found with a ray against the body's real surface (`addWound`), so it lies on the clothes, vest or skin wherever it lands, on any body shape.
- **Look:** a small dark, wet splat texture instead of a square.
- **Respawn:** clears every wound, the bleeding and any half-finished finisher or dive (`clearWounds`).

**Blood that looked like red paper:**
- **Ground pools and splatters** use a splat atlas (`BLOOD_GROUND_TEX`, 4 tiles) instead of perfect circles. Big decals get rounded pools with satellite drops; small ones get spiky splatters and droplets. Each is darker where it's thick.
- **Sheen:** roughness 0.88 and a weak environment reflection. Any glossier and the sun's highlight turned the pools pale brown.
- **Wall blood** (exit spatter, wall slams) has its own instanced mesh with a spray texture that has runs dripping down. Bullet holes stay as they were.
- **Night:** blood droplet particles darken at night (they're unlit and used to glow).

**Animation:**
- **Closing in:** the finisher approach (and the chain dash) takes real running steps instead of sliding.
- **Parry:** a forearm deflection with a twist of the shoulders.
- **Shootdodge:** the legs trail together and tuck as you land, and you roll back upright over a third of a second instead of snapping up.
- **Disarm:** the gun is in your hand for the strike.

**Code:** `p94mods.js` and `p94.py`. Test hooks are under `window.game.BLOODT`.

---

## 2zw. Update (build 74): close quarters (parries, finishers, disarms, a human shield, the shootdodge)

**Parry:** block (RMB, fists or melee) just as a punch or kick comes in, within about a third of a second. You take nothing, the attacker is knocked off balance (slow-mo blip, PARRY), and they're **open**. Holding block early is still an ordinary block.

**Open enemies:** parried, hit with a heavy blow (hook, uppercut, round, spin or flying kick, bat), or worn below 35% health. A diamond marker and the prompt say what a click will do.

**Finishers (LMB on an open enemy):** the move is picked from what's around them (`finKind`):
- **Wall slam:** a wall right behind them. Blood on the wall.
- **Car slam:** a parked car behind them. Dents it.
- **Shoulder throw** or **knee + elbow:** open ground, alternating.
- **Gutted:** with a knife or blade. Kills.
- **Home run:** with a bat. Launches them; kills if they're nearly done.
- **Disarm:** fists against someone pointing a gun at you from within 2 m (no need to be open). You take their pistol, SMG, shotgun, rifle or revolver plus ammo, then butt them with it.
- **Death from above:** click while falling onto someone.
Everyone except the knife victim is knocked out (the usual 24–40 s), and it's reported like any assault. The camera swings round and punches in during the move.

**Chain takedowns:** finish one with another attacker within 7 m and the world slows. Click while it's slowed and you dash up to 6.5 m into the next finisher, and so on (CHAIN ×2, ×3).

**Human shield:** grab someone (hold Y) with a pistol, revolver or SMG out. You can aim and shoot past them, and your shots don't hit them. Most shooters hold fire ("Hold your fire! He's got a hostage!"); elite guards don't. Their bullets can still hit the hostage. With fists or a two-handed gun, a click still throws them.

**Shootdodge:** dodge (Z) while aiming a gun: a sideways dive (or whichever way you're moving) in slow motion, laid out flat and still shooting, with tighter spread. Enemy aim is worse against you mid-dive.

**Aiming:** the hit marker turns gold on headshots.

**Code:** `p93mods.js` (`CQ`, `FIN`, `cqTarget`, `finKind`, `startFin`, `updateFin`, `parry`, `startDive`, `updateShootDive`) and `p93.py` (the hooks into `updatePlayer`, `updateGrab`, `fire`, the HUD and the prompt).
- **Gotcha:** `pose()` only replaces NaN joint values, not missing ones. Every pose object must list all ten limb joints; the finishers merge `FIN_REST` in.

---

## 2zv. Update (build 73): walls that line up, and stairs kept clear

**House walls:** a wall with windows or a door in it is built from several pieces. Each piece used to start its siding boards or brick courses from its own corner, so the lines jumped or stopped short beside every window.
- **The fix:** the texture is now taken from where each piece sits in the world (`worldUV`), so clapboard and brick run straight across the whole wall: above, below and beside windows and doors.
- **Where:** every house (`wallRun` in `homeShell`) and tower shells (`towerShell`).

**The Pinewood stairs:** in a two-storey house the STAY LOW neon, the planning board, the back LED strip and the go-bag now stop 0.35 m short of the staircase (`H.room.st.x0`) instead of running into it.

---

## 2zu. Update (build 72): the Pinewood house gets the same treatment

**The Pinewood house:** the house you rent in Pinewood now gets everything the safe house has (`buildSafeDecor(H)`, one set per house in `SAFEDECO.homes`):
- **Inside:** the planning board, the STAY LOW neon, the warm LED strips, the room light, and the go-bag (by the front-door corner, since there's no gun locker there).
- **Outside:** the lanterns, the planters, the mat, the house number and the camera.
- **If the lease ends:** it all goes.

**Also:**
- **The wardrobe** there works upstairs or down (it already did; now tested).
- **Wall placement:** wall pieces now keep clear of open archways (the kitchen arch) as well as doors.

---

## 2zt. Update (build 71): a wardrobe at the safe house, and a safe house that looks like yours

**The wardrobe** (`WARDR`, `openWard`): at the safe house (and your Pinewood house), E at the bedroom wardrobe opens it.
- **The panel:** a boutique-style list of every outfit, each with a little clothes icon in its colours.
- **Trying on:** you turn to face the camera, which drifts slowly as if you're turning at the mirror. Hover (or A/D) to try an outfit on; click or E to wear it; S when you're done.
- **What you can wear:** your own clothes and anything you've bought from the rack outside Masks & Costumes. The rest show greyed out with their price, and you can't leave in something you don't own.
- **Mask:** if you own one, you can put it on or take it off from here.
- **Saving:** what you own and what you're wearing are saved (`sprawl.outfits`, `sprawl.outfitOn`). Buying from the rack adds it to the wardrobe.
- **The mirror:** a long mirror on a stand with a warm light sits beside the wardrobe.

**The safe house, made yours** (`buildSafeDecor`):
- **Inside:**
  - A cork planning board on the living room's back wall, placed clear of doors and furniture: photos of Brenner, Hale, the bank and "Det.?", notes, a pinned map and red string, with a picture light over it.
  - A pink STAY LOW neon on a dark backing.
  - Warm LED strips along the ceiling.
  - A go-bag and some cash by the gun locker.
- **Outside:** iron lanterns either side of the door, two planters, a doormat, a house number, and a small security camera with a red light.

**Lighting fixes, every house:**
- **The indoor light** that follows you used to sit at the centre of the whole house. Since build 66 that point is on an interior wall, and it made a glaring hot spot. It now sits in the middle of the room you're actually in, a little dimmer.
- **Ceiling discs** are a plain fixture now rather than emissive, so they no longer bloom at night.

**Tooling note:** for a while python3 needed the Xcode licence accepted, so this build was patched with node (`p91.mjs`) and served with `serve.mjs`. Python works again.

---

## 2zs. Update (build 70): your papers change hands

The second life is done in person now: you hand your papers to people and sign things (`PAPERS`, `openPapers`).

**The hand-over screen:** someone asks for something; your wallet is laid out as cards (licence, social security card, birth certificate, lease, paycheck, cash).
- **Choosing:** click (or 1–6) what to hand over, then E.
- **Wrong or missing papers:** they tell you what's missing ("I'm sorry, dear, I can't do anything without your driver's licence").
- **Forms:** a form comes up filled in with your new identity; click to sign, then hand it back.
- **Walking away:** S steps back.
- **While it's open:** you can't move. It closes if you're wanted or if you walk off.

**The people:**
- **Mo the forger** slides your licence, social security card and birth certificate across the table.
- **Doris Pruitt** (Pinewood Realty) meets clients at the Pinewood Diner, Monday to Saturday 9 to 6.
  - Choosing a house in the Papers app arranges the meeting.
  - At the diner she wants your licence and the first week plus deposit in cash. Then you sign the lease (property, licence number, term, rent, deposit, the small print) and she hands you your copy and the keys.
- **Hank Doyle** at the General Store counter hires you for your licence, social security card and lease (proof of address). Then you fill in and sign a W-4.
- **Paycheck:** Friday's pay is a check Hank hands you (a check card in your wallet). Cash it at the store: the check plus your licence, endorse the back, and it's cash.
- **Sheriff's deputies** sometimes walk up to you in town (more often when the sheriff's interested): "Driver's licence, please."
  - **Hand it over:** a thank-you, and the sheriff wonders a little less.
  - **Step back:** "I'll remember you", and the sheriff's interest goes up 15.
  - **If your face is on posters:** wearing the same clothes with the sheriff already suspicious, there's a chance he recognises you.

---

## 2zr. Update (build 69): the detective, false evidence and framing, a second life in Pinewood

**The detective** (`DET`):
- **When:** once an open case reaches 25%, a named detective of the Major Crimes Unit takes it (on the news, and the radio).
- **What they do:** they work it in the open, one job at a time, each taking game hours, with a drive between (`detNext`, `detDone`):
  - **The scene:** your prints and camera footage make it count for more.
  - **Each witness:** a good, unmasked description makes it count; pending witnesses get questioned sooner.
  - **Fences you sold to recently** (`DET.sales`).
  - **Your safe house at night** (or your Pinewood house) once they're half sure: sitting in a car across the street.
  - **Paperwork** at the precinct.
- **How close they are** (`DET.sus`, 0 to 100) grows with every lead and pushes the case along. At 100 they get a warrant.
- **In person:** you'll find them there (trench coat, an unmarked car parked near): tail them, watch them. If they get a good look at you, they're closer. They're on the map.
- **The Cases app opens with their file:** what they're doing now, how close they are, their last moves, Show on map, and Pay off.
- **Paying them off:** $3,000 plus $110 for each point of suspicion. 60% of the time it takes 50 off and they look away for 36 hours; otherwise they report it (+25, heat, the news).
- **Killing them:** all open cases jump 15%, 3 stars, and Internal Affairs takes over about 10 hours later. Internal Affairs works faster, starts suspicious, and rarely takes money.

**False evidence:**
- **Evidence kits** (2 for $1,200 at a gun shop). Crouch at an open case's scene and press E:
  - The case drops 20%, they lose 12 points of suspicion, and they spend 3 hours chasing a false lead across town.
  - If anyone sees you do it, it's in the file instead (case +15%, suspicion +20).
- **Framing:** inside someone else's house, crouched, holding a weapon from an open case (`C.weapons`, recorded when the case opens), press E to leave it there.
  - They raid the house on an "anonymous tip", charge a resident (it's on the news), and the case is closed ("Someone else charged").
  - It cuts their suspicion by 45. You lose the weapon.

**A second life in Pinewood** (`COVER`):
- **Mo the forger** works out of an artist's house in the city. $6,000 buys a new identity: a name, date of birth, licence number, social security number and birthplace.
- **The Papers app** (new phone tab) shows:
  - **The wallet:** a driver's licence with your photo, the details and a signature; a social security card; a birth certificate.
  - **Your standing:** how the town sees you, and how much the sheriff wonders about you.
  - **Paperwork:** houses to let; the lease (signed by you and the agent); the job ad and the timesheet; pay stubs with tax lines; the mail.
- **Your house:** rent one of three houses on the edge of Pinewood ($280 to $420 a week plus a deposit). It's yours while you pay:
  - Sleep at the bed: up at 7:00, healed, the heat gone if nobody saw you come in.
  - Stash goods under the wardrobe floor.
- **The job:** stock clerk at Pinewood General Store, $16 an hour, Monday to Friday 9 to 5. Apply at the counter (you need ID and an address).
  - You clock in by being in the store; the clerk greets you by name; late or on time counts.
  - The Papers app can skip to the end of a shift.
  - A missed shift gets a letter; three and you're fired.
  - Friday 5 pm you're paid, with a pay stub in the mail.
- **Rent** comes out on Mondays. Miss it and you get a letter; miss two and you get a notice to quit.
- **The town:** with good standing, people in town greet you by your new name. The mail brings letters from the agent, the store owner and the sheriff.
- **The sheriff** (`COVER.sheriff`):
  - **What raises it:** crimes in the county with your face showing, and your face on posters.
  - **What lowers it:** good standing.
  - **On the way up:** at 50, Hank at the store warns you the sheriff was asking about you. At 80, a community notice.
  - **At 100:** a search while you're away. If the stash is there (65% chance they find it), the cover is blown: the papers are burned, the house and job are gone, your alias is wanted and it's on the news. If not, nothing's found and things calm down.
- **Saving:** the cover is saved between sessions.

---

## 2zq. Update (build 68): turning sensors off, lock and safe minigames, stakeouts, four fences with bases, wanted posters

**Turning motion sensors off:**
- **Sensor jammer:** $20,000 at a gun shop (`P.tools.jammer`).
  - **Using it:** look at a live sensor from 2 to 14 m away (outside its reach) and press E. It's off till 7:30 next morning.
  - **Wear:** each use costs 4 to 8%, and the chance it works follows its condition (never below 30%). A glitch sets the light off and counts as a noise.
  - **Servicing:** $2,500 at a gun shop puts it back to 100%.
- **Cutting the power:**
  - **The meter:** every house has an electricity meter on the side wall without the garage (`H.meter`). Hold E there for 2.6 s and the power's off till 7:30: lights and motion sensors die, but the alarm keeps its battery.
  - **If they're awake:** 70% of the time someone comes out 10 to 25 s later to check the meter. If they see you, you've been noticed; otherwise they switch it back on and are suspicious.
  - **If they're asleep:** a 15% chance it wakes them.

**Minigames** (`MG`, `openMG`):
- **Lock-picking:** a locked front door now opens a lock with 4 pins. A needle sweeps a bar; press E or click while it's in the gold.
  - Each set pin narrows the gold and speeds the needle.
  - A miss is a scrape: a little noise to a sleeping house. Four misses and the pick snaps.
- **Safe-cracking:** a dial (A/D to turn, Shift for fast).
  - The LISTEN meter fills as you near the number, and it clicks when you're on it. Press E to set it; three numbers open the safe.
  - A wrong number makes a clunk and a little noise, and every second wrong one resets the dial.
  - The combination stays with that safe.
- **Stopping:** S stops either one.

**Real routines and stakeouts:**
- **Each house has its own routine** (`houseSched`, `schedMode`): wake time, work hours (or none), bed time, a weekend lie-in and outing, a Saturday night out, Friday nights. Seeded from the house, so it holds day to day (give or take 15 minutes). `routineMode` now uses it.
- **The street follows it** (`updateStreetLife`): near you, as the hour changes, people walk out of their front doors to the street, come home and go in, and the lights go out.
- **The stakeout** (`stakeOn`, `updateStakeout`):
  - **Starting it:** park, and after 5 s still the engine switches itself off (W or S starts it; the phone has a button too). Engine off, it's a stakeout.
  - **What it logs:** every front door in view within 48 m (`SO.book`). Two comings or goings, or 3 hours watching, and the house's routine is known.
- **The Stakeout phone app:**
  - **Status:** what you're watching, how many doors are in view, and Wait an hour / Wait 3 hours buttons (the time passes and the app writes down what happens).
  - **One card per house:** a weekday and a weekend 24-hour timeline (home, out, asleep), the routine in words, the next window when it's empty or asleep, the latest events, and "Show on the map".

**Fences, each in their own place** (`FENCES`):
- **Sal:** a house a few blocks from the chop shop. Takes anything, a bit more for electronics.
- **Vera "the Countess":** a house in Northgate. Art ×1.6, silver ×1.35, watches ×1.3; electronics at under half.
- **Lenny Two-Bags:** a house out on the country roads. Electronics ×1.4 to 1.5, booze and groceries more too; art at half.
- **Dutch:** a house by the water in Havenport. Gold, jewellery and parcels at about ×1.3, and full price for hot goods.
- **How it works:** each sits on their sofa with the door unlocked. Each is on the map and in the phone's Intel app, and the sale prompt says what they like. Sal no longer stands in the road.

**Your face on posters** (`FACE`):
- **When:** once an open case has your face on camera, or an unmasked witness has picked you out, the news runs it and wanted posters go up on the lamp posts round you.
- **Recognition:** bystanders within 6.5 m who look at you may recognise you and call it in (about 3.5% a second each, then 25 s before it can happen again).
- **Avoiding it:** a mask, or a change of clothes from the costume shop rack. When the case closes, the posters come down.

---

## 2zp. Update (build 67): a calendar, motion sensors and a scanner, neighbours, hiding, the county sheriff, country roadblocks

**A calendar people live by:**
- **The date:** it starts on Saturday 21 November and every midnight is a new day (`TRACK.day`). The HUD shows it beside the time ("SAT 21 NOV · 23:01"), and a note says what kind of day it is when it changes.
- **Who's home** (`routineMode`, replacing the old night/day coin flip in `homeMode`):
  - **Weekdays:** asleep until about 6:30, mostly out at work from 8 to 5, home in the evening, asleep by 11. Friday nights more people are out.
  - **Weekends:** people sleep in until about 9:30 and stay home a lot. Saturday night half the street is out.
  - **By theme:** the elderly are home all day and in bed by 9; gamers stay up late.
- **The phone:** Intel opens with a "Today" card that says what that means for a break-in right now.

**Motion-sensor lights** (`H.sensors`):
- **Where:** over the front door of about 60% of alarmed houses (18% of the rest), and on the back wall of a few.
- **What happens:** at night, stepping into the zone (a 7.5 m half-circle) lights the porch and lights you up.
  - Passers-by may spot you, and it counts as a noise for the neighbours.
  - In a sleeping house it can wake someone (30%); in a house where people are up, it makes them suspicious.
- **The sensor scanner** ($400 at any gun shop, Explosives & gear) shows every zone near you as red on the ground.

**Neighbours** (`neighbourNoise`, `NB`):
- **When they come:** a noise (a window smashed, a door kicked in, an alarm, gunshots indoors, a house woken, a porch light) has about a 10% chance of bringing one out. Every recent noise nearby adds roughly 16% more.
- **Who comes:** someone from a house with a view of it. They walk over, look about for about 14 seconds and go back in.
- **If they see you** masked, armed, carrying a body, wanted, in someone's house, or standing where the noise came from, they call the police.
- **Gunshots indoors:** these now mostly bring a neighbour to look; only 12% go straight to a 911 call.

**Hiding** (`H.hides`, `hideNear`, `enterHide`, `exitHide`):
- **Where:**
  - **A wardrobe:** E. You watch through the slats.
  - **Under a bed:** crouch, then E. You see along the floor.
- **While you're hidden:**
  - Nobody can see you: police lose you (the search clock runs), residents' suspicion stops, and the sneak indicator says HIDDEN.
  - You can't move or shoot; the mouse looks about.
- **Being found:** a police officer, or a suspicious resident, who stands right at your spot for a couple of seconds may check it and find you.
- **Holding a door shut:** hold E at a closed interior door. Whoever's on the other side pushes and shouts, then forces it: a police officer after about 3 s, a tough resident after 4.5 s, anyone else after 7 s. The door flies in and knocks you back.

**The county sheriff** (`COPB.sheriff`): Pinewood, Cedar Falls, Snowcrest and Westbrook.
- **Cars:** white, with dark green COUNTY SHERIFF lettering and a gold stripe.
- **Deputies:** tan shirts, olive trousers, a brown wide-brimmed hat, a gold star, SHERIFF on the back.

**Roadblocks in the country** (`countryRoadblock`): at 2 stars or more, driving fast on the highway or a country road, the police set two cars across the road 230 to 300 m ahead, with an officer behind each. From 3 stars there's a spike strip in front. They're from whichever force's ground it is: Highway Patrol or the sheriff.

---

## 2zo. Update (build 66): houses with rooms, people asleep in bed, three police forces, roadside houses, lit windows

**Houses with real rooms** (every house except the mayor's mansion; all 1,862 in the city, Havenport and along the country roads):
- **The plan** (`homePlan`, run inside `homeShell`):
  - **One storey:** an open living room and kitchen at the front. Across the back are a bedroom, a bathroom and a second bedroom (a study as well in the big ones), each behind its own door.
  - **Two storeys:** downstairs is a living room, a kitchen through an archway and a toilet. Upstairs, a hall runs beside the stairwell: two bedrooms off it (four, off a second hall, in big houses) and a narrow bathroom in front of the stairs.
- **Windows:** placed per room from the plan (one or two per outside wall a room touches; small high ones for bathrooms), so no wall lands across a window. The open back window you climb in through is in the master bedroom.
- **Furniture** (`furnish2`): each piece goes against a wall of its room, clear of every doorway's swing, the front door, the stairs and the climb-in window.
  - **Living room:** sofa, TV, coffee table, rug, armchair, shelves.
  - **Kitchen:** a run of units with a fridge (an island if nowhere else fits), and a dining table.
  - **Bedroom:** a bed with its head to a wall, nightstands and lamps, a wardrobe, a dresser.
  - **Bathroom:** tub or shower, toilet, sink and mirror.
  - **Each theme adds its own:** the rich get a piano, art and a safe; gamers an RGB desk with a PC; artists easels; the elderly a grandfather clock; bachelors a bar and a stash in the sofa. Loot sits where it belongs.
- **Interior doors** (`IDOORS`, one instanced mesh per 176 m tile):
  - A shut door is a wall: it blocks movement and line of sight.
  - Walk into one and you push it open, with a hand on it (slow and silent if you're crouched). E closes it again; the prompt says "Close the door" or "Open the door".
  - Residents open doors as they reach them.
  - At night the bedroom and bathroom doors are shut.
- **Getting around inside** (`homeWay`): a 20 cm walkable grid per floor (walls and furniture blocked, with clearance), A* with string-pulling. Shut doors count as open, since people open them as they arrive. This replaces the old single partition doorway.
- **Upstairs:** the walls bound the camera as well as you (`L.walls`), so it no longer sits inside them.

**Asleep means in bed:**
- **Where they sleep:** an asleep house has its people lying in their beds (`spawnSleepers`, `H.beds`): couples share the double bed, kids are in theirs. You can see them, and they don't count as witnesses.
- **Noise** (`sleepK`) is what wakes them:
  - **Loud:** right beside the bed.
  - **Less:** in the same room.
  - **Much less:** through a shut bedroom door.
- **Waking:** they climb out of bed over about a second and come at you. If you're downstairs, the ones upstairs come down the stairs after a few seconds.
- **Victor Hale** sleeps in his bed too.

**Life at home:**
- **Sitting:** residents sit on the sofa, in the armchair and at the dining table (`H.seats`, `homeLife`). They get up when something's wrong, or now and then to potter about.
- **Lights at night** (`updateHomeGlow`): windows glow where people are up, go dark where they're asleep or out, and come on when you wake a house. Far houses follow the hour.

**Fixes:**
- **Crouching indoors:** crouch-walking used to keep snapping you into wall cover (door frames, walls, furniture) and dragging you sideways. Cover now only engages when you press crouch beside something, and never indoors.
- **Bodies out of house windows:**
  - **Upstairs:** a thrown body used to drop through the floor into the room below. Now it smashes the window it's flying at and falls outside (with fall damage). Against a solid wall it bounces back in.
  - **Downstairs:** a body thrown hard at a window now crashes through onto the lawn.
- **The phone:** it rebuilt itself every second, and smooth scrolling made the list jump, and could eat a click. Now only the parts that changed are redrawn, the scroll position holds, and the Jobs app's extra sections don't duplicate.
- **Witnesses** go in for questioning 5 to 9 hours after a case opens (it was 3 to 10).
- **Prompts:** no "Bus stop" prompt from inside someone's house.

**Three police forces, each marked** (`COPB`, `copBranch`):
- **Sprawl City PD:** the city, island, bridge and airport. White cars lettered SPRAWL CITY POLICE; navy uniforms with POLICE on the back.
- **Havenport PD:** in and around Havenport. Navy cars lettered HAVENPORT POLICE; light-blue shirts with HAVENPORT PD on the back.
- **Highway Patrol:** everywhere else. Black cars with gold HIGHWAY PATROL lettering, interceptors more often; khaki uniforms, a campaign hat, STATE TROOPER on the back.
- **On screen:** the nearest force after you is named under the stars (SWAT and the army too). The radio speaks as that force's dispatch and announces when a chase crosses into another force's ground.

**More country:**
- **Roadside houses** (`RSITES`, `roadsideHomes`): about 28 along the Havenport Road, North Pass, Coast Road and the new roads. Each is on a levelled pad at road height, with a lawn, a front path, a drive (or a garage), a mailbox and a car out front. They're lived in, burglable and on the map.
- **Three new roads:**
  - **Valley Road** (`VALLEY_RD`): from the highway west of Pinewood south past Pine Lake to the Coast Road.
  - **Mirror Lake Road** (`LAKE_RD`): from the highway north round Mirror Lake to the North Pass.
  - **Kessler Back Road** (`BACK_RD`): from the Coast Road up the west side of Fort Kessler to the Havenport Road.
  - All three are graded to 13% or less, with valleys carved, names on screen and traffic.
- **Less square:** houses always get a pitched roof (gable, front gable or hip, no flat boxes), and hedges are rounded.

---

## 2zn. Update (build 65): cars stay out of buildings, roofs you can step off, a parachute on your hands, real town edges, more roads

**Fixes:**
- **Cars and buildings:** a car can't drive into a room (shops, bars, the airport terminal, homes). The car wrapper (`carCollideWorld`) puts it back where it was. A car that starts inside one can still drive out.
- **The metro:** no car exists past x = 4000, where the metro platforms are. Police cars and taxis used to follow you down.
- **Rooftops:** walking off a roof edge used to land you straight back on the same roof every frame (the shaking). The fall now ignores that roof for 1.2 s (`leaveT`, `fromY`), so you fall, or open the parachute.
- **Parachute:** the canopy group's pivot is at your hands (1.45 m), not the canopy. Banking and the opening animation swing it about the risers, so the lines stay in your hands.
- **Havenport road traffic** could pick a car type that doesn't exist ("hatch") and crash the update. Fixed.

**Town shapes:**
- **Sprawl City:**
  - The land (west) side now has a countryside fringe (`WILDA`, `wildDepth`, `wildInit`): up to 9 blocks deep at the corners, none where the highway comes in.
  - Those blocks are meadow, trees and the odd hedge, with no pavement, buildings or people. Their streets are closed through `NODE_OK` and `EDGE_OFF`, so traffic, the road mesh and the map all follow.
  - Hospitals, shops, bars, parks, promenades and other special blocks are always kept.
  - The map shows the fringe in green.
- **Havenport:** a rounded, irregular outline on its outer two rings (`havenKeep`). The quay is still straight, the road ends are always built, and the cut lots are grass and trees. Streets are drawn only where a block sits beside them, and the traffic loops moved in to rings 2 to 12.

**More roads:**
- **North Pass Road** (`NPASS`): from Havenport's north edge, east south of Mirror Lake, to Snowcrest.
- **Coast Road** (`SCOAST`): from Havenport's south edge, along the south past Pine Lake, to the Cedar Falls road.
- **Both:**
  - Graded to 13% or less (just over 20% for a short stretch into Snowcrest).
  - Each has a valley carved along it (`VALLEYS`, which now include Havenport Road).
  - Named on the HUD, with up to 4 cars each. In open country they spawn far down the road, since nothing's hidden.
- **Havenport Road** is now graded all the way into town; the old end smoothing was making it steep.

**Known:** the main city's building layout changed with the fringe (the shared random sequence shifts). Special places are where they were.

---

## 2zm. Update (build 64): Havenport, weather, respray, outfits, a lawyer, races, property, and fixes

**Havenport** (a second city, past Fort Kessler):
- **Where:** a harbour city on the west coast, beyond the Kessler Range. It's 14 × 14 blocks (616 m), smaller than Sprawl City but much bigger than Cedar Falls or Pinewood.
- **Terrain:** the mountain heightmap now starts at x = −4804 (1,404 m further west, a whole number of 6 m cells, so existing heights don't move). The city sits on a level plain at 4 m (`HAVEN`), with a 420 m blend into the hills and a bay cut to the west.
- **Getting there:** Havenport Road (`HAVEN_ROAD`) leaves the Kessler Highway at (−1960, 250), runs round the north side of the base, and comes down a valley graded at 13% or less into Main Street.
- **What's in it:**
  - Built with the main city's lot generators: a downtown of towers, commercial blocks with storefronts, walk-in homes (about 377), an industrial strip by the water, and five parks.
  - Two bars (The Lighthouse, Salt & Rye) and three shops, each with a clerk.
  - A sea wall and promenade rail on the waterfront.
  - Street names, centre lines, zebra crossings downtown, lamps and trees, and a welcome sign.
- **Generation:** it's built after everything else on its own seed (`_seed` is saved and restored), so nothing else in the world moves.
- **Life:**
  - Up to 34 people walking the pavement loops, more downtown and fewer at night.
  - About 14 cars on six street loops.
  - Local police cars when you're wanted, and a few cars on Havenport Road.
- **On the map** it's under "Out of town".
- **Draw cost:** building chunks past the fog aren't drawn (`cullChunks`), and static scenery groups past the fog move to an undrawn layer (`farCull`). From Havenport, the worst view went from 2,244 draw calls and 11.5M triangles to 936 and 4.0M. This helps the main city too.

**Fixes:**
- **Arrests:** the cuff timer drains again. A build 63 comment had swallowed the `else`, so "Being cuffed" stuck on screen and later touches busted you almost at once.
- **Struggling** is Space only. It no longer jumps or fires.
- **Rallies and VIPs were empty:** the 125 m pedestrian despawn deleted them right after they were built (events build at 230 m). Events, targets, guards and bar crowds now keep their own range (420 m), and the night thinning and people heading home leave them alone.
- **Contract pins** follow the target's real day. Brenner: rally, City Hall, the SUV, the bar, home. Hale: home, errands, his plane. They used to always show the house.
- **The army:**
  - Only a jet you've just stolen calls it, not getting back into your own.
  - The rampage kill count resets when you die or get busted.
  - Tanks chase you in a plane too.
- **Car AI:** unknown car AI modes fell through to the police driver, so the build 63 tank was driven twice. The tank and race cars now run only their own code, and the 200 m car despawn leaves race cars and army vehicles alone.
- **People going home** wait at the door until you look away.
- **Bar crowds** stand on the pavement out front (they were inside the bar), each spawns out of sight, and they stay until closing.
- **One star outside the city** still sends an officer.
- **The new lamp** in homes no longer glows in daytime.
- **Spike strips** only go on the road you're on, and not under a civilian.

**Improvements:**
- **Notices queue:** each stays up at least 1.5 s.
- **F3** shows fps, frame time, draw calls, triangles, people, vehicles and weather.
- **Search timer:** a countdown under the stars, with "leave the circle" while you're inside the search area.
- **The army stands down** if you stay unseen for about 75 s (it drops to 4 stars), with a news item.
- **Shop robberies** pay about two-thirds of what they did.
- **Drunk people** sway and say things.

**New:**
- **Weather:** clear, overcast, rain or fog, with fog mostly in the mornings.
  - Rain is one 1,800-line mesh, and the wet street look only updates when wetness changes.
  - Rain and fog cut how far the police see you.
  - Wet roads make cars slide (lower grip).
- **Respray:** stop at any gas station in a car and press E ($450). The car gets a new colour. If the police can't see you, they lose you, and they're looking for the old car.
- **Outfits:** the rack at the back left of the costume shop ($220 each, eight looks). Changing while unseen throws off their description of you.
- **Lawyer:** Benny Marsh, in the phone's Jobs app. $1,500 per star (plus $2,000 at 3+) removes one star if you're unseen. Not at 5 stars or with the army. Four-minute cooldown.
- **Police radio:** dispatch lines at the top of the screen with your car's colour and model, heading and street, plus "we've lost visual".
- **Drinks:** E at any bartender, $15. You get drunk (a wobble and a warm haze). After a few, someone may pick a fight.
- **Hostages:** while you hold someone, patrol officers hold fire unless you shoot. SWAT and soldiers don't.
- **Street races:** a meet on the map, 8 pm to 4 am. Pull up, press E, $500 buy-in, two laps round a block loop against three cars. First wins $2,000, second gets the buy-in back.
- **Your record:** in the Jobs app. Most stars, longest chase, biggest score, money made and spent, kills, busted and wasted, km driven, races, drinks, army calls.
- **Property:** two houses ($18k and $26k) and three businesses (two bars and a shop, $22k to $42k), bought in the Jobs app when you're within 40 m. Houses: E at the door to sleep until 8:00, which heals you and clears unseen heat. Businesses pay $420 to $900 a day.
- **More VIPs:** Judge Harlan Pike, Marco "Mint" Delgado, Kxng Rello and Ava Sterling. **More rallies:** Chief Rourke and Pastor Gideon.

**Known:**
- House positions in the main city vary slightly between loads. This was already true in build 63: some early world generation mixes `Math.random` into the seeded sequence.
- Havenport has no traffic lights and its cars don't turn at junctions. They drive fixed loops.
- The FPS budget wasn't measured on your machine. Use F3.

---

## 2zl. Update (build 63): the police ladder, search and memory, the arrest, the army, the night, rooms

**Search.** Breaking line of sight starts a search: the existing sweep of where they lost you, plus the helicopter's searchlight.
- Stars only go once you've stayed out of sight for 38 + 10 × stars seconds outside the search area (48 s at 1★, 88 s at 5★). Inside the search area it's at 45% speed; hiding indoors or in cover outside it, 125% speed.
- Then all stars go at once: "You lost them." Before this, 2★ was gone in about 15 s; now it takes about 58 s outside the search area.

**Memory (`PURSUIT`).** The police remember the car they last saw you in and whether you had a mask on.
- In that car, they spot you from 1.25 × the normal distance.
- In a different car: 0.45 × once they've seen you in another car, 0.8 × if they never saw a car.
- On foot with the mask toggled since: 0.55 ×.
- Switch cars while unseen and you're told which car they're hunting.

**The ladder.**

| Stars | Response |
|---|---|
| 1★ | One officer on foot (`footOfficer`), no cars |
| 2★ | Patrol cars, and roadblocks ahead when you're driving fast (was 3★) |
| 3★ | Spike strips across the road about 80 m ahead every 20–30 s when you're driving fast (`spikesAhead`), and the helicopter (was 4★; still 60 s between helicopters) |
| 4★ | One SWAT van |
| 5★ | Two SWAT vans, two patrol cars, and the SWAT helicopter |
| 6★ | The army (`MIL`), with a sixth olive star on the HUD |

- Officer cap per level: 0/2/4/6/10/15.
- The army comes after 25 kills within 3 minutes at 5★, or when you take a military jet or attack helicopter.
  - The news announces the National Guard.
  - Army trucks (an olive armored truck) arrive every 18 s, up to 3, each dropping four soldiers in olive with rifles and 180 hp.
  - After 25 s, a tank (`milTank`) hunts you down the streets and fires when it has a clear shot.
- The army goes home when you drop below 5★ or die.
- Tested: 2 trucks and 4 soldiers plus a SWAT van and the helicopter killed a test character standing in the open within about 25 s.

**Arrest.** At 1–2★, being grabbed now takes 3.2 s of cuffing (was 1.8 s) with an on-screen "Being cuffed N%" prompt. Mash jump (or kick, shove, click) to struggle: five struggles that push the cuffing back to near zero break you free. The officers are thrown off and knocked down, and you get +1 star for resisting.

**Money.** Heist estimates are 60% of what they were, and Sal pays 60% of the bag value × the bonuses.

**The night.**
- 145 pedestrians (was 175). Night density is lower: 0.10 before 5:00 (was 0.16), 0.20 after 21:30 (was 0.32).
- Street crime happens 2.5× as often at night.
- After 22:00, a couple of walkers at a time head for the nearest front door within 55 m and go in (`goHome`).
- From 6:00 to 9:30, 40% of residential spawns come out of a front door.
- From 21:00 to 3:00, bars get a crowd out front, up to 7 at a time in groups: chatting, smoking, about 40% drunk. They leave when it's day or you're over 140 m away.
- Tested at 23:00: 9 people outside Neon Lounge, 32 pedestrians in total.

**Rooms.** The room light is brighter (intensity 15, was 9). Every house gets `homeDecor`:
- a rug, pictures on the back-room wall and in the back room, a pendant light over the front room, and a potted plant by the door;
- colours come from the house's position, not the world-generation random numbers, so the city layout doesn't change;
- all of it is merged into the existing building chunks, so no extra draw calls.

---

## 2zk. Update (build 62): mantling, sealed rooms, getting into cars, helicopter spacing, playtest

**Mantle and climb.**
- Jump now looks for something to get over in a fan of directions (where you're moving, facing and looking; ±0.3 and ±0.6 rad), not just straight ahead. A climb reaches 1.5 m (was 1.1).
- Climbing tall fences and walls (up to about 2.5 m) has a real motion (`updateVault`, `poseMantle`): reach up and pull to the top, swing your legs over, then drop down the far side.
- Low obstacles get a one-hand speed vault with the legs swinging through.
- Tested: 10/10 vaults over low fences approached at a 26° angle; 7/8 climbs over tall thin walls.

**Police helicopter.** The next one waits 60 s after the last is shot down or leaves (`HELIWAIT`).

**Sealed rooms (the real bug).** Build 51's `homeRooms` bedroom walls landed on top of the existing back-room partition from `homeShell`. That left a 0.7 m strip between two walls, and the 0.9 m bedroom doorway barely fit a 0.42 m-radius person. The bedroom walls are now off. The back room, with its 1.3 m doorway, is the second room. Tested: walked into the back room in 12/12 houses.

**Getting into cars.** You always went to the driver's door, so from the passenger side you walked into the car and gave up after 3.5 s. Now you use the nearer door. Once you're within 1.9 m and have been trying for 0.6 s, you get in. Tested: 8/8 parked cars, from both sides.

**Draw distances.**
- Cars: details hidden beyond 70 m (was 90), shadows only within 45 m (was 90), not drawn beyond 240 m (was 300).
- Characters: full detail out to 48 m for pedestrians and 56 m for others (was 64/70).
- A fresh scene went from about 1,300–1,600 draw calls to about 950.

**Playtest notes (build 62):**
- No console errors across vaulting, house rooms, the shooting → witness → police → arrest loop, stealing and driving a car, map, phone tabs, all heist plans, every contract, jobs, armored truck stop, the armory, and 4 street-crime events.
- Police lose you very quickly. Out of sight, 2 stars went to 0 in 15 s with the car crashed and standing still. That's the biggest problem with how the game feels; see the review in the chat.
- Frame-rate numbers in the test browser aren't reliable (the pane was hidden and throttled). JS per frame is about 12–15 ms; the rest is GPU (shadows, ambient occlusion, about 5 million triangles).

---

## 2zj. Update (build 61): indoor camera, roomier houses, phone with the mouse, free aim, the helicopter, a clean slate

**Indoor camera (`indoorBox`).** Inside a house, shop, bar or tower floor, the camera now:
- moves over your shoulder (0.42 m), with a wider lens (+10°, or +4° while aiming);
- uses the room's own walls as the limit for the boom (`rayRectExit`). On tower floors it used to ignore walls entirely and clip through them: that was the "glitching";
- when squeezed against a wall, rises toward the ceiling and tilts up to 0.32 rad down, so you look over your head into the room rather than at your back;
- hides your head if it gets within 0.8 m.

**Roomier houses.** Footprints are +0.3 m wider and +1.2 m deeper, and single-storey ceilings are 3.7 m (were 3.3).
- A typical room is now about 9.9 × 8.7 m (was 8.8 × 7.7).
- I checked about 1,700 homes: no two sets of walls touch.
- The front door does open from inside. The real problem was that you couldn't see it past your own back.

**Phone.**
- Opening it frees the mouse without pausing the game (`pointerlockchange` ignores it while the phone is open). Clicking the game doesn't recapture the mouse until the phone is put away.
- The mouse wheel scrolls the phone, not your weapons. The phone also stops wheel events from reaching the game, and the wheel never changes weapons while the phone or map is open.
- The keyboard highlight only shows (and only scrolls into view) once you use the keys. It used to snap the scroll back every second.
- Restyled: a bigger phone, a gradient screen, hover states on cards and buttons, a highlighted active tab.

**Free aim.** On foot you can look 69° up (was 29°), and your arms follow up to 1.1 rad. Missed shots and bullet holes can now be up to 220 m high (was capped at 14 m).

**The police helicopter.**
- Shot down, it drifts as it falls, and if it's over a building it crashes onto the roof instead of falling through to the street (`heliRoof`).
- The crash also:
  - does 480 damage to buildings within 12 m (a small building collapsed in testing; big towers only scorch, as before);
  - damages cars within 14 m and sets most of them on fire;
  - leaves 5 fires for 14–24 s that burn anyone standing in them;
  - sends people running.

**Dead is dead.** When you die, your record resets: kills, cops, VIPs, robberies, sprees, the warrant, cases and pending witnesses all clear, city tension drops by 70%, and the city alert ends.

**Fewer witnesses.** At most 2 witnesses can be waiting to talk across all cases. A lone killing has a 50% chance per eligible witness of anyone coming forward.

---

## 2zi. Update (build 60): frame rate, witnesses, warrants, the press

**Frame rate.** I profiled it (temporary per-function timers, plus `renderer.info` draw calls):
- The game update is about 4.5 ms per frame. Everything added in builds 57–59 (cases, witnesses, heists, cover, street crime, hit reactions) totals under 0.05 ms.
- The real cost was the seated figures from build 56: each one was a full character of 24 meshes. In traffic that added about 575 draw calls per frame (1,504 vs 929).
- Now every seated figure (car occupants and bus riders) is baked into one mesh with vertex colours (`bakeGeo`, `PUP_MAT`). A patterned shirt uses its texture's average colour.
- When someone dies in their seat, the rig is re-posed and re-baked (`posePup`). Wounds sit on the baked mesh at the stored head and chest positions (`headP` / `torsoP`).
- Budget: figures are created within 36 m and shown within 46 m, at most 12 cars at a time. Bus riders are created within 38 m. Geometry is freed when a car or bus goes away (`PUPS`, checked every 3 s).
- Result: 10 visible figures cost about 6 draw calls in total.

**Witnesses (`pickWitnesses`).** A case gets at most 1 witness, or 2 for a massacre (3 or more dead). For a single killing there's often nobody willing to talk at all.
- Each witness is due in for police questioning 3–10 in-game hours after the case opens (`gt()` is in-game hours).
- The phone (Cases) and the map (W) show who they are, where they are (out and about, or at home), and when they're due.
- If a witness despawns, they're "at home". Within 90 m of their home they come back into the world, out of sight, so you can find them.
- Kill a witness before questioning and they're silenced. Once questioned, they add 42 progress, or 14 if you were masked.
- Other evidence also lands in in-game hours: camera footage after 1–3 h, prints after 2–5 h, weapon details after 1–2 h, a car noted after 2–4 h.
- Case evidence and the case update are checked once a second. New bodies come from a pending list (`CASES.pend`), not a scan of every character.

**Warrants (`WARRANT`).** At 100% progress you get a warrant for 48 in-game hours; you get no stars just for that. Then:
- A cop who sees your bare face within about 26 m has a 40% chance each second to move in (1 star).
- A passer-by who recognises you within 10 m has a 5% chance each second to phone it in.
- Stay near your safe house or cabin for 25 s and the police raid it once a day: 2 stars and three officers.
- Being busted serves the warrant.

**The press (`PRESS.tension`).** Each incident raises the city's tension, and it calms by about 4 points per in-game day. A headline's tone follows how tense the city already was:
1. An appeal for information.
2. Possible links to earlier killings, with the suspect's profile.
3. The commissioner orders more patrols, or the mayor holds a press conference.
4. A Major Crimes task force, with tactical units on standby.
5. A public safety emergency.

Stories are credited to outlets: The Sprawl Herald, Channel 6 News, SNN, The Sprawl Times, KSPR News Radio, Metro Wire. Single-body stories have new wording too. The city alert (drastic measures) only comes at tension 16 or more, at most once per in-game day.

---

## 2zh. Update (build 59): heists

**The board** is in the phone's Contracts app, under "Heists" (`heistBoard`). You can plan one heist at a time (`planHeist`); calling it off is free. Each heist has a prep checklist, a quiet/loud switch, and an expected cut.

| Heist | Base take |
|---|---|
| First Sprawl Bank | about $15k |
| Diamond District | about $6k |
| Armored truck | about $4k (loud only) |
| Northgate mansion safe | about $8k |

**Prep.** Each item done adds 10% to the cut:
- **Scout it.** Bank or jeweller: 8 s inside during opening hours with your gun away (the bank uses the old `CASE.scouted`). Truck: 15 s within 35 m. Mansion: 10 s within 40 m at night.
- **Tools.** Bank: thermite or the manager's keycard. Jeweller: a glass cutter. Mansion: a stethoscope or thermite. Truck: any gun with ammo.
- **Kill the power.** Hold E for 3 s at a grey box on the side wall, after dark. The bank's is the old alarm box. The jeweller's and the mansion's are new (`HPROPS.boxes`); the mansion's also turns off the house alarm (`H.alarmOff`). With the power cut, the robbery case has no camera evidence.
- **Getaway car.** Park any car at the marked spot (G on the map; `getawaySpot`, 110–280 m from the target). Getting into it during the escape while no officer can see you takes 1 star off.

**Quiet or loud.** A quiet job with no alarm pays 35% more; if an alarm trips, it goes loud (`heistAlarm`).
- Bank: tellers or the guard still on their feet hit the panic button about 2.5 s after the thermite starts.
- Jeweller: the cutter is silent only once the clerk and guard are down, held up or knocked out.
- Mansion: thermite sets off the house alarm unless the power is cut.
- Truck: always loud.

**New tools: the "Heist gear" tab at the gun shops.**
- Thermite ×2 ($900): FRONTIER ARMORY, BULLSEYE TACTICAL. It replaces the drill at the vault: 14 s, no drill noise (`startThermite`).
- Glass cutter ($400): AMMO & ARMS, BULLSEYE TACTICAL.
- Stethoscope ($350): LOCK, STOCK & BARREL, BULLSEYE TACTICAL. It cracks the mansion safe in 18 s of holding E; let go and the progress slowly drains. Thermite cracks it in 8 s.

**Loot bags (`HB`).** During a planned heist, loot goes into duffel bags (`addLoot`) instead of your pocket:
- A bank bag holds two carts; the jeweller's haul fits in one bag.
- You carry at most two bags: one on your back, one in your hand. One bag slows you 16%, two slow you 34%. Extra bags drop on the floor and show on the map.
- The truck's cash comes out as bags (`dropPickup` is captured while the truck opens).
- Getting into a car moves your bags into it.
- Drive or walk them to Sal (`fenceSpot`) with no stars to get paid (`payout`): bag value x the prep bonus x the quiet bonus. Being busted or killed loses the bags.

**The police case.** A paid heist opens a Robbery case in the Cases app (`openHeistCase`). Evidence:
- camera footage (none if the power was cut; weaker if you were masked);
- prints, if you had no gloves;
- witnesses who saw you when it started;
- a car noted near the scene, unless you used the getaway car.

A quiet job is discovered 90 s later. The target cools down for 25 minutes.

**Tested:**
- Jeweller, quiet with the cutter and the staff knocked out: all 8 cases opened with no alarm into one $5,703 bag, paid as $10,009 (3 preps, quiet).
- Mansion safe opened with the stethoscope (it's placed along the first clear wall).
- Bank thermite opened the vault with no drill.

---

## 2zg. Update (build 58): the case file, worn gloves, hit reactions, cover, aim settings, city hours, street crime

**Case file (phone → Cases, key 5).** Every kill you make is recorded at the moment it happens (`recordKill`): mask on or off, gloves, weapon, whether you were in a car, whether it was indoors, your top's colour, and up to 4 people who saw it (`seenBy`: facing you with a clear line, close by, or near a loud shot).
- When the body is found, a case opens (`openCase`). Kills within 90 m and 5 minutes of each other share one case.
- Evidence lands over time (`updateCases`), and the bar shows how close the detectives are:

  | Evidence | When it lands | Weight |
  |---|---|---|
  | Prints (no gloves) | after 50–90 s | 55 |
  | Security camera (indoors) | | 40, or 12 if masked |
  | Weapon / ballistics | | 5 |
  | A witness noting your car | | 12 |
  | Each witness statement | after 70–150 s | 32, or 12 if masked ("a masked figure in a blue top") |

- A witness you kill before they talk is "silenced". One who wanders out of range has gone to the police.
- At 100%, an arrest warrant is issued (2 stars) and it makes the news. A case with nothing new for 10 minutes goes cold. Bodies nobody finds open no case.
- The case file took over the old prints-match news (`forensicDone`).

**Gloves wear out.** Wearing them uses up about 16 minutes. Hauling a body wears them 3x faster, and each melee hit takes 1.5%. You get a warning at 75%; at 100% they tear and you're bare-handed. A new pair resets the wear, and the utility panel shows how much is left.

**Aim settings.**
- "Forgiving aim" (on by default) is the old behaviour. Turned off, it's precise free aim: the hit area is 0.3 m instead of 0.45 m, a shot more than 8 cm over the head or below the feet misses, and the crosshair's target area shrinks to match.
- Lock-on remains its own toggle.
- Bystanders only react to your gun (`noticesAim`) if they're within 4 m, or facing you with a clear line: up to 15 m, or 24 m if they're looking right at you. Anyone else carries on.

**Hit reactions (`hitReact` / `poseHits`).** Every bullet hit plays a 0.42 s additive reaction:
- The body leans away from the shot.
- A head hit snaps the head back.
- An arm hit spins them by the shoulder.
- A leg hit buckles the knee.
- They're pushed back along the shot; a close shotgun blast or a sniper round knocks them off their feet.
- Your hits get a short hit-pause.
- The old drop-the-gun and fall-on-a-leg-hit effects are unchanged.

**Snap to cover (settings toggle, on by default).** Crouch within 1.9 m of a wall or car, or walk into one while crouched, and you stick to it (`findWallCover`; the surface normal comes from two rays).
- Moving slides you along it, and you stop at its edges.
- Backing away or standing up leaves cover.
- RMB pops you up over low cover; at the edge of tall cover you lean 0.65 m out. LMB blind-fires.

**City hours.**
- Corner stores are open 6:00 to midnight; about a third never close. Clerks leave and come back (one spawns per frame).
- Kill a shopkeeper and the shop closes for two days: no clerk and no shoppers, with flowers, candles and a "CLOSED · in loving memory" sign outside the door.
- During the rush hours (7:00–9:30 and 16:30–18:30), half the downtown and commercial walkers are business types walking faster.
- Bus seats fill by time of day: 85% at rush hour, 60% at lunch, 15% at night, 45% otherwise.

**Street crime that isn't yours (`NCRIME`).** One event every 2.5–5 minutes (sooner at night), only at 0 stars, in front of you and 15–60 m away:
- **Mugging:** the mugger approaches, holds up the victim, takes the cash and runs.
- **Car theft:** smashes the glass, sets off the alarm and drives off.
- **Street fight** between two bystanders.
- **Shoplifter** running out of a store as the clerk shouts.

For muggings, fights and shoplifters, a patrol officer turns up 5–14 s later out of sight and runs the culprit down and arrests them (`npcCop`). If you stop a mugger yourself, nobody reports it (`HERO`) and the victim drops you $60–160.

---

## 2zf. Update (build 57): windows in vans and buses, rams, the chainsaw, crashes into buildings

**Pause menu flicker.** The game kept drawing under the menu's blur at 30 fps, and the dynamic resolution kept changing as it did.
- Now one still frame is drawn when you pause, and nothing more until you resume (`PAUSEDRAW`). A window resize redraws it.
- Dynamic resolution only runs while you're playing.

**Steering wheel.** The hands reached 15–25 cm past the wheel on every model. The wheel is now at seat + 0.55 m, and the dashboard follows it but stops short of the windscreen base. The far-away stand-in figure's hands moved too.

**Your car never rolls.** `crashFlip` skips the car you're driving or riding in. Other cars still roll; buses, bikes, tanks and boats don't.

**Windows in vans, delivery trucks, ambulances and buses.** These bodies were solid boxes with glass painted on the side.
- Now `boxyNotch` finds the window band, and `carBody` builds those bodies in three pieces: rear, cab and front. The cab piece is a lower body plus a roof, with a real gap between them.
- The side glass covers the gap, and there's a dark floor at the sill and a headliner inside. The armored truck (SWAT) stays solid.
- Van drivers are visible through the side window.

**Buses.**
- The window glass is lighter (opacity 0.28) and runs to the front on both sides, apart from the doors.
- Every rider has a dark seat back. Within 45 m, the riders are seated characters, created two per tick.
- Ramming a bus breaks the glass on the side you hit. Riders within about 1.6 m of the impact are hurt, or killed above 14 m/s (`ramCabin`).
- Tested: a 22 m/s SUV into a bus's side killed the 2 nearest riders and broke that side's glass.

**Rams into cars.** At 11 m/s or more, the struck car's glass shatters. From 12 m/s, a hit on the passenger side hurts the passenger (they can die), and a hit on the driver side hurts the driver, with wounds and blood. Your own car only loses its glass.

**Chainsaw.** It cuts the piece under your crosshair, slowly, and pieces drop instead of flying (`sawCut`, `sawPieces`, `cutPiece`).
- Cutting times on a corpse: forearm or shin about 0.7 s; whole arm or leg about 1 s; head about 1.1 s; the torso goes in 3 chunks of about 1.3 s each, then the body is gone. A living person takes 1.4x longer.
- Cutting off the head kills; any other piece makes them bleed out. If you aren't aiming near anything, it takes the piece nearest the blade.

**Crashes into walls and buildings.** A wall hit at 9 m/s or more throws masonry debris and dust and leaves a crater mark (the last 50 are kept).
- It also feeds `damageBuildings`, scaled by vehicle mass: a sedan hit at about 26 m/s did 36 damage to a small 18x12 m building with 228 hp. A few hard hits make it smoke, and more bring it down. A bus does far more.
- The news then says a vehicle smashed into it, not an explosion (`o.crashed`).

---

## 2ze. Update (build 56): people in cars, glass first, rollovers, gentler crashes, hand keys

**People in cars are real people.** The car body used to be solid up to the window line, so its flat top hid everyone below the shoulders.
- The cabin is now a hollow tub (`carTub`, plus the tub rings in `carBody`), with dark door cards and carpet. You can see down into the seats.
- Within 42 m of the camera, the driver and any passenger are full characters in a seated pose (`makePuppet` / `seatPuppet`, managed by `updatePuppets`): hands on the wheel, or in the lap for a passenger. At most 16 cars have them at once.
- Further away, the old merged bust is shown instead. Puppets are dropped when you take the car, or when it's wrecked or empty.
- The window glass is a little lighter (opacity 0.36).

**Glass first.** The first round that reaches a car's windows blows all the glass out (`shatterCarGlass`), with shards and a sound, and hurts nobody.
- Later rounds hit the driver, or, from the passenger side, the passenger (`passengerHit`, about 60 hp).
- Wounds land on the seated person's head or torso, on the side the shots came from. Blood goes on the seat back and headrest behind them (`carWound`).
- A dead driver slumps over the wheel (`SIT_DEAD`), and the foot-on-the-gas behaviour from build 55 is unchanged. A dead passenger slumps sideways.

**Crashes are gentle on you.**
- In a car you lose at most (closing speed - 20) x 0.8 health, and never below 30, so a crash alone can't kill you.
- Your own car takes half the crash damage and can't go below 8% from crashes, so it won't catch fire under you (`crashCarDmg`). The fire-starting from build 55 now only applies to AI cars.
- On a bike, a hard hit throws you off (`bikeThrow`). You lose up to impact x 0.9 health, never below 20, and get up after about 1.5 s.
- Tested: head-ons at about 30, 45 and 60 m/s closing speed cost 9, 19 and 36 health (before the final x0.8 trim); a 25 m/s bike crash cost 35.

**Rollovers.** A hard hit, mostly in the side, can trip the lighter car over (`crashFlip`):
- The chance rises with impact speed above 13 m/s, how side-on the hit is, and how much heavier the other vehicle is. Tanks, bikes, boats and buses never roll.
- The car tumbles through the air, bounces and rolls up to 4 times (`tumbleLand`; each landing dents it, can shatter glass and costs hp), then settles upright, on its side, or on its roof (`car.flipped`).
- While tumbling it still hits people, cars and walls, so it can wreck what it rolls into. `tumbleVisual` lifts the body so its lowest corner stays on the ground.
- After 1.2 s an AI driver crawls out and runs (cops get out as cops), or you're put out of the car.
- Walk up and press the vehicle key to heave a flipped car back onto its wheels. Flipped cars can't be entered or driven.

**Hand keys.** A new "Hands" group in the controls holds:
- Shove (Y; hold it to grab).
- Grab a person (J; press again to let go).
- Throw who you're holding (Y, or click).
- Drag a body (E).
- Shoulder a body (Space while dragging; now its own `lift` bind).
- Bag a body (B).

---

## 2zd. Update (build 55): bumps, bodies in cars, crashes

**Bumpy country roads.** Outside the city the ground height came from a 6 m height grid, so cars rode over little ridges between grid points.
- On a road, `groundY` now uses the road's own smooth profile (`roadSurfaceY`, with road segments bucketed in `MT.segB`). Where roads cross, the highway wins.
- On the mountain highway, average roughness dropped about 5x.

**Bodies landing.** A ragdoll that falls onto low furniture (a bed, a table, a counter) now rests on top of it, about 0.5 m up, instead of being pushed sideways off it. Only tall things act as walls. Limbs are also kept out of car bodies.

**People in cars.** Drivers and passengers now have thighs, shins and shoes (and the driver's hands on the wheel), not just a bust (`seatedLegs`).
- Shooting into a car leaves wounds on the person and blood on the side glass (`carWound`, up to 6 wounds and 5 blood marks).
- A driver killed at the wheel slumps forward. About 2 times in 3 their foot jams the gas (`deadFloor`): the car takes off for 5 to 10 s and can run people over, you included. Otherwise it creeps forward for a moment.

**Crashes hurt.** Car damage from a collision now grows with the square of the impact speed above 10 m/s, so a big hit is a big hit. `crashHurt` handles the people in the cars from about 15 m/s of closing speed:
- You lose health, with a red flash on a hard hit.
- AI drivers have their own health: about 70, or 110 for police. A moderate crash can scare them into panic; a hard one kills them.
- Above about 27 m/s, a car may catch fire.
- Tested before a final softening: 36 mph closing speed means dents only; 100 mph head-on kills both drivers and both cars burn. After the softening, a 63 mph head-on now badly hurts AI drivers instead of always killing them.

---

## 2zc. Update (build 54): clipping

**Cars sinking into the ground.** A car's height came from the ground under its centre, and the body just tilted to match. On a bump, a kerb, a junction or the edge of a levelled pad, the nose or tail ended up under the ground.
- Now the four wheel points are sampled, the body takes their slope, and the car sits high enough that no wheel is below the ground (`wheelGround`).
- This applies within 220 m of the camera; bikes are left as they were.
- Tested: 136 cars over 10 s of play, no bad positions.

**Cars inside houses.** Two causes, both fixed:
- **Coverage:** cars checked walls with only two circles near their ends. A bus had a gap of about 5 m between them, and a thin house wall could slide into it. Cars now use as many circles as their length needs.
- **Pushed out the wrong way:** a fast car crossing a thin wall's centre line was pushed out on the far side. Thin walls now push a car back the way it came (`collideCircleFrom`).
- Tested: a bus fired at a house front at 30 m/s stopped against the wall.

**Bodies in walls, cars and furniture:**
- **Roofs and upper floors:** a body put down or thrown on a roof or upstairs used to fall to street height, inside the building, then get pushed out through a wall. Bodies now keep that roof or floor as their ground, with limbs allowed to hang over the edge.
  - A body that reaches the edge moving outward goes over and falls.
  - Tested: thrown mid-roof it stays up; thrown at the edge it falls to the ground below.
- **A crash, fixed:** a body thrown on a plain roof used to crash the window-throw check.
- **Cars:** body parts can no longer end up inside a car's body (`ragCars`).
- **Picking bodies up:** you can now pick up bodies on roofs and building floors (same height only).

**Window climbs:** while climbing through a window or vaulting, the camera stays close (1.5 m) and the near clip drops to 5 cm, so walls stop vanishing or showing through. Not checked in game.

**Still to look at:** ragdolls on low furniture (sofas, benches) are pushed round them rather than lying across them.

## 2zb. Update (build 53): grab and throw people, warning shots, a reputation, news with numbers, wounds, rangers

**Grab someone.** Hold Y (shove) next to someone to grab them. Tapping Y still shoves.
- You walk them along at 2.4 m/s (3.6 sprinting), wherever you like (an alley, say). They plead and shout, and anyone watching may call it in.
- Click or tap Y and you throw them: they hit the ground stunned for about a second and a half, then run.
- E lets them go.
- Thrown hard at an upper-floor window, they go through it.
- Close-protection officers can't be grabbed.
- Tested: grabbed, held 0.55 m in front while walking, thrown about 2 m, down for ~1 s.

**Warning shot (' key).** Inside a shop with a gun, fire one into the ceiling.
- Plaster falls, everyone inside goes face down, and the clerk hands over the till ($280–760, once every 5 minutes).
- **Suppressed:** nobody outside hears and there's no police call.
- **Unsuppressed:** the street hears it and you get two stars.
- Tested: $312 handed over.

**Keys:** trackers have their own key (; by default). L is charges only, so you can't plant the wrong thing. Both new keys can be rebound in the pause menu.

**Chainsaw:** it no longer deletes a body in a second. It works a body over limb by limb (a limb comes off every 9 cuts) and takes about six seconds of cutting before nothing's left.

**Five stars:** past four stars, heat counts for 30%, and the fifth star is held back until you've lasted 75 s at four.

**Wounds:** bullet and blade hits leave marks where they land on the torso or head (up to 7 per person). Blades leave slashes, and punches to the head leave marks. Badly hurt people leave a blood trail as they move.

**Bigger explosions:**
- A downed police helicopter scatters debris, blasts a 16 m radius for 240 damage and burns.
- A car exploding throws debris and sends a second, wider blast (10 m) through what's round it.

**News with numbers, and consequences.** Once it goes quiet after a spree (25 s) and at least three bodies are found, the news gives the count: "N dead around <street>: X civilians and Y police officers".
- **Ten or more dead, or five or more police:** the commissioner promises drastic measures, and they're real. For 8+ minutes the city is on alert: three more officers allowed at each star level, one more car sent, and patrol cars make up 16% of traffic (normally 5%).

**Your police file (`PROFILE`, saved).** Kills, police, public figures, quiet kills and robberies add up to a name the press uses:
- The Ghost
- The Assassin
- The Butcher of Sprawl
- Cop Killer
- Killer
- Armed Robber
- Nobody

It shows at the top of the phone's Intel app. Once you're known, people who see you bare-faced may recognise you, back off and call it in.

**Gun shops say what they sell.** The specialty shows on the map, in the prompt and under the shop's title:
- AMMO & ARMS: handguns, shotguns & gear
- LOCK, STOCK & BARREL: hunting rifles & sniper
- FRONTIER ARMORY: military & explosives
- BULLSEYE TACTICAL: blades, chainsaws & quiet tools

**Map:** Kessler Lumber & Freight and the ranger stations no longer show "undefined".

**Sky:** a plane every 16–38 s, up to six at once. They start 1.5 km away and pass within about 260 m, airliners at 320–460 m and private planes at 110–180 m.

**Events:** rallies and VIP walks do work. They now start every 3–5 minutes (was 6–9). A VIP walk names the street it was last seen on (there's no pin). Rallies keep their pin.

**Your cabin, rebuilt:** a 14 × 10 m log lodge at the end of its own track off the highway, on a levelled pad clear of grass and trees.
- Inside: a stone fireplace with a sofa and rug in front, a kitchen counter, a dining table, a walled bedroom, antlers, warm lights, and the gun cabinet (your armory).
- Outside: a deep porch with chairs and a lantern, a fire pit with log benches (it burns bodies too), a woodpile and the sign.

**Ranger stations:** West Kessler and Pine Lake, one on each side of the woods.
- Each has a green-roofed station, a flag, a lookout platform and a truck.
- Now and then (rarely, one at a time) an armed ranger walks a trail loop near the station.

**Rooftops:** walk-in towers now have their stair hut built into the building, with the roof slab and cornice cut away under it. Coming up the last flight you no longer pass through the roof.

**Highway guard rails** are solid: cars can't drive through them.

**Westbrook:** pavements along every street, street lamps, white picket fences on about half the front yards.

**Not done yet (seen, not fixed):** the ground along parts of the highway. (Cars sinking, bodies in walls, cars in houses and window-climb clipping were dealt with in build 54.)

## 2za. Update (build 52): your own cabin in the woods

You now own two places: the safe house in the city and **your cabin**, a third hunting cabin.
- **Where:** in the trees 55–100 m off the mountain highway, west of Pinewood (around x −1618, z 18 with the current layout). It's placed on flat ground, clear of water and other sites, and the pines are kept off it.
- **Inside:** it's built like the other cabins: a fire going in a stone hearth (you can burn a body in it), a bed, a table and stools, antlers and a lantern. It also has a "PRIVATE PROPERTY" sign at the front and a truck outside.
- **The gun cabinet** in the back corner opens **your armory**, the same storage as the safe house locker: put a gun away in the city and take it out at the cabin.
- **On the map:** a green "Your cabin" marker, in the "You" section of the key next to the safe house.
- **Tested:** the cabin builds, the first-visit note shows, and the cabinet opens the armory.

## 2z. Update (build 51): trackers and intel, Hale's day, private flights, news when bodies are found, the armory, a new wheel and phone

**No more live VIP pins: you find people.**
- Brenner, Victor Hale, contract targets and walking VIPs no longer show live on the map or minimap, and their name tags only show once you've tracked them. Homes are still marked: Hale's house reads "HALE'S HOUSE".
- **Trackers:** you start with 2, and AMMO & ARMS and BULLSEYE TACTICAL sell 3 for $300.
  - **Tap** the plant key (L) next to someone, or next to Brenner's SUV, to stick one on. **Hold** L still plants a charge.
  - From behind, they don't notice. Face to face they do, and any close protection nearby draws on you.
  - Tracked people show on the map wherever they really are, even far away and not spawned (`vipWhere`), as long as trackers are switched on in the phone's Intel app.
- **Intel app:** notes on each person's usual routine, marked as changeable, plus your trackers and the on/off switch.
  - **Brenner:** home ~8:15 → City Hall 9–5 (press around noon) → his bar 5:30–6:30 → home ~7:30.
  - **Hale:** a line on what he's doing today. It's right about 70% of the time.

**Victor Hale's day (`haleNow`, `haleDay`).**
- **Evenings and nights:** home from about 5 pm to 7 am, asleep from 11. Some nights he's up late, and some evenings he's out at the bar until 11.
- **Days,** seeded per game day:
  - court at City Hall, lunch near City Hall, the bank;
  - or the bank, a drive out to Pinewood, then court;
  - or the airfield, flying his own plane for four hours, lunch, the bank;
  - or a day at home.
- **Out and about:** he's at the place with two close-protection officers. Between places he's on the move: trackers interpolate his route.

**Private planes (`PRIV`).** Two small planes at the airfield.
- One flies a loop over the countryside every few minutes: taxi, a long roll, rotate at about 70 mph, climb to around 230 m, the loop, approach, landing, taxi back to its stand. Tested through a whole flight.
- The other is Hale's. On flying days he's in it, and the tracker follows the plane.
- Climb into either and it's yours (no script).
- **Airliners:** take-off checked: they roll, rotate and climb away. They now rotate at 57 m/s with a bit more acceleration, so they lift off well before the end of the runway.

**News waits for a body (`newsOnFind`).** A killing nobody saw isn't news until someone finds the body. If the body is never found (burned, sunk, chainsawed, bagged and hidden), "missing" news follows a couple of minutes later.
- This covers Brenner in his office, at home and outside his bar; Hale anywhere; the Cedar Falls witness; and everyone else (forensics already went by discovery).
- Public killings (the rally, the plaza, a car bomb) are still news at once.
- **A VIP killed with a witness** (`vipKilled`): at least four stars on the spot.

**Police and roofs.** Officers in the street can only hit you on a roof if their line of sight actually clears the roof edge (`roofShotClear`). Stand back from the edge and they can't.

**SWAT helicopter.** At five stars the police helicopter turns SWAT: black, tougher, armed with an assault rifle. When it's over you in the open, four SWAT fast-rope down (within the officer limit).

**Weapons:**
- **Drop the weapon in your hands:** hold Q (a tap still switches weapons). It lands as a pickup, with its rounds, and you won't grab it straight back for four seconds.
- **The new weapon wheel:** silhouettes of every weapon, rounds under each one. The one you point at lifts out in gold and your current one is outlined. The centre shows the name, clip/reserve and "hold Q: drop it".
- **The armory at the safe house** (replaces the locker): "On you" on the left, "Stored here" on the right.
  - W/S choose, A/D switch side, E moves an item across, R moves everything, Q closes.
  - Grenades count too. It's saved between sessions.
  - Anything the police confiscate turns up in there.

**Phone:**
- **It no longer opens the pause menu.** Opening it used to release the mouse, which the game read as "pause".
- **Keyboard control:** A/D (or the arrows) switch apps, W/S choose, E selects. The chosen button is outlined in gold.
- **Apps:** Messages, Intel, Contracts, Jobs, News (1–5).
- **In your hand:** on foot you stop and hold the phone up at chest height, screen lit, while it's open.

**Homes:**
- **Rooms:** single-storey homes with space get a walled bedroom in the back corner with a door frame, about 300 homes in all. It's only built where it wouldn't cut through furniture.
- **The front door:** nothing stands right inside it any more.
- **Night owls:** about a quarter of houses have someone still up at night.

**The carried body when crouching:** it rides on the torso, so crouching lowers it with you (checked).

**Not done:** Hale's drives between places aren't a visible car (the tracker follows his route). Homes don't get a whole set of rooms. Two-storey homes get no new rooms. Only one rooftop situation was checked against police fire.

## 2y. Update (build 50): cooler and steadier, no rain, saner police and cars, bodies you can really handle, blades, a dealership, Westbrook, air traffic

**Performance (it ran hot):**
- **Frame cap:** the game never draws faster than 60 fps (45 on Low), and 30 fps on the start screen and pause menu. A 120 Hz screen used to draw twice as many frames as it needed.
- **Ambient occlusion off:** screen-space AO is off at every quality. It was the most expensive pass, and its noise made the floor look grainy as you walked.
- **No film grain:** the animated film grain is gone too.
- **Resolution:** Medium renders at 1.1× pixel ratio (was 1.25) and High at 1.5× (was 1.75). The canvas no longer anti-aliases on top of the composer's MSAA.
- **Shadows:** the shadow map is redrawn whenever its camera moves. Updating every other frame left a stale, shifted shadow under you: the floor "glitching" as you walked.
- **Distant flicker:** the camera's near plane is 0.25 m (was 0.15) to cut z-fighting between ground layers in the distance. It drops to 0.05 m in the stairwell, the lift and vents, so walls don't vanish in front of you.

**Rain is gone.** Weather is clear or overcast. Cedar Falls stays grey but dry.

**Cars:**
- **Top speeds:** ordinary cars top out at 75–80 mph. Shift (nitro) takes anything ordinary to 100 mph.
- **The fast ones:** the sports coupé (95 mph), muscle car (105 mph) and supercar (130 mph) are `rare`. About 2% of traffic is a sports or muscle car and 0.6% a supercar, and only 2 supercars are parked about the city (was 6).
- **The speedometer** reads MPH.
- **PRESTIGE MOTORS:** a dealership with a glass showroom, turntables, a forecourt with bunting, and display cars (locked; they're for sale).
  - E at the counter buys a compact, saloon, SUV, motorbike, sports, muscle or supercar.
  - Your car waits on the forecourt, unlocked. The last few you've bought are there again next session.

**Police:**
- **A hard limit on officers near you** (600 m), counting every source: crews, partners, roadblocks, SWAT. The limit is 2, 4, 6, 8 and 10 for one to five stars.
- **Pacing:** units are sent every 6–9 s. Roadblocks only come when they fit under the limit. Officers far away and out of sight are recalled when there are too many.
- **Five stars:** an armoured SWAT truck with four officers (vests, assault rifles or shotguns) instead of a flood of patrol cars.
- **Reaching it:** heat gained past four stars counts for 45%, so the fifth star takes real effort.

**Fewer people at night.** Pedestrian density is 32% of daytime in the evening and 16% after midnight, and the extras drift off out of sight.

**VIPs:**
- **Same face every time:** Brenner and Victor Hale come from a fixed seed (`withSeed`).
- **Hale is always home now,** not only during his contract. He has a vest, and by day two close-protection officers watch his door. His house has "V · H" in gold over the door and lamps on the piers.
- **Rich homes (`luxuryFront`):** every rich home now has one of three looks: timber cladding, a flat canopy on posts with a light strip, a glass balcony upstairs, a low wall along the street with lit piers and planting, sometimes a reflecting pool, and uplights.

**Bodies:**
- **Carrying:** the body and the body bag ride on your actual shoulder each frame, so they follow crouching, stairs and your stride instead of floating.
- **Indoors and on roofs:** bodies you set down stay on that floor or roof (`bodyFloor`). Dragging keeps the heels on the floor you're on.
- **Throw it:** click (or shove) with a body on your shoulder. A body thrown hard at an upper-floor window goes through the glass and falls to the street.
- **Other ways to get rid of one:** burn it in a fireplace, or take it apart with the chainsaw.

**Things you couldn't do before:**
1. Throw a carried body: off roofs, through windows, into water, onto the tracks.
2. Hurry with a body: carrying at 2.8 m/s, sprinting at 4.6 (was 2.4/3.6); dragging at 2.2/3.2 (was 1.8/2.4).
3. Jump and vault with a body on your shoulder.
4. Climb walls and fences up to about 2.5 m anywhere, the mayor's estate wall included. Building walls aren't climbable.
5. Vault vans and pickup trucks, not just cars.
6. Aim with a body in your arms: you drop it there and then.
7. Bag a body while it's on your shoulder.
8. Drag a body up and down stairs and along any floor.
9. Burn a body in a fireplace.
10. Cut a body up with the chainsaw until it's gone.
11. Crawl through vents into the mayor's house and the bank (round the back).
12. Shove with a body on your shoulder: it's thrown.

**Weapons:**
- **Chainsaw (hold to cut):** it rasps, draws a crowd and sprays blood. It severs limbs once someone's hurt badly enough. On a body, 14 cuts and there's nothing left to identify.
- **Katana** (58 damage) and **machete** (44).
- **Each gun shop has its own range:**
  - **AMMO & ARMS:** pistols, SMG, shotgun, gear.
  - **LOCK, STOCK & BARREL:** hunting: shotgun, carbine, sniper, revolver, throwing knives.
  - **FRONTIER ARMORY:** military: assault rifle, RPG, grenades, explosives.
  - **BULLSEYE TACTICAL:** blades and quiet work: chainsaw, katana, machete, knives, suppressors, charges.

**Shops:**
- **Doors:** shop doors stay shut unless you're at them or someone is walking through. Before, anyone within 2 m held them open.
- **Clerks:** in an apron with straps and a name badge, in the shop's colour.
- **Customers:** one to three of them are already browsing when you come in.
- **Inside:** a cigarette and lottery wall behind the till, a coffee machine, an ATM, posters and a fruit stand.

**Cabins in the woods:** the two hunters' cabins are real buildings now. Inside: a log fire in a stone hearth (with chimney smoke), a bed, a table and stools, antlers and a lantern. Outside: a porch, a woodpile and a truck.
- Carry or drag a body to the hearth and press E to burn it.

**Westbrook:** the flat land between the city and the hills.
- Two streets of houses with cars in the drives and trees.
- Westbrook Plaza: four shops, two of them real (WESTBROOK MART and WEST PHARMACY, with clerks and tills), a car park and a pylon sign.
- Kessler Lumber & Freight: a shed, stacked timber, containers, a forklift and a fence. Workers in hi-vis are there by day.
- People walk the streets (fewer at night), and there are traffic signals at the junctions with the main road.
- It sits north of Hollis Farms. The map wasn't made bigger: the suburb uses land that was empty.

**Sky and airport:**
- **Traffic overhead:** every 45–110 s an airliner crosses high (520–720 m) or a private prop plane potters over low (160–260 m) and wanders a little.
- **AI airliners** take off over a longer roll.
- **Your own take-off:** the prop plane rotates at 31 m/s (about 70 mph) and the jet at 66 m/s, with half thrust while rolling. You **look up to pull the nose up**; it won't leave the ground on its own.
- **Airport police:** four officers (close protection) at the checkpoint and the gates. Stay airside and they come for you. Taking a plane from the apron is aircraft theft: two stars and they open fire.

**Not done:**
- Vents only lead into the mayor's house and the bank.
- The lift camera and the first-person stairwell keep the near clip, but crowded corners can still clip.

## 2x. Update (build 49): lifts you ride, stairs you walk, and build 48's rough edges

**Lifts are a car you ride (`makeCab`, `updateCabs`, `cabY`).** The old lift faded the screen and teleported you.
- Every walk-in building has a lift shaft at the back of each floor, and the lobby has a landing with sliding doors, a frame, a floor display and a call button.
  - The car is its own model: mirrored back wall, handrails, a lit ceiling, a button panel, and a display over the doors that counts the floors (▲/▼).
- **Riding it:**
  1. E at the landing calls the car.
  2. It travels from wherever it is, and the doors open.
  3. Walk in. The view switches to a fixed lift camera in the back corner.
  4. E brings up the buttons: W/S to choose and E to go, or type the floor number (0 is the lobby). Q closes them.
  5. The doors close and the car moves up the shaft with you in it. Travel time depends on distance: 2.4–8.5 s.
  6. The floor you're going to loads while you travel, so it's ready when the doors open.
  7. Walk out.
- **Doors:** they close after 5 s if nobody's near and bounce back if you're in the doorway. The landing doors are a wall unless the car is there and open.
- **Floors:** slabs and ceilings now have the shaft cut out of them, so no floor sweeps through the car.
- **Skyscrapers:** each has a lift column in the lobby corner ("ROOF DECK") that rides to a hut on the roof. The hut now has a real doorway.
  - The tower above the lobby is solid, so the city geometry is hidden while the doors are shut and the car is moving.
  - The old E-teleport (`nearElevator`) is retired.
- **The roof:** the tower lift serves every floor. The roof is a walk up the last flight of stairs.

**Stairs you walk.** The stair door used to open a floor panel and fade you to your floor. Now you walk through the green-lit door and up or down the switchback flights, landing by landing, to any floor and out onto the roof.
- From the roof, walking into the hut takes you back down.
- In the stairwell the view goes first-person (the shaft is too tight for a third-person camera) and comes back when you step out.
- The tall dark slab that stood in for a handrail is now a proper stepped rail on both flights.
- Tested: floor 3 → landing → floor 4 on foot. Roof → hut → top floor.

**Fixed from build 48:**
- **Trees through walls:** street trees whose canopies reached into a building are stepped toward the kerb (up to 0.7 m) or shrunk to fit (`trimTreesFromBuildings`). Of 5,656 trees, about 1,150 were adjusted and 18 were too close to keep.
- **Treadmills:** gym-goers run on them now (`poseJog`): legs and arms in a running cycle, bouncing on the belt.
- **The "radius is NaN" warnings:** vans and ambulances measured the driver's seat behind the cab outline, which returned −Infinity for the roof height. Their seats and wheel were never drawn, and three.js complained every frame. Fixed in `cabinLayout`. Zero NaN geometry after load and a 10-second run.
  - `?nandbg` in the URL logs any future NaN geometry with its details.

## 2w. Update (build 48): walk into most buildings, Brenner at his desk, close protection, new weapons, charges on anything, buildings that come down

**Bodies: dragging works.** Holding E for 0.4 s used to lift the body onto your shoulder, so anyone holding E to drag ended up carrying instead.
- E over a body now drags it, straight away. Holding E does nothing extra.
- While dragging, Jump lifts the body onto your shoulder.
- While carrying, E puts it down. At an open trunk, E loads it, as before.
- Jumping is disabled while you drag.
- Tested: tap → drag; held 1 s → still dragging; walked 1 s → still dragging; Space → carrying; E → down.

**Parachute and base-jump landings.** Shops, bars, city homes and skyscrapers weren't marked as flat-roofed, so landing on one shoved you sideways off the edge.
- They now hold you: hollow buildings and homes record `flatY`, and skyscrapers point at their own roof level (`skE.sky`).
- Rooftop clutter is solid. Every tower records its vents, stair huts, tanks and crowns in `SKYLINE[i].ru`, plus any upper section stacked on top. Landing on top of a vent steps you off it.
- Tested on a shop, a skyscraper and a plain tower: each landing holds, and you can't walk through a roof unit.

**More buildings you can walk into, each one something.**
- Towers with a shopfront ground floor (`store: true`) used to have no door. The shopfront band is now four faces with the doorway left open, and the shop is real inside.
  - The ground floor is a shop: a till with a clerk (sometimes armed) and cash to take, aisles of shelved products, a drinks fridge, and customers.
  - The floors above are flats or offices.
- Walk-in buildings went from 142 to 314.
- Every walk-in building has a use, picked from its facade and position (`bldUseFor`): offices, flats, gym, clinic, storage or City Hall. All but the shop towers have a name plaque over the door.
  - **Gym:** treadmills facing the windows, a mirror wall, bench presses, a dumbbell rack, stretching mats, people working out.
  - **Clinic:** beds with curtain screens, a nurses' station, nurses and patients, sometimes a pharmacy box to take.
  - **Lobbies by use:** flats have mailboxes; clinics have a waiting area and patient; gyms have treadmills by the door.
- **People are there before you arrive.** A building's ground floor now loads within 60 m of its door (was 28 m).
  - Homes: residents used to spawn only between 12 and 70 m away, so a house you walked straight up to was often empty. The near limit is gone, and the cap went from 14 to 20 people.
- **The sign atlas was full.** It held 128 text rows and the city used about 180, so later signs drew blank or showed the wrong text. It's now 8192 px tall (256 rows).

**Brenner works at City Hall.**
- City Hall is a real building now: you go in under the portico. The lobby has a metal detector, flags and an officer at the desk.
- Floor 1 is the mayor's office: a big desk on a red rug, flags behind it, bookcases, a leather sofa, a secretary out front. Sometimes there's a gold watch on the desk.
- From 9 to 5 Brenner is at his desk with three close-protection officers (pistol, SMG, assault rifle). He no longer stands on the plaza.
- At noon (12:00–12:45) he steps out for a press conference on the steps: four officers and a handful of reporters.
- Killing him in the office gets its own headline.
- He wears a vest (150 hp, body shots reduced).

**Close protection (`eliteize`, `updateElite`).** Brenner's office detail, his press and motorcade guards, the estate guards, rally security and every contract bodyguard are now elites. Earpiece, shades and a vest on each.
- **Tougher:** 230 hp. A vest takes 38% off body shots and 30% off punches.
- **Better shots:** fire every 0.22–0.5 s (civilians 0.5–1.1), with about half the spread, out to 34 m.
- **Watchful:** standing guards turn and scan every few seconds.
- **Warn, then shoot.** They warn you if, facing you or within 3.2 m, they see any of these: your gun aimed, a body you're carrying or dragging, a mask within 10 m, two or more stars, or you near the principal. Keep it up for 1.6 s, aim at them, or touch the principal and they draw.
- **Sharing a threat:** one engaging pulls in every other elite within 35 m, as if by radio.
- **The principal:** they react if their principal is hurt or killed in sight (25 m, same floor, clear view), then hustle them away. A silent kill through walls still goes unnoticed.

**Fixed: shooting indoors.** Two fixes, and both mattered for every lobby guard:
- `losClear` treated the building's own footprint as a wall, so nobody inside a walk-in building could see anyone else. Now, inside the current building, only the stairwell walls block sight.
- `fire()` only used the in-building bullet path for the player. People who work inside now shoot inside too.
- Tested: Brenner's three officers took 88 hp off you in 3 s once you drew on him.

**New weapons.** Number keys: 1–9 as before, then − revolver, = assault rifle, ` throwing knives. All three are on the wheel too.
- **Revolver:** 62 damage, 6 rounds, slow and loud.
- **Assault rifle:** 25 damage, 30 rounds, fast, a little more kick than the carbine.
- **Throwing knives:** silent.
  - An unaware target or a head goes down in one (elites only take damage).
  - Otherwise 70 damage.
  - Each throw draws the next knife in 0.28 s.
  - The knife drops where it lands or where it hit, so walk over it to pick it up.
  - They fly with a little drop, spin, and bounce off walls.

**Four gun shops.** AMMO & ARMS keeps its spot. Three more were added: LOCK, STOCK & BARREL, FRONTIER ARMORY and BULLSEYE TACTICAL. Each is on the map with its name.
- The menu has two tabs, switched with A/D or Q.
  - **Guns:** pistol, revolver, SMG, shotgun, carbine, assault rifle, sniper, RPG, ammo for everything you own, knife and bat.
  - **Explosives & gear:** throwing knives ×8, grenades ×4, body armour, remote charges ×3, a demolition pack of ×8, gloves, suppressors, body bags.
- The old menu had 13 items on 12 keys, so body bags couldn't be bought. Fixed.

**Remote charges on anything (`plantRemoteAny`).** Press L and the charge goes on what's in front of you:
- **A car,** as before.
- **A person, alive or dead.** It goes on their back if you're behind them. If they're unaware they don't notice; otherwise they shout and run. Whoever wears it dies when it goes off.
- **A wall or door,** at chest height, inside or out.
- **The ground,** if nothing else is there.
- You can have up to 12 charges planted (was 6).

**Buildings come down (`damageBuildings`, `collapseBuilding`, `RUINS`).**
- **Damage:** every explosion damages buildings it goes off against. The reach is about half the blast radius, and damage falls off with distance.
- **Health:** 160 + width × depth × height × 0.05. A house takes about 2 charges or rockets, a six-storey block about 6–8.
- **Too big to fall:** towers over 48 m (counting any sections stacked on a podium) and halls over 1,500 m² only take scorch marks.
- **Warning:** past 45% it smokes from the roof, and you get a warning.
- **Collapse:** the building's actual merged geometry pancakes over 2–4 s into a heap. Upper floors fall last and walls splay out a little. Pavements outside the footprint stay put, while awnings and signs come down.
  - A heap of broken slabs, blocks and bent rebar is added on top.
  - Dust clouds, secondary blasts, a big flash and screen shake.
  - The rubble burns and smokes for a minute and a half.
- **Afterwards:**
  - Everyone inside dies, including you if you're in there.
  - The doorway, lift and stairs go, and the roof becomes the low rubble top.
  - The map shows a rubble patch.
  - The news reports a collapse, and you get three stars.
- Tested: an 8-charge wall job on a 22 m block. It came down as described, with the street round it untouched.

**Not done / known:** fixed in build 49 (trees through walls, treadmills, the NaN warnings).

## 2v. Update (build 47): fights that land, carrying and dragging, a less grid-like city, a subway, Snowcrest

**Fighting**
- **Punches:** they reach (range + 0.6 m, a wider cone) and close the gap on contact, so they connect instead of whiffing. Jabs push less, so you can keep a combination going.
- **Kicks:** a kick ragdolls the target (`kickRag`). They go limp for 1.3–2.1 s, then get up and carry on.
- **Blood:** every landed hit throws droplets in the direction of the blow (`bloodHit`), and heavy ones leave a spatter on the ground.
- **Knife:** the move follows from where you stand:
  - Slashes alternate left and right.
  - Running in is a lunge to the chest.
  - From behind it's a stab in the back.
  - A sneak takedown cuts the throat.
  - The arm pose is eased, so it no longer snaps.

**Bodies**
- **Drag (E):** stand over anyone down and press E. You drag them by the collar at walking pace.
- **Carry (hold E):** puts them over your shoulder.
- **Car trunk:** E at the back of a car puts the body in.
- The prompt appears whenever you're standing over someone.
- **Key changes:** these keys moved, and old saved bindings are migrated:

  | Action | New key |
  |---|---|
  | Dodge roll | Z |
  | Crouch | C |
  | Camera | U |
  | Carry | E |
  | Bag | B |

**The city**
- **Sprawl Common (`BIGPARK`, `pickBigPark`):**
  - Nine blocks south of downtown are merged into one park, and the streets through it are removed (their four crossroads are switched off in `NODE_OK`).
  - The surrounding streets now meet it at T-junctions.
  - Inside: a lake, a loop path, woods, a bandstand and joggers.
- **Promenades (`PROMS`, `EDGE_OFF`):**
  - Seven street segments downtown and in midtown are closed to cars.
  - Each is paved, with bollards at both ends and tree planters and benches down the middle.
  - `edgeOK` respects them, so traffic, GPS, road paint and the road mesh all route around them.
- **Satellite-style map:**
  - Roofs vary in colour and show parapets, rooftop units and the odd helipad.
  - Taller towers are drawn over their podiums.
  - Trees cast shadows, and a fine grain covers everything.
  - Closed streets get no lane paint.

**Sprawl Metro (`SUB`)**
- **Stations:** four. The street entrances (green globe, SUBWAY canopy) are in the Common and on three promenades. They're on the map as **M** under Landmarks.
- **Going down:** E at an entrance fades you down to the platform.
- **Where the platforms are:** in enclosed halls far east of the map, the same way the airport interior works. `groundY` reads them for x > 4100.
- **Trains:** one per station every 80 s, on a schedule (`subPhase`): about 9 s coming in, 14 s with the doors open, 9 s pulling out.
- **Riding:** E at the platform edge while the doors are open takes you to the next station.
- **The track bed:** you can walk or be shoved off the edge. You can't step back up (Space climbs out).
- **The train:** kills anyone in its path. If you put them there, it counts as your kill, and anyone who saw it can call it in.

**VIPs on the map (`drawVipMarker`, `vipLabel`)**
- **Their own section:** Mayor Brenner, his house, Victor Hale, your contract target and roaming VIP events are the first section of the map key, "VIPs & targets". It can be toggled like the others.
- **People:** shown as a pin with a silhouette and a pulsing ring on the ground. **Homes:** shown as a house shape. Both are drawn on top of every other icon.
- **Name tags:** each VIP always has a coloured tag with a status:
  - Brenner: in his SUV, City Hall, at his bar, home, or home asleep.
  - Hale: home, or home asleep.
  - Your contract target, and the name of a roaming VIP.
  - On the minimap, a VIP off the radar is pinned to the edge with its distance, and its tag stays inside the frame.
- **Brenner at home:** his pin shows there too, and only one tag is drawn.

**The country**
- **No more random hills:**
  - The foothills and the hills north and south of the city are much flatter (`mtNatural`). Only the Kessler Range keeps its height.
  - Mirror Lake's shore no longer ends in a sheer rim: it rises gradually back to the land, so the cliff walls around it are gone.
  - The Cedar River's banks are filled up to the water so it never floats.
- **Cedar Falls is bigger:**
  - Mill Street runs behind Main Street, joined by two cross streets.
  - It has more clapboard houses, a pharmacy, a bakery, The Logger's Rest, Cedar Falls School, and the Hollis & Sons sawmill by the river.
- **Snowcrest (`SKI`, `buildSkiVillage`):**
  - A ski village in the Kessler Range on the north shore of Mirror Lake, up a side road off the Kessler Highway.
  - Timber chalets with snowy roofs, the Snowcrest Lodge and a welcome arch.
  - A gondola rides up to the highest peak within reach. Its cable follows the slope over pylons, and red and white cabins run up and down.
  - Three ski runs come back down, with no trees on them.
  - Visitors walk the village street.

---

## 2u. Update (build 46): Brenner's motorcade, remote charges, witnesses only

**His day (`mayorPhase`):**

| Time | Where he is |
|---|---|
| 8:15–9:00 | Drives home → City Hall |
| 9:00–17:00 | City Hall plaza |
| 17:00–17:30 | Drives to his bar (the bar nearest City Hall) |
| 17:30–18:30 | Outside the bar with two bodyguards |
| 18:30–19:15 | Drives home |
| Rest of the time | Home (asleep at night) |

The map's **B** marker (Jobs & targets) shows where he is at the moment, and the car itself while he's driving.

**The motorcade (`MC`, `updateMotorcade`):**
- **The SUV:** each leg's route is planned with `gridPath`. Out of view he moves along it on schedule. Come within about 230 m and a black SUV is really there (out of sight when it appears), driving the route with `followPts`. It's tougher than a normal car (1.7× health) and has a gold MAYOR BRENNER tag over it within 80 m.
- **Reactions:** gunfire near it, or you aiming at it from close, makes the driver floor it. If the driver is shot, the car drops below 55% health, or it's boxed in near you for 3.5 s, a bodyguard and the driver come out shooting and Brenner runs (tagged).
- **Death:** if the car is wrecked with him still inside, he's dead. Either way the BREAKING story airs about 45 s later.
- **Clean-up:** the car parks when it arrives and is tidied away once you're gone. If a leg's time runs out while nobody's watching, he counts as arrived. The venue (City Hall or the bar) takes over from there.

**Remote charges:**
- **Buying:** AMMO & ARMS sells three for $450 (up to 9 carried).
- **L (plant):** sticks one to the car in front of you (on the panel you're facing, at door height, and it moves with the car). Otherwise it drops one on the ground. Up to six at once, with a blinking red LED.
- **0 (detonate):** sets them all off in quick succession. A charge on a car blows the car up on the spot.
- Both keys can be changed in the controls menu, and the utility panel shows charges carried and planted.
- Planting counts as a crime only if somebody sees it.

**Witnesses only:**
- `witnessCall` now always needs line of sight. Before, anyone within 6 m counted, even through a wall.
- Gunshots and explosions are the exception (`reportCrime(…, noisy)`): heard within 40 m (60 m for cops), no line of sight needed.
- A witness's call now takes 6–9 s (was 4–6.5), so you have time to stop them.
- A cop or police driver killed with nobody watching no longer brings the police straight away.

**News waits:** a body still has to be found by someone with line of sight. The story then airs about 80 s later (it was 14 s), and the motorcade or bar killings air about 45 s later.

## 2t. Latest update (builds 44–45): Brenner's estate, a mayor you can't miss, roof landings, a real parachute, break-ins, street life

**Brenner's estate (in the city).** `pickMayorBlocks()` picks four residential blocks in Northgate (near x 0, z −440) and turns them into one walled estate. It removes the crossroads between them, which takes out the four inner streets for traffic and the road surface. Pedestrians don't spawn there or cross into it (block type `estate`). `groundY` uses `mayorEstGround`: the house floors, flat grounds at one height, and the pavement outside.
- **The mansion:** a 38 × 20 m two-storey home built with the normal home system, so it has doors, windows, loot, an alarm and the upstairs. It has extra windows on the long sides, a flat roof and a white stucco finish.
- **Grounds:**
  - a wall with a lit gateway, a barrier and a guard booth
  - a circular drive round a fountain, and a six-column portico
  - topiary, flower beds and statues
  - a pool with loungers, a helipad, a three-door garage, a flag, and hedges along the walls
- **Ways in:**
  - the front door
  - the open back window by the drainpipe (as on any home)
  - a service ladder up the side wall to the roof (E at its foot)
  - a parachute landing on the roof
  - On the roof, E at the skylight smashes it and drops you onto the upstairs floor. The roof also has vents, air handlers and a dish.
  - Standing on the roof no longer counts as being inside, so it doesn't start the alarm countdown.

**The mayor all day.**
- **Schedule:** City Hall 9:00–17:00. At home the rest of the time: awake mornings and evenings (pottering between rooms, a pistol in the drawer) and asleep on the sofa at night. Before, he didn't exist between 17:00 and 21:30, or on "away" nights.
- **Guards:** four walk the grounds while he's home (two when he's out), plus one on the gate. Guards and the mayor aren't culled at 125 m like ordinary pedestrians.
- **Look (`brennerize`):** a navy suit, red tie, gold sash of office, lapel pin, and a gold **MAYOR BRENNER** tag over his head within 55 m. This applies at home, at City Hall and on the rally stage.

**Roofs and the parachute.**
- **Landing on roofs:** you now stay on any flat roof you land on: towers, garages, the mansion. On a tower with stairs you get its proper roof, hut and all. Pitched house roofs still tip you off.
- **New canopy (`buildChuteV2`):** a seven-cell ram-air wing with airfoil-shaped cells and lines down to risers at the shoulders. It snaps open over 0.8 s and flutters slightly.
- **Pose:** free fall is a stable arch, or a head-down dive while tracking (forward). Under the canopy, hands are on the toggles and the inside hand pulls down when you turn. Below 3 m you flare (both hands down, legs forward).

**Break-ins.**
- **Suspicion:** residents who are awake build suspicion over a second or two when they see or hear you. Facing you, close by, you standing and aiming all make it faster; crouching and staying out of sight let it fade. At about a third they say "Hello? Who's there?" and come to look. When it fills, they react as before. A gunshot, or walking straight into them, still alerts them at once.
- **Opening a front door:** done normally, it creaks and puts anyone awake on edge. Crouched, it eases open slowly and silently.
- **Kick (V) at a closed front door:** blows it in. It's loud: everyone inside reacts at once, armed-at residents tend to freeze, sleepers wake, an armed alarm goes off, and anyone on the street sees it.
- **Cops and others indoors:** they route through the house's partition doorway (`room.pdoor`, used by `navPoint`) instead of pushing into the wall.

**News.**
- Bodies found within about 14 s of each other become one story. There are five single-victim wordings, each describing the victim (a jogger, a businesswoman, a police officer and so on), and four for several victims.
- Headlines are tagged by desk (BREAKING, CRIME, POLITICS, LOCAL), each in its own colour. There's a 22 s gap between stories, except breaking news. The queue keeps at most a few stories, and breaking ones are never dropped.

**Street life.** About every 20 s a walker near you may stop to take a call (with overheard lines), text, look up at the buildings, stretch, tie a lace, or dance. Two passers-by may start an argument, or a gym-goer may break into a jog. These ride on the existing `visit` state, with new poses for each.

## 2s. Latest update (build 43): the flicker hunt (z-fighting)

"Things vibrate like two objects inside each other" is z-fighting: two surfaces at the same height fight over which one draws. I didn't guess. I wrote a scanner that walks every static triangle in the world. In 2 m cells it samples points and measures the exact height of every upward-facing surface there, then reports places where two different pieces sit within 3–4 mm of each other. Across the whole map that was **6,071 samples** before and **about 160** after, all small leftovers of a few m² each (a mountain road edge, a couple of lots, under the sea).

What was flickering, and the fix:

| What | Where | Fix |
|---|---|---|
| The kerb strips and the pavement slab under them, 1.5 cm apart and crossing on slopes | Every city block, the biggest source | Slabs now stop at the kerb instead of running underneath |
| Upstairs floor in every two-storey house: its top shared a surface with the ceiling slab below | Upstairs in houses | The slab stops 2 cm short |
| Highway and side-road junctions | Country roads | The side road's ribbon is trimmed to start at the highway edge. Any corner that still reaches onto the highway is sunk 0.4 m under it. Side roads also sit 3 cm lower |
| Boulevard sections overlapping where they meet at an angle (road, pavements and kerbs) | Boulevard | Each section 1 cm apart. The roadway is cut from one ribbon so its pieces share exact edges |
| Overlapping aprons, the ring-road corners and the new roads | Fort Kessler | Each a few mm apart |
| Causeway road and service road over the frontage road | Airport | Raised 6–12 mm |
| Pool terraces level with the house plinths | Silver Lake Estates | Raised 2 cm |
| Rooftop pool water 5 mm above its deck | Skyscrapers | 1.5 cm |
| Main road, bridge link, loop road and pavements | Coral Key | Now 0.07 / 0.078 / 0.088 / 0.1 |
| Crop rows running across the farm road; bales on the road | Farm | Rows break at roads, no bales on roads |
| Beach ground 2 cm under the street plane near the shore | City coast | 5 cm |

There were no duplicate props (trees, lamps, benches and so on, all checked). Walls were scanned as well; what turned up there were back-to-back faces, which you can't see.

## 2r. Latest update (build 42): no arrests through floors, no doorway dip, the right house's window

- **Arrests and melee respect floors.** A cop only "touches" you (the arrest bar) or tackles you when he's within 1.6 m of your height. Punches, kicks and tackles (`standingInFront`, `kickHit`) skip anyone more than 1.4 m above or below. A cop downstairs can't arrest you upstairs. Tested: 3.5 s with a cop directly below, no arrest; on the same floor, busted after about 2 s as before.
- **The doorway dip.** On sloped lots a home's floor sits level with its highest corner, but the 0.3 m door frame belonged to neither the room nor the yard. Every step through the door dropped you to ground height for a moment. Many porches also floated up to 1 m above the path with no steps.
  - Every home now has a stoop zone (`buildStoops`, `stoopAt`, checked in `groundY` after interiors). It's flat from inside the door frame across the porch, then ramps down to the path.
  - Where the rise is over 14 cm, there are real concrete steps and a plinth under the porch slab.
  - Yard trees are kept off the front steps (`clearDoorways` now includes home doors).
  - Tested on all 1,801 homes: no dips through any doorway.
- **Back-to-back houses.** Houses were shifted 1.2 m toward their back gardens, which left about 1.8 m between neighbours' back walls. Breaking in at the back often grabbed the neighbour's window, the nearest one, and set their house off.
  - The shift is now 0.3 m, so the gap is at least 2.9 m (median 4.5 m).
  - `nearWin()` now prefers the window you're facing, and your current house's windows from inside.

## 2q. Latest update (build 41): map sections you can switch off, the mayor's house marked

- **Mayor's house:** always on the map (gold star, labelled "Mayor's house") while Brenner is alive, not only during his contract. It glows at night once you've taken the job. Victor Hale's house is marked too ("VH", it glows while his contract is on).
- **Sections:** the map key is split into six sections, each with an on/off switch, plus Show all and Hide all buttons:
  - You
  - Jobs & targets
  - Crime
  - Shops & services
  - Landmarks
  - Out of town

  Switching a section off hides its icons on the big map, the minimap and the hover tooltips. The choice is saved (`sprawl.mapcats`). Every place type is now in the key, each with its name and a one-line description. Before, City Hall, the library, fire station, school, church, gas station, supermarket, Cedar Falls, the marinas, the mayor, delivery trucks and the contract target were missing.
- **No shared symbols:** every icon is now distinct:

  | Place | Icon |
  |---|---|
  | City Hall | CH |
  | Library | Lb |
  | Fire station | Fi |
  | School | Sc |
  | Supermarket | Mk |
  | Gas station | Gs |
  | Cemetery | Cm |
  | Cedar Falls | CF |
  | Marina | Ma |
  | Fire lookout | Lk |
  | Plane wreck | Wk |
  | Campsite | Cp |
  | Hollis's strongbox | S$ |
  | Fort Kessler | FK |
  | Contract target | X |

  Two-letter icons use a smaller font.

## 2p. Latest update (build 40): readable controls, gloves on/off, utility panel, a cleaner phone

**Controls menu (pause):** the controls are now five cards: Movement, Combat, Driving, Crime & utility and Interface.
- Each action has a plain name and, where useful, a one-line hint (e.g. "Crouch: sneak, take cover, slide while sprinting").
- To change a key, click it and press the new key. Esc cancels, and a key that's already taken swaps with the old one.
- Keys you can't change (mouse buttons, 1–9, Esc) show in grey. Nitro and handbrake show whatever sprint and jump are bound to. Arrow-key alternatives are listed under their actions.

**Start screen:** shows the same groups as a compact three-column sheet, plus a short line of tips about moves, lifts and shops.

**New keys:**
- **O: gloves on / off.** With gloves off you leave prints again. Without gloves it tells you where to buy them. `hasGloves()` now respects `player.glovesOff`.
- **I (hold): Utility panel.** Shows gloves (on / off / none), body bags, grenades, mask, armour, plus the bank keycard and the briefcase when you have them.

**Phone:** a full restyle, with no emoji anywhere.
- **Look:** a status bar (time, SPRAWL TEL, battery), a big title with a Close button, cards with readable 14 px text, and line-icon tabs with an unread badge. A keyboard hint sits at the bottom.
- **Messages:** show a coloured initial avatar for each sender, and a blue dot until read.
- **Contracts:** show the reward in green, a status chip (Open / Active / Lie low first / Done) and one clear button. The bank prep is a checklist with real checkboxes.
- **New-message pop-up:** avatar, NEW MESSAGE label, sender, text, and "Press T to read". Opening the phone clears it.

**Emoji removed elsewhere:** from notifications (the rally, the shop hold-up), from a shopper's "call 911" line, and from four map icons. City Hall is now H, Fire station F, Supermarket S and Cedar Falls C.

## 2o. Latest update (build 39): inside the airport terminal

The terminal used to be a solid glass block. It's now a hall you can walk into through two sets of sliding doors on the street side, with people in it. The airside glass, the side walls and the security screen all block you. The floor sits at its own height (`groundY` now checks interiors south of the city as well as west of it).

What's inside, east to west:
- **Check-in hall:**
  - three airline desks with lit signs and staff
  - queue posts and belts with travellers holding suitcases
  - a baggage belt behind the desks
  - a hanging DEPARTURES board
  - an information desk with an attendant
  - a row of seats by the front glass
- **Security:** a glass screen across the hall (x = -185) with three lanes. Each lane has a walk-through scanner, an x-ray belt with trays, two officers and a short queue.
- **Gate lounge:**
  - rows of seats at gates 1 and 2, with people waiting
  - gate desks with staff and a passenger or two
  - people at the window watching the planes
  - three kiosks along the street glass (coffee, news, duty free), each with staff and customers
  - café tables at the west end
  - planters and a gates board
- **Walking:** travellers wheel bags up and down the concourse and through the check-in hall.

**Starter kit when playing from the file:** the first time the game opens straight from `index.html` (a `file://` address, whose saves are separate from localhost's), it hands over $5,000, a pistol, shotgun and sniper rifle (each with a full magazine and 40 spare rounds), 6 grenades, gloves and 6 body bags. It only ever adds, never takes away, and it happens once (`sprawl.fileKit`). Adding `?starterkit` to the address does the same on localhost.

**How the people work** (`TERM.slots`, `updateTerminal()`): each seat, queue spot, desk and walking route is a slot. A slot fills with a person once you're within 110 m. People are removed in the normal way past 125 m. A slot whose person died or left refills after 90 s, out of your sight. Expect about 70 people inside when you're close. Seated people use the bench sit pose; queues and staff stand idle facing their desk. Everyone still reacts to trouble like any other pedestrian.

## 2n. Latest update (build 38): full-map detail and glitch pass

I flew the camera over every region (downtown, residential, Southpoint, the port, the beach and pier, Coral Key, the airport, Pinewood, the farm, Silver Lake Estates, Fort Kessler, Cedar Falls) by day and by night, and fixed what looked wrong or empty.

**Glitches fixed:**
- **Sandbar at sea.** A flat sand strip floated just past the beach all the way round the city. The beach mesh was built before the outer heightmap existed, so its outer 30 m sat at y≈0, above the water. It is now built after the mountains, and the beach shades cleanly into the sea.
- **Pinewood on a mesa.** The town sat on a 40 m plateau with cliffs. Roads can now climb a 13% grade (was 8.5%), and flat pads blend into the land over a wider radius.
- **Milky distance.** Fog closed fully at 720 m and washed the hills white. It is now pushed out (1300 m and more as you climb, 2200 m in the open), starts at 30% of that, and is a slightly bluer haze (0xb4c4d3).
- **Black lawns and hedges.** Any grass piece given a green tint went near-black, because the grass texture is already green and the tint multiplied it again. Tinted grass is now lightened automatically (very dark tints, like scorched ground, are left alone). This fixed the estate lawns and hedges.
- **Stepped estate lawns.** The lawns and inner roads were 24 m tiles, each at its own height. They now follow the slope.
- **Grass through paving.** Grass blades no longer grow inside Fort Kessler, where they came up through the roads and aprons.

**Fort Kessler, filled in** (`baseDetail()`). It was a 660×480 m lawn with a few sheds. It now has:
- **Roads:** a main avenue from the gate, with cross roads, kerb lines and centre dashes.
- **Barracks:** 8 two-storey blocks with porches, roof plant, building numbers, walkways and trees.
- **Parade ground:** painted grid, reviewing stand and a row of flags.
- **Mess hall and PT field:** the dining facility, plus an obstacle course with walls, bars and tyres.
- **Motor pool:** rows of trucks and jeeps, a maintenance shed with tool chests, and a fuel point.
- **Firing range:** a covered firing line, lane lines, distance boards, targets and an earth berm.
- **Aircraft:** static fighter jets on the flight line. The flyable jet, attack helicopter and helicopter stay where they were.
- **Around the base:** a water tower, floodlight masts, a chicane of Jersey barriers at the gate, sandbagged posts and netted supply stacks.
- **HQ:** a staff car park and jeeps in the motor bays.
- **Grounds:** mowing stripes that stop at the paving, and tree lines inside the fence.

**Sprawl International** (`airportDetail()`):
- **Gates:** ground crews at the two occupied gates (tug and baggage carts, belt loader, fuel bowser, stair truck, cones), and cones round the empty stand.
- **Apron:** equipment parked along the back.
- **Light aircraft:** two static props tied down past the hangars.
- **Airfield:** runway and taxiway edge lights, taxiway signs, an ILS glide-slope mast and a localizer array.
- **Terminal roof:** skylights and air-handling units.
- **Landside:** a long-stay car park with about 70 parked cars, a planted median, lamps and trees, plus a monument sign at the causeway.

**Cedar Falls** (`cedarDetail()`):
- **Back yards:** fenced yards behind the Main Street houses, with sheds, vegetable beds and maples.
- **Church:** a white church with a steeple and a small graveyard at the top of Hill Street.
- **Hay field:** stubble, windrows, round bales and a split-rail fence.
- **Woods:** the pines now come right up to the town (they used to stop at a 210 m circle).

**Hollis Farms** (`farmDetail()`): crop rows in every field, hedgerows along the lanes with gaps for the gates, bales on the stubble fields, hedgerow trees, and a tractor in the field next to the yard.

**Silver Lake Estates:** hedges between the lots, trees along the back walls and the lot sides, and lamps along the drive.

**Rooftops:**
- **Towers you can't enter:** more roof plant, a stair and lift housing, and vent stacks. Some tall glass towers get a helipad, and the tallest a stepped crown with a mast.
- **Towers you can walk onto:** keep clear roofs, so the stair hut and the walkable area aren't blocked.

**Shared scenery kit:** `SCN` holds static vehicles merged into the chunk meshes: sedan, baggage tug, cart, belt loader, fuel bowser, stair truck, cone, and a static plane wrapper around `planeMesh`.

**Known, not new:** about 175 THREE "bounding sphere is NaN" warnings print once at load. They happened before this build too. None of the affected geometry stays in the scene, and nothing visible is wrong.

## 2m. Latest update (build 37): the phone, contracts, casing the bank, the city's day, city services

**The phone (T):** it slides up from the bottom right and frees the mouse. Escape or T puts it away. 1–4 switch apps:
- **Messages:** texts from V. (your fixer) and the bank-job contact, with an unread badge. New texts also pop a toast.
- **Contracts:** what's on offer, the active one, and the bank prep checklist.
- **Jobs:** the old odd jobs (cars, hits, couriers), with Find work and Abandon.
- **News:** every SPRAWL NEWS headline.

Your weapons don't fire and the camera doesn't turn while it's out.

**Contracts:** one active at a time, taken whenever you like. The target shows on the map (✖) and the GPS routes to it. "Walk away" drops a contract for a couple of minutes. Payment arrives about 12 s after the job is done.
- **Mayor Brenner, $25,000:**
  - **Night:** asleep on his sofa at home, with two yard guards.
  - **Day (9 to 5):** on the City Hall plaza with two bodyguards (SMG and pistol). He flees if threatened.
  - **Rally:** once a day, around 13:00 while the contract is active, he holds a rally (V. texts you).
  - **News:** daytime and rally kills hit the news immediately; a night kill in the morning.
- **Victor Hale, banker, $9,000:** at a rich house well away from the mayor. Asleep after ten; otherwise awake with a pistol, and he draws it.
- **The Cedar Falls witness, $12,000:** Danny Price, outside the Riverside Diner by day and on the red footbridge in the evening, with an armed marshal. He runs if threatened.
- **Fort Kessler briefcase, $18,000:** on a table among crates in the base. Walk over it to take it, then bring it to the drop behind the Cedar Falls hardware store. Dying loses it.
- **The gold car, $7,000:** a gold supercar on a drive at Silver Lake Estates, delivered intact to the chop shop.

**Casing the bank** (the checklist is in the phone):
- **Case the floor:** about 8 s inside during opening hours, with your gun away and no stars. The vault drill won't jam.
- **The manager's keycard:**
  - **His walk:** he leaves at five and walks to his car.
  - **Getting it:** crouch up behind him and press E, or put him down. The vault then opens with a 1.2 s swipe instead of the 45 s drill.
- **The alarm box:** on the bank's side wall, with a green light. After dark, hold E for 3 s. The next silent alarm is held back 60 s.

**The city's day:** crowd and traffic sizes follow the clock.
- **Night:** about a third.
- **Morning commute (7–9:30):** commuters walk faster and traffic is up a third.
- **Lunch (12–14):** busier pavements, with more people at food carts, shops and benches.
- **After work (16:30–18:30):** half again as much traffic, driving a little slower, so it jams.
- **Late night:**
  - **Bars:** clubbers in groups outside them, some drunk.
  - **Traffic:** taxis make up nearly a third of it, and garbage trucks crawl the streets from 1 to 6. No buses or delivery trucks after dark.

**City services**
- **Wrecks:** a wreck in the street brings a red fire truck. Two firefighters hose it down, then a yellow tow truck hooks it up and hauls it off. Tested: truck arrives in 2 s, hosed by 17 s, towed by 53 s.
- **Road crews:** seven work zones around the city, each with cones, a fresh tarmac patch, an open manhole, a lit barrier and two workers.

**Detail**
- **City Hall:** a fountain with spray, three flags, planters and benches on the plaza.
- **The mayor's house:** a hedge round the grounds, lamps glowing on the lawn, and lit stone gateposts on the drive.
- **Cedar Falls:**
  - **Houses:** every one gets a porch light, a mailbox and most a white picket fence.
  - **Main Street:** puddles and a covered bus shelter.
  - **The river:** drifting mist.

**Cost:** at rush hour (76 cars, 210 people) the simulation takes about 4.7 ms a frame and drawing about 7.5 ms.

## 2l. Update (build 36): an audit pass, the news, gloves and prints, the Brenner contract, Cedar Falls

**Audit fixes:** a read-only audit agent went through the animations, mechanics and AI. Applied:
- **Traffic:**
  - **Reversing:** a timer name was shared by the gridlock relief and the "can't move, back up" logic, so cars reversed at full lock after every red light. Renamed.
  - **Red lights:** cars crept through on red; now they stop at the line.
  - **Parked cars:** kerbside cars were placed 5.0 m from the centre, inside the lane; moved to 5.5 m.
  - **Panic:** traffic panic after gunshots now wears off in 10–16 s.
  - **People ahead:** cars ease off early for someone in the road, but ignore people standing on the pavement.
- **Pedestrians:**
  - **Crossing:** they look both ways properly (the car's path, not one point; turning cars count) and give up after 20 s rather than stepping into traffic.
  - **Fleeing:** they never flee into moving traffic, and get off the road if they're on it.
  - **Obstacles:** they step round kerb clutter on the pavement side.
  - **Carjack victims:** can no longer be left frozen half out of the door.
  - **Gunmen:** can't get stuck forever mid-reload.
  - **Hiders and watchers:** nobody hides behind traffic that's about to drive off, or watches a fight from the road.
  - **Bus boarders:** come from the kerb side.
- **Animation:**
  - **Fireman's carry:** belly over your right shoulder, torso and arms down your back, legs down your front. The body no longer passes through your chest, and your right arm wraps the legs.
  - **Body bag:** rides on your shoulder, not through your head.
  - **Shove:** the lean no longer builds up.
  - **Waking up:** waking from a knockout no longer flips the body over.
  - **Heads:** fleeing people no longer turn their heads 120°.
  - **Searchlight:** the helicopter searchlight cone had been swallowed by a comment (the same kind of bug as last build); it's back.
- **Controls:**
  - **F:** next to a car, F gets you in the car instead of hailing a bus.
  - **E:** at a door, lift, case or stair door, E no longer also holds someone up.
  - **Parachute:** a parachute landing on water floats.
- **Measured:** traffic averages 19 km/h through the lights with nothing stuck over 30 s (longest wait 11.5 s) and almost no mid-road stops. One pedestrian died to traffic in a minute.

**SPRAWL NEWS:** a ticker slides down at the top when the city finds out. It covers:
- bodies found ("Body found: Point St, Downtown. Police are treating the death as murder.")
- forensics results
- the mayor

**Gloves and fingerprints**
- **Buying them:** leather gloves cost $150 at the gun shop. The knife and bat are now one item ($140). Gloves show on your hands and are saved with your gear.
- **Without them:** anyone you kill bare-handed carries your prints. When the body is found, police match them 45–80 s later: a news line, then wanted stars. Bodies that are never found (bagged, sunk, in a trunk) tell nobody anything.

**The Brenner contract**
- **The house:** the biggest rich house in the north of the city is the mayor's residence, with a flag out front and a black SUV in the drive.
- **The offer:** the first evening (after 19:30, while you're not wanted), a text arrives: $25,000 if he doesn't wake up. The house goes on the map (★).
- **At night:**
  - **Brenner:** asleep on the sofa. Only a gunshot (not a suppressed one) wakes him, or the house being alerted.
  - **Guards:** two armed guards walk a loop round the yard. Their sight range is 16 m, 11 m in the dark and 6 m if you're crouched. If they see you they draw and shout.
  - **If he wakes:** he runs, yells for security and calls it in.
- **Afterwards:**
  - **Discovery:** the body is found in the morning (from 7:00, or sooner if someone finds it).
  - **The news:** "BREAKING: Mayor Brenner found dead at his home…", then an investigation update depending on how you did it: prints recovered, "no witnesses, no prints, a professional", or an appeal for witnesses.
  - **Payout:** $25,000 arrives about 20 s after the news. Prints left mean wanted stars 30 s later.

**Cedar Falls:** a damp autumn mill town across the bay.
- **Getting there:** a new road leaves the Kessler Highway at the city's west edge and runs south past Silver Lake and round the bay.
- **Main Street:** level, with a general store, a diner, a post office and a hardware store, clapboard houses with porches and lit windows (grey-blue, white, sage, charcoal, cream), red, orange and gold maples, street lamps and dark cars at the kerb.
- **Hill Street:** climbs south with houses stepping up the slope.
- **The Cedar River:**
  - **Course:** comes down from the hills east of town (11 m down to sea level) in a carved channel with rocky banks.
  - **Footbridge:** a red steel through-truss footbridge you can walk across.
  - **Under the hood:** the river has its own water level, so it bakes into the water shading, swimming and the map.
- **Weather:** the valley keeps its own: low cloud and drizzle within about 400 m.
- **Locals:** walk Main Street.
- **On the map:** 🍁 and a label. Location names: Main Street, Hill Street, Cedar River, Cedar Valley.

**Cost:** load about 6.5 s. In the city, the simulation is about 1.7 ms a frame and drawing about 6 ms.

## 2k. Update (build 35): stairs without the stairwell, lane-keeping traffic, pedestrians off the road, keys

**Keys:** bodies now have their own keys: **J** carry / drop / trunk and **U** body bag (both rebindable). R used to reload and bag a body in the same press, and E picked bodies up as well as robbing, buying, lifts and trunks. The controls screen now lists shove, bodies, boats, buses, the taxi hail and the lift panel.

**Buildings: no more walking the stairwell.** The cramped shaft, the camera squeezed in it and the roof geometry clipping in all came from walking up the flights. Now:
- **Floors:** on every floor, the green stair door is a prompt: E opens the floor panel (0–9, = for the top floor, R for the roof).
- **The climb:** the screen fades with footsteps, longer for more floors, and you come out at that floor's stair door facing into the room.
- **Roof:** the roof hut has the same panel ("Stairs down"). You can't walk into the stairwell any more. Lifts work as before.
- **Tested:** lobby → floor 2 → roof → lobby.

**Traffic**
- **Lane keeping:** cars steered straight at a point 8 m before the next junction, so after a turn they came in at an angle and drifted up to 1.9 m into the parking lane. They now aim 8 m ahead on the lane line itself. Measured: stops caused by parked cars fell from 153 to 69 samples a minute.
- **Parking bays:** moved 0.2 m nearer the kerb, clear of the lane.
- **Abandoned cars:** any car left sitting in a traffic lane (a driver who bailed, a wreck) for over 24 s is removed once it's out of sight.
- **Buses:**
  - **Stops:** pull right in to the kerb, skip a shelter whose kerb is taken by parked cars, and dwell 5 s (7 with you aboard).
  - **Waiting for you:** they hold up to 6 s for you only if you're walking up within 6 m (it was 14 s whenever you were within 9 m, which looked like a bus stuck in the road).

**Pedestrians**
- **Off the kerb:** someone who drifts off the kerb outside a crossing (not counting the corners) walks straight back onto the pavement.
- **No road huddles:** chat groups never form in the road, and a chat breaks up if anyone's standing in it.
- **Fleeing:** fleeing people treat the road as a last resort.
- **Kerb waits:** at most 5 s before crossing anyway, down from 12.
- **Measured:** 1.6% of pedestrian samples were off the kerb and not on a crossing, nearly all a step across a rounded street corner.
- **Distant people:** they're fully animated out to about 65 m (was 40). Beyond 40 m they had been static stand-ins sliding along, which read as people freezing.

**Bug found:** a comment typed on the same line in build 29 had swallowed the code that stands a character upright after a ragdoll, so people who got back up could stay tilted. Fixed.

## 2j. Update (build 34): the city inside the land, a real airport, civic buildings, buses that work, shoves and windows

**The land, like the reference image:** the countryside heightmap now runs east to x = 640, and the coastline wraps round the city.
- **South:** a wooded shore across a bay about 250 m wide, tapering to a headland in the east.
- **North:** across a strait, the plain the airport sits on.
- **East:** the coast stays open (the harbour, Coral Key).
- **Under the city:** the city area itself is masked out of the country mesh. The new seabed follows the city's shelf, so there's no seam.
- **New land:** gets rolling hills that rise away from the water and ease down to the airport plain, about 21,000 pines (up from 15,000), and grass.

**Airport (smaller, tucked into the north shore):**
- **Size:** 760 × 320 m with a 680 m runway, down from 940 × 450 m with an 880 m one.
- **Airside:**
  - **Runway and taxiway:** a runway with piano keys and touchdown marks, a parallel taxiway with a yellow centre line and links.
  - **Apron and terminal:** an apron with three gates and lead-in lines, and a glass terminal under a flat roof with a canopy and jet bridges. Airliners sit at two gates; the third is for the scheduled one.
  - **Buildings:** a control tower, three hangars, a fuel farm and a windsock.
- **Landside:** a frontage road and departures pavement, a car park with bays, a hotel, a cargo office and a rental office.
- **Fence:**
  - **The barrier:** airside is fenced all round (posts, chain link, barbed wire, too tall to vault). The only gap is the service gate, with a guard booth, a guard and a red-and-white boom.
  - **Crashing the gate:** ramming the boom raises it and gives 2 stars ("security breach").
  - **Trespassing:** being airside on foot or in a car gets a "restricted area" warning, then a star after 8 s.
- **Vehicles:** taxis and vans loop the frontage road, and tugs and trucks drive the apron loop (measured: all 11 moving).
- **The airliner:** the scheduled airliner lands, taxis to gate 3, waits and takes off again on the new layout (tested end to end).
- **Causeway:** now just spans the strait and meets the airport road.

**Civic buildings:** 17 civic blocks are placed on free blocks in the right districts, spread apart, each with a map icon:
- **City hall:** steps, a six-column portico, a pediment, a green copper dome, a flag.
- **Library:** a portico.
- **Fire stations (3):** red bay doors, a hose tower, a fire truck and an ambulance out front.
- **Schools (3):** an L-shaped building, a fenced yard with a marked court and hoops, a yellow school bus.
- **Churches (3):** a nave with a pitched roof, a bell tower with spire and gold cross, a few old graves.
- **Gas stations (4):** a canopy with a red band and lights, pumps on islands, a kiosk and a price sign.
- **Supermarkets (2):** a big store with a sign and awning, a car park with bays, a cart corral.

**Buses**
- **Gridlock:** buses (and all traffic) jammed in junctions waiting on each other. Now any vehicle stuck for 8 s stops giving way and creeps through; one stuck 14 s out of sight is removed. Measured: buses stuck 1–7 s per 45 s instead of 40 s per 60 s.
- **Stops:** no more random stops in the road, only at shelters (or when you've rung), with a gentler pull-in.
- **Waving one down:** at a shelter, or with a bus coming within 35 m and no car beside you, F flags it down. It pulls up beside you (about 4 s in the test). The prompt tells you when one is coming. There are a few more buses in traffic.

**Buildings**
- **Rooftop camera:** on a roof, the camera used to test the building's own footprint as a wall and slam in. It no longer does (3.8 m boom on the roof, tested).
- **Lift panel:** E in the lift opens a panel. Press 0–9 for any floor (= for the top one), or R for the roof: you come out of the hut onto the roof.
- **Stairwell camera:** 80° field of view and the shoulder offset centred, so it isn't cramped.

**Shove and windows**
- **Shove (Y):** palms out. It shoves whoever is in front (harder at a run). They stumble or fall, and may square up for a fight or tell you off.
- **Through the window:** anyone shoved, kicked or knocked hard into an outside wall on a tower's upper floor breaks the window. Glass sprays, the pane is left as a dark hole, and they fall to the street, dead on impact from over 5 m. Every body part is first set just outside the glass at a sane speed: starting inside the wall had popped them out at 140 m/s.

**Ragdolls:** run on a fixed 120 Hz step (two even steps a frame at 60 fps) instead of the frame time, with one more solver pass and damping and friction rescaled to match. They fall and settle smoothly instead of jittering.

**Vaulting:** a proper side vault: crouch and reach, a hand planted on the rail, the body swung sideways with the legs tucked, and a knee bend on landing.

**Aircraft models**
- **Helicopter:** a teardrop cabin, a canopy wrapped round the nose, side windows, an engine cowl, a tapered boom, a swept fin and tailplane, five tapered blades with yellow tips, skids on cross tubes. The attack variant adds stub wings, rocket pods and a chin gun.
- **Prop plane:** a high-wing four-seater with a shaped fuselage, painted cowling and spinner, cabin windows, tapered wings with struts and red tips, wheel spats and a two-blade prop.
- **Fighter:** a shaped fuselage and radome, a bubble canopy, a delta wing, twin canted fins, stabilators, intakes, wingtip missiles and nozzles.

**Cost:** load is about 6.5 s. In the city, the simulation is 0.9 ms a frame and drawing about 5 ms.

## 2i. Update (build 33): a rebuilt map, a proper beach, jetties you can stand on, doors that stay in the wall

**Marinas**
- **Standing on the jetty:** walkable decks were only checked outside the city's street grid, so Eastside Harbor (just inside it) had no floor and you fell through. Marina decks are now their own list, checked first by the ground-height lookup everywhere (one box test per marina).
- **The boats:** they were tied up facing the shore, between finger piers, in water that's shallow all along the beach. Now:
  - **Layout:** the jetty runs out until there's about 3 m of water under its end (50 m for both sea marinas), finishing in a wide platform with bollards, posts and finger piers along the way.
  - **Moorings:** five boats (two on Silver Lake) are tied along the platform's seaward face, bows out. Step off the platform, press F and drive straight out. Pilings now reach the seabed.
  - **Tested:** standing on all three jetties, then boarding a boat from each and driving 44–105 m out in 5–6 s.

**Doors:** tower lobby doors used to slide out across the front of the building, in front of the facade. Their panels now sit in the middle of the wall and slide into it, like the shop doors.

**The beach (3D)**
- **Sand:** finer ground mesh (3.5 m). Dry sand drifts between two tones and has a wind-ripple texture. It turns damp, then wet, toward the waterline, with a broken line of seaweed at the high-water mark and dune grass creeping in at the top.
- **Under the water:** the seabed is pale sand under the shallows and darker further out, seen through the clear shallow water.
- **Dune grass:** about 9,000 wind-blown clumps along the top of the beach, kept off the streets, jetties and buildings.
- **Lifeguard towers:** red huts on white stilts with a flag and steps, about every 230 m, facing the sea.
- **Seabed seam:** the seabed dropped to −7.7 m inside the city square but sat at −6 m outside it, with a cliff at the edge. It now levels out at −6 m on both sides and carries the city's shelf outward, so the water colour (3D and map) no longer shows a rectangle around the city.

**The map, rebuilt**
- **One terrain pass:** a single pass over the real terrain for the whole world (0.85 s at load), instead of mountain shading plus flat-colour shapes:
  - **Water:** coloured by real depth, like the 3D sea: turquoise shallows, teal, then deep navy, with a light surf line. Lakes are a little greener.
  - **Shore and slopes:** sand at the shore, wet at the waterline. Meadows, forest canopy, rock on steep ground, an alpine band and snow on the peaks blend softly.
  - **Hill shading:** slopes are measured over the heightmap's own 7 m spacing, so there are no stair-steps along roads and shores.
- **Coral Key and the airport:** now take their shape from the terrain instead of hand-drawn blobs.
- **Buildings and roads:** every building outside the city (Pinewood, Fort Kessler, the farm, the estate, the airport) is drawn with its shadow. Roads have verges. The runway has markings.
- **Removed:** the clouds, and the pale "sea wall" outline that boxed the city into the sea.
- **Zoom:** a sharp re-render of exactly what you're looking at is drawn about 0.15 s after you stop zooming. Forest canopy, lake depth, roads and buildings stay crisp up close. The city's own detailed map still draws on top.

## 2h. Update (build 32): water that moves, boats and marinas, bodies that fly, doors, calmer pavements

**Bodies in the trunk:** a body in a trunk stayed where you loaded it instead of riding with the car. Once you drove off it was cleaned up as a far-away corpse, so taking it out grabbed a deleted body. It now rides along, hidden, with the car. Unloading skips anything no longer valid. Tested: loaded, drove 470 m, took it back out and carried it.

**Hit by a car:** the person takes the car's momentum and goes flying as a ragdoll. Measured: about 6 m at 40 km/h, 21 m at 60 km/h and 38 m at 90 km/h. Survivors lie knocked out for 5–9 s (longer the faster you were going), then get up.

**Pavements:** about half the clutter is gone.
- **Fewer items:**
  - **Meters:** 2 per side at 45%, down from 4 at 70%.
  - **Hydrants:** 28%, down from 50%.
  - **Bins:** 22%, down from 40%.
  - **Benches:** 30%, down from 50%.
  - **News boxes:** 15%, down from 35%.
  - **Phones:** 7%, down from 15%.
  - **Mailboxes:** 12%, down from 25%.
  - **Trees:** two per side (or one), down from three.
- **Knock it over:** what's left can be ploughed through. Meters, hydrants, bins, news boxes, mailboxes, phone booths, benches and sign posts fly off as debris and slow the car a little. A hydrant becomes a 14-second geyser.

**Doors:** every walk-in shop, bar and store (they were bare 2.4 m holes) now has a pair of framed glass doors. They slide into the wall when anyone comes within about 3 m. No street tree is planted within 3.6 m of any shop or tower doorway.

**Water:**
- **Shader:** the sea is a custom shader.
- **Swell:** five travelling waves, faded out near shore and in the distance, on a 1 km grid that follows the camera, with a flat far plane to the horizon.
- **Ripples:** two scrolling ripple layers.
- **Colour:** set by real depth, from a depth map baked at load (720 texels across the map, 58 ms). Turquoise shallows you can see the sand through, then teal, then deep blue.
- **Foam:** a broken, animated foam line at the shoreline, and the odd whitecap on crests offshore.
- **Lakes:** the same shader, calmer and greener.
- **Reflection:** sky reflection was turned down so the water doesn't wash out to white.

**Boats and marinas**
- **Marinas:**
  - **South Bay Marina:** on the south beach, west of the pier.
  - **Eastside Harbor:** on the east shore.
  - **Silver Lake Boats:** a small jetty on Silver Lake.
- **What's there:** each has a walkable jetty on pilings with finger piers, bollards, lamp posts, a harbour office with a sign, and a ⚓ on the map.
- **Boats:**
  - **Types:** speedboats, fishing boats and a cabin cruiser moored alongside.
  - **Taking one:** walk up and press the vehicle key. You stand at the helm with your hands on the wheel.
  - **Handling:** throttle and steer like a car, but they slide.
  - **On the water:** boats ride the same swell as the shader, pitch and roll, lift the bow at speed and leave a wake and bow spray.
  - **Limits:** they can't go into water under 0.55 m or through the jetties (they bounce off, hard hits do damage).
  - **Replacements:** a boat you take or wreck is replaced once you're 220 m away.
- **Offshore:** sailboats, a yacht and a fishing boat cruise slow loops in open water (only on loops that stay deep), bobbing, heeling and leaving wakes.

**Cost:** simulation 0.9 ms a frame; drawing about 5 ms in the city and on the coast.

## 2g. Update (build 31): smarter crowds, livelier gunfights, real buses, a steady camera indoors, markers back

**Map markers:** stores, bars, towers and the woods landmarks are full icons on the big map again at every zoom, not tiny dots. Small ones draw underneath, key places on top. The minimap shows markers a little beyond its edge, and key places from 1.1 km away.

**Camera inside towers:** the normal camera collision tested the building's interior walls, furniture and the floors above and below as flat 2D obstacles, so it could slam in to 0.6 m. A hard clamp then snapped it again. Now:
- Inside, the camera is a single boom that is shortened along its own line so it stays in the room (or the stairwell) and under the ceiling. It pulls in quickly and eases out slowly, and never re-aims.
- At the door the camera may trail out into the street, so walking in doesn't snap it.
- The boom is 2.6 m on floors and 1.7 m in the stairwell.
- Measured walking in and turning: the camera moves at most 0.18 m in a frame and never comes closer than 1.8 m.

**Buses**
- **Model:** a passenger window band with pillars and people in about half the seats, two sets of sliding glass doors on the kerb side, a lit route board (e.g. 12 DOWNTOWN), a roof air-con pod, mirrors and a rear grille.
- **Stops:** buses pull in at real shelters on their side of the road. They line up toward the kerb, stop with the front door level with the shelter, and hiss the doors open. A few people get off; people waiting at the stop walk to the door and board.
- **Riding:**
  - **Getting on:** stand by the open door and press the vehicle key ($2). The driver waits while you walk up.
  - **During the ride:** press the vehicle key while moving to request a stop, and the bus pulls over at the next safe spot or shelter.
  - **Getting off:** press the vehicle key at a stop to step off onto the pavement.

**Crowds**
- **Fleeing:** people choose among nine directions away from the threat. They avoid ones that run into a wall or car within 2 m, prefer the pavement to the road, and stick with their choice instead of zig-zagging.
- **Calming down:** they sprint, slow to a jog past 30 m and a walk past 50 m, glance back over their shoulder, then return to their day.
- **Panic spreads:** calm people within 7 m of someone running from a threat (within 45 m of it) react too.
- **Measured:** after gunfire in a busy street, 15 of 16 nearby people fled. Five seconds later they were 50–55 m away and easing back to walking, with none stuck.

**Gunfights**
- **Suppression:** rounds you fire that pass within 1.8 m of a gunman pin them. They shout ("Taking fire!", "I'm pinned!"), go for cover immediately, sometimes can't get a shot off, and their aim spreads up to about 2.4×. Being hit pins them too. Bystanders near a round's path panic.
- **Reloads:** every armed NPC has a real magazine (pistol 12, SMG 25, rifle 30, shotgun 6). When it runs dry they crouch for 1.6–3 s, often calling "Reloading!". That's your window.
- **Callouts:** when one falls, the others nearby shout "Man down!" / "Officer down!" and go for cover.
- **Flanking:** a gang crew of three or more sends its farthest gunman wide round your side ("Flank him!").
- **Grenades:** if you sit behind cover or stay put for 4 s, a gang member (or a cop at 3+ stars with a grenade at 4+) at 11–28 m may lob a grenade at you, aimed with a proper arc ("Frag out!"). At most one every 14–24 s.

**Your side of it**
- **Flinches:** NPCs flinch when shot: their torso jerks away from the hit and their next shot is delayed.
- **Streaks:** two kills within 3.5 s shows DOUBLE KILL, then TRIPLE KILL and RAMPAGE ×n (with a slow-motion beat from three).
- **Headshots:** a headshot kill gets a short hit-stop.
- **Clearing a crew:** dropping the last of a crew you were fighting (at least two kills in the fight) gives a one-second slow-motion beat and **CLEAR**.

**Characters**
- **Shadows:** everyone has a soft contact shadow under their feet, so they sit on the ground. It shrinks while jumping, and bodies get a larger one.
- **Faces:** faces are drawn at double resolution (sharper eyes, brows, lips).
- **Heads:** heads are shaped like a skull rather than an egg: flatter temples, a brow ridge, cheekbones, a jaw that narrows to the chin, and a tucked nape.
- **Hair:** hair has a strand texture and a soft sheen.
- **Hands:** hands have four fingers and a thumb instead of a block.

**Cost:** the simulation runs about 2.5 ms a frame in the city with roughly 200 people.

## 2f. Update (build 30): grass you can walk through, a cleaner map

**3D grass:** wind-swept grass tufts now cover the countryside (Kessler Range, foothills, meadows, the cemetery and the woods sites).
- **What you see:** about 4,000–5,500 tufts within 42 m of the camera. Each is seven curved blades, dark at the root and light at the tip.
- **Wind:** blades sway in the vertex shader, with slow gusts rolling across the field.
- **Variety:** thick meadows and thinner worn patches, colour that follows the terrain (lush, dry, deeper green higher up) and the odd wildflower in yellow, white or violet.
- **Where it doesn't grow:** roads, water and lake shores, farm crops, the estate, steep rock, above 182 m, and anywhere with a floor or deck.
- **Placement:** tufts sit on a fixed jittered grid, so they don't shuffle when the field is rebuilt. It's rebuilt when you move 9 m (about 2 ms), drawn as one instanced mesh, and hidden in the city and high up in the helicopter. Measured cost: about 1.5 ms a frame.

**Ground textures:** lawns and parks use a painted blade texture instead of a flat speckle. The terrain detail texture has blade streaks and clumps.

**Big map**
- **Snow:** now starts at about 224 m (in 3D too) and is a softer white that no longer blows out, so only the high ridges are white.
- **Labels:** the Pinewood Cemetery label sits beside its icon instead of on top of the Pinewood label.

## 2e. Update (build 29): a satellite-style map, the outskirts filled in, fixes

**The big map, drawn like a satellite photo**
- **Relief:** terrain is hill-shaded from the actual heights, lit from the north-west.
- **Forest:** a two-scale noise mask (the same one that places the 3D pines) shows the stands, with a tree-by-tree canopy texture.
- **Ground:** deeper meadow greens, rock on steep slopes, a grey alpine band above 140 m, and snow on the high peaks from about 210 m (with noise, not on cliffs).
- **Water:** lakes go from teal shallows to deep blue, with a light rim and sandy shores.
- **Clouds:** soft clouds drift over the map edges but are kept off the city.
- **New places:** Silver Lake Estates (walls, road, glass houses, pools) and Pinewood Cemetery (rows of graves) are drawn and labelled, with icons in the map key for every new site.
- **Speed:** heights are sampled once per pixel and reused for the shading, so building the map stays quick at load.

**The world to match:** the 3D snow line came down to about 210 m to match the map, and trees now grow up to 205 m. Pines rose from 12,000 to 15,000, in denser stands with fewer gaps.

**Silver Lake Estates** (gated community, south of Silver Lake)
- **Gate:** stone perimeter walls, a lit gate with pillars, a barrier arm, a guardhouse and the estate sign.
- **Inside:** lawns, an entrance road, and six two-storey glass houses on plinths that take up the slope, each with a terrace, pool, loungers, palms and a drive.
- **Cars:** a supercar, sports car, SUV or muscle car parked on each drive.

**Pinewood Cemetery** (just outside Pinewood)
- **Enclosure:** a wrought-iron fence on a stone footing, and a gated stone arch with the cemetery sign.
- **Graves:** about 60 in rows: rounded headstones, crosses and obelisks, some leaning, some with a candle.
- **Landmarks:** the Hollis family mausoleum (columns, pediment, iron door), crooked dead trees and lamp posts.

**In the woods:** placed away from roads, water, the town, the farm and the base, at least 160 m apart, in clearings the forest leaves for them:
- two fire lookout towers, 14 m with a cabin top and a ladder
- a light-plane wreck: broken fuselage, wing, tail and scattered debris on scorched ground
- a ring of nine standing stones on a hilltop, with lintels, an altar and candles
- two hunters' cabins with a porch, woodpile, chimney and a pickup out front
- two campsites with tents, a stone fire ring with embers, and log seats

**Fixes**
- **"Glitching" black building:** this was the Diamond District jeweller, deliberately given a near-black facade, which rendered as a flat black slab in shadow. It's now warm stone.
- **Feet in the ground:** characters' soles sat about 5 cm under the surface; every character is lifted to match. Measured: 1 cm above.

## 2d. Update (build 28): body bags, trunks, suppressors, knives and bats, smoother frames

**Tools pocket:** a separate inventory from your guns, saved with your gear. It holds body bags; the HUD shows **BODY BAGS n** next to grenades.
- **Bagging:** stand by a body and press R. The body turns into a black bag that lies on the ground, or rides over your shoulder when you pick it up with E. Nobody "finds" a bag, so bagged bodies are never reported.
- **Trunks:** walk to the back of any stationary car you could take and press E to load what you're carrying. E at the back of a loaded car takes it out again. Getting in the car while carrying still loads the trunk too.

**Carrying a bare body:** a fireman's carry, with the hips on your right shoulder, head and arms down your front and legs down your back. Before, it folded inside your own torso.

**Gun shop (AMMO & ARMS):** 12 items on keys 1–9, 0, − and =, now including:
- a knife ($90)
- a baseball bat ($60)
- suppressors for your pistol, SMG and carbine ($750 for all three)
- body bags, three for $45
- grenades and armour, merged into one item
- **Suppressed shots:** a short soft pop instead of a bang, 15% of the muzzle flash, and no muzzle sprite. Only people within 6 m react (32 m otherwise). Traffic doesn't panic, there's no witness call from the shot itself, and neighbours don't hear it in houses. Hits are still hits: someone who sees you shoot a person still calls it in.

**Frame rate**
- **Shader stalls:** the stutters came from shaders compiling the first time something new appeared on screen. One cost 482 ms on the first frame, and later ones were 30–40 ms. At load, every kind of car, interior, glass, body-bag, livery and banner material is now drawn once off-screen through the full pipeline (shadows and post-processing included), and their textures are uploaded. Measured: the first frame dropped to 29 ms, and new parts of the city to 6–35 ms.
- **Steady load:** the existing dynamic resolution and quality shedding still handle that.

**Police helicopter:** its searchlight was 2,600 units with distance falloff, about 35× sunlight where it landed. It's now 160, about the same as car headlights.

## 2c. Update (build 27): walk-in buildings, saner pedestrians, you behind the wheel

**Buildings you walk into**
- **The doorway:** about 120 towers are now built as four walls with a real 2 × 2.6 m doorway on the street side, with a metal frame and a lit green sign. Glass doors slide open as you, or anyone, comes within a few metres, and you just walk in. There's no separate mode, camera or teleport. The old spiral stair mode is retired.
- **Inside:** a lobby with a desk, a security guard, plants and a bench. The stairwell is at the back through a green-signed door: real switchback flights you walk up, a landing halfway, and you come out on the next floor. A lift alcove sits next to it on every floor; E takes it up to the top floor, or down to the lobby from the top.
- **Floors:** offices (desks, monitors, chairs, filing, a water cooler, workers at desks), flats (sofa, TV, bed, kitchen, residents) or storage (racking, crates). Some have cash or valuables to take with E.
- **The roof:** the top flight comes out into a hut. Walk out onto the roof (base-jump off the edge, shoot from up there) and back into the hut for the stairs.
- **Loading:** a building's floors exist only while you're nearby. The lobby loads within 28 m of the door. Inside, only your floor and the ones directly above and below exist; they're built one per frame, so there's never a hitch, and thrown away (geometry freed, people removed) as you move on. Interiors are unlit vertex-coloured meshes (a few draw calls a floor), so they cost almost nothing to draw.
- **Shooting inside:** rounds stop at the building's walls and only hit people on your floor. The camera stays inside the walls and under the ceiling.

**Pedestrians:** they used to bolt about once a second somewhere nearby, because they "dodged" traffic that was never going to hit them. Turning cars looked like they were coming straight at people on the corner, and ordinary traffic brakes for pedestrians anyway. Now they only dodge you, police, panicking drivers and anything doing over 15 m/s. After a near miss they go back to walking, and only flee if it was you. Measured standing still for 30 s: from 27 people running down to 4.

**Driving a taken car:** the figure behind the wheel is redrawn in your clothes and skin. It was the person you pulled out.

**Ragdolls:** walls are checked on every solver pass, and each body part is pushed back out on the side it came from, so the solver can't drag a limb through. Measured: bodies thrown into a house wall at 10–30 m/s stayed inside every time.

**House doorways:** the frame on the back-room partition overlapped the wall ends by 8 cm and flickered. It now sits just inside the opening, with a head piece.

## 2b. Update (build 26): traffic that copes, bodies you can carry and hide, damage after death

**Traffic**
- **Stopping:** cars only count something as "in their lane" by the two vehicles' actual widths. A car parked at the kerb never counts, so buses no longer stop behind parked cars. Parking bays and delivery-truck stops moved out to 5.3 m from the road centre.
- **Passing:** stuck behind something parked, broken down or making a delivery, a car waits about 1.5 s and then pulls round it through the other lane. It only does that if the lane is clear for 40 m, nobody is near the obstruction, and it isn't within 20 m of a junction. Measured: 13 passes in 2 minutes.
- **No more ramming:** being blocked no longer turns into driving into the obstruction after 7 s. After 9 s they creep forward at 2 m/s instead.
- **Junctions:** before pulling in, a car predicts 2.4 s ahead (1.6 s while turning inside the junction) and gives way if it would meet another moving car. Turning gives way to straight on, AI gives way to you and to police, and between equals the slower one yields. The crashes we logged were turning cars cutting across buses.
- **Measured over 2 minutes with 50 cars:** 4 contacts over 3 m/s (damage starts at 6 m/s), and 1 car stopped for 15 s or more.

**Bodies**
- **Carrying:** E next to a body puts it over your shoulder; E again puts it down. You walk at 2.4 m/s (3.8 running) and can't aim or shoot while carrying.
  - Put it down in water and it sinks for good.
  - Get in a car while carrying and it goes in the trunk, hidden for good.
- **Discovery:** someone you kill is only reported when someone finds the body. That means a pedestrian within 14 m, a cop within 22 m, or a clerk, with a clear view and in the same room (so a body inside a house waits for someone to come in).
  - If they can also see you, it's a witness call (stars).
  - If not, it's "a body was found, nobody saw who did it": an ambulance comes, but no stars.

**Gore after death:** shooting a body keeps damaging it limb by limb until parts come off (sniper and close shotgun fastest). Cars running bodies over and explosions nearby do it too. With lock-on aiming on, RMB snaps to the nearest living target, so free-aim to shoot a body.

**Ragdolls:** every part of the body (not just pelvis, chest and head) is kept out of walls. A fast limb that would pass through a wall in a single step is stopped at the wall and bounces back.

**Getting into buildings**
- Stair doors now have a lit green **STAIRS** sign. The first time you pass within 12 m of one you get a hint.
- If a building's street side is blocked, the door goes on the next side round. That brought in downtown towers: 312 stairwells, 7 of them office towers.
- In stepped towers the stairs go up through the sections above to the very top. On a lower terrace roof, the section above is solid.
- Climbing speed scales with height in tall towers.
- Floor types: office towers have offices; brick and concrete buildings are two-thirds offices, one-third flats; warehouses have storage.

## 2a. Update (build 25): saved gear, a safe house, floors inside buildings

**Saved gear:** weapons, ammo, magazines, grenades, armour and your mask save to the browser (`sprawl.kit`) every 2 s and when you leave. The first load of this build returned your shotgun (30 rounds), sniper rifle (20) and a balaclava.

**Safe house:** the single-storey home nearest the starting point is yours. It has a green **H** on the map, and nobody else lives there: no alarm, no residents, nothing to steal.
- **Locker:** a gun locker sits in the front corner.
- **Healing:** you heal 12 HP a second inside.
- **Getting busted:** all your weapons, grenades and mask are confiscated and go into the locker (saved as `sprawl.locker`). The locker's light blinks amber and the map icon glows until you collect them with E. Getting wasted doesn't take anything.

**Floors:** stop at any landing in a stairwell and press E to go in. The floor is built only while you're on it, as a few merged meshes plus one moving light, and removed when you leave, so it costs nothing elsewhere.
- **Offices:** desks with monitors and chairs, filing cabinets, a water cooler, petty cash in some desks.
- **Flats:** sofa, TV, bed, kitchen, table, cash, and sometimes valuables for the fence.
- **Storage:** racking with boxes, crates, sometimes a box of stock.
- Window bands and ceiling lights. Loot taken stays taken until you reload. E at the stairwell door goes back out.

## 1z. Update (build 24): real hold-ups, events, stairwells to every roof, a clearer map

**Front doors** now swing outward onto the porch. Swinging inward, the first 27 cm went through the wall and the door could clip furniture by the entrance.

**24/7 stores**
- No more glowing ring to stand in. Each store has one to three customers queuing at the till and sometimes one browsing; more wander in now and then.
- Stand behind the last person to join the queue. At the front, **E** buys snacks ($6, +20 HP).
- Aim a gun inside (or fire, or hurt anyone) and it's a hold-up: you shout, customers drop to the floor, and the clerk puts their hands up and empties the till (about 7 s). Leave before it's done and you get nothing.
- Anyone you're not watching (within 12 m and about ±45° of where you're looking) may reach for a phone. You'll see them holding it with a 📱 bubble. Look at them and they drop it; leave them about 4.5 s and they get through to 911 (2 stars). The clerk edges toward the silent alarm the same way (1 star).
- If nobody called it in, the clerk calls 20 s after you leave.
- Measured: facing the door, a customer was on the phone within 0.8 s.

**Neighbours and witnesses**
- **Gunshots in a house:** a 50% chance a neighbour calls it in 6–12 s later. That's one star, so one patrol car comes. Measured: 4 of 8.
- **Break-ins:** picking a lock, smashing a window or climbing the drainpipe can be seen by people on the street. By day that's up to 22 m (less crouched); at dusk and night it's much less. Anyone facing you with a clear view, or within 6 m, may call the police.

**Events (every 6–9 minutes in the city; marked with a pink ! on the map)**
- **Rallies:** three speakers, each with their own banner, lines, crowd chants, security and reward:
  - Mayor Brenner: 4 guards, $2500
  - tech CEO Dana Vale: 3 guards, $3200
  - Councilman Ortiz: 2 guards, $1600
  - The setup: a stage in a park with a podium, mic, banner, flags, speakers and a velvet rope, 14 people in the crowd, armed security in black suits, and a black SUV waiting down the street.
- **VIPs:** someone important walking a city block with bodyguards keeping close (measured 2–3.5 m), guns hidden until trouble starts:
  - Don Carlo Ventresca, a mob boss, with 3 goons; carrying $4000 and a gold watch; draws his own pistol
  - Lux, a pop star, with 3 bodyguards; $2200 and jewellery
- **Starting trouble:** a shot nearby, hurting anyone in the group, or aiming a gun from within 20 m for more than about 1.6 s. Security shouts first, then opens fire, and you get 2 stars (1 for the mob boss). The crowd scatters. A speaker runs for the SUV and is driven off; shoot the driver through the glass to stop it. Take down the target and they drop a cash briefcase.

**Stairwells:** 276 proper buildings in the city now have a grey stair door on their street side.
- **Climbing:** inside is a spiral stair with a red fire door and a floor number on every landing and a green door at the top. W climbs, S goes down, Shift runs (25 m takes about 12 s); E at the top or bottom goes out.
- **The roof:** walk off the edge to base-jump; the stairs down are by the door.
- **Shooting from roofs:** your own building no longer blocks your aim or bullets. Measured: 3 of 4 targets hit from a 25 m roof. Cops within 70 m can see you up there and shoot back, and the helicopter fires at you on roofs too (not inside stairwells).

**Map**
- 24/7 stores use a small **24** icon and are dots until you zoom in, so the green **$** no longer covers the city. That's left for the cash truck and the stash.
- Car parks show a blue **P** and parking bays are outlined.
- District names (Downtown, Midtown, Port Sprawl, Northgate, Southpoint) appear once you zoom in a little; street names from 3× zoom.
- Live events are marked with a pink **!** and described in the map key and tooltip.

## 1y. Update (build 23): parking, homes with variety, people who walk round things

**Parking**
- **Parking lanes:** some streets have a painted lane along the kerb (a solid line 4 m from the centre and T-marks for bays). It's commonest on commercial streets (55%), then downtown (45%), residential (30%) and industrial (10%). The choice is fixed per street, so the city stays the same between sessions.
- **Car parks:** about 9% of plain commercial and downtown blocks (4% of residential ones) are now car parks. Each has two rows of marked bays, an aisle you can drive straight through with entrances off the roads on both sides, planted strips with trees and lamps, a pay booth and a blue P sign.
- **Parked cars:** these fill parking lanes, car parks and house driveways within about 115 m of you, and are cleared once you're 220 m away. Cars you've driven are left alone. This replaces the 165 cars that used to be parked at random across the whole map: total cars dropped from about 250 to about 130, with more of them near you.

**Delivery trucks** now pull in at the kerb mid-block, 17–21 m from the junction, well clear of the crossings. If someone's already parked there they shift 5 m along, or try again at the next block. The truck is 2.3 m wide (was 2.4) so it clears the traffic lane.

**Pedestrians** now steer round lamp posts, trees, hydrants, bins, meters, news boxes, phone boxes, post boxes, benches and stopped vehicles. They're pushed back out if they clip into one.

**Homes**
- **Fixed flicker:** the lawn under each residential block sat 2 cm above the house floors, so grass showed through and flickered in some homes. Rugs sat millimetres above the floor too. Both fixed.
- **Five roof styles:** side gable, front gable, hip, and flat with a parapet.
- **Three walls:** clapboard, brick or stucco.
- **Extras:** porches on posts, chimneys, an attached single garage with a driveway (sometimes with a car in it), and front hedges with gaps for the path and drive.
- **Few repeats:** the game re-rolls a house's look if the same roof-and-wall combination was used in the last three, so it almost never repeats along a street.
- **Big houses:** about one row in five is a single big house (16.5–18.5 m wide, mostly rich, mostly two storeys) across both plots.

## 1x. Update (build 22): saved cash, gore and limb damage, shooting into cars, calmer police, confrontations, more sound

**Saved cash:** your cash saves to the browser (localStorage `sprawl.cash`) every 2 s and when you leave the page. The first load starts at $3500. Add `?nosave` to the URL to play without touching the save; tests use it.

**Damage**
- **Car hits:** damage now grows with the square of the speed and the vehicle's weight. About 50 km/h hurts, 80 km/h and up is usually fatal, and trucks and buses hit harder. Survivors' legs are hurt, so they limp.
- **Limbs:** bullets know whether they hit an arm or a leg.
  - A badly hit leg makes someone limp, or fall.
  - A shot gun arm can make an NPC drop their weapon.
  - You limp and your aim shakes if you're hit, until it heals (about 4% a second).
- **Gore (on by default; toggle in Settings):** heads and limbs can come off and bounce, with blood spraying from the stump. The causes:
  - very hard car hits (rising chance above about 85 km/h, weighted by vehicle mass)
  - a sniper rifle or a close shotgun blast: to a limb that's already badly hurt, or to the head of someone already down
  - an explosion very close to them
- **Fists and kicks:** each blow varies ±25%, one in ten lands 1.6× harder, hits on someone already down do more, and heavy blows draw blood.

**Shooting into cars:** rounds through the glass can hit whoever's inside, more likely near the driver's seat, and three times as hard to the head.
- A dead driver slumps on the horn while the car rolls on, then coasts to a stop.
- A shot police car's partner bails out.
- A shot bike rider falls off.
- Take the car and the body comes out first.

**Police**
- **Driving:** chase speeds are now 15–30 m/s depending on stars (was up to 100% of top speed). They keep up with you, slow down for anyone in the road (reacting later in hotter chases), only PIT at 2+ stars and never with people within 12 m of you, and back off for 4–9 s after each attempt.
- **Shooting:** aim settles over about 1.3 s once they see you, widens with range, your movement, their own movement, and when you're shooting back. Each cop has their own skill. Rifles fire in bursts of 2–5. They hold fire if someone's in the line. Measured hit rate: about 17% of shots on a player standing still, 7% on one moving. The helicopter gunner misses more too.

**Bumping into people:** they may say something (45% walking into them, 85% sprinting). Some square up instead, more often if they're tough or street types, less often if you're armed. Stay in their face and they shove you, then start a fight. Walk off and they let it go. Draw a gun and they back down.

**People in cars:** the glass is lighter (50% opacity, was 80%). Drivers have a neck, eyes and a nose, and 30% of ordinary cars have a passenger.

**Delivery trucks** aren't on the map any more; they're part of the scenery.

**Sound (all synthesised):** footsteps (quieter crouched, softer indoors), landings, tyre squeal, a city hum and birds or crickets, car doors, bodies hitting cars, gore, bullets whizzing past and ricochets, reload clicks, shell casings, police radio chatter near officers, dogs barking, splashes, the knockout crack, and the delivery trucks' roll-up doors.

## 1w. Update (build 21): stealth crouch, delivery trucks, a gentler police searchlight

**Crouching (Z)**
- **New pose:** a proper sneak, leaning forward with hands up. Standing still, you drop to one knee. The camera lowers with you.
- **Stealth badge** above the minimap while crouched: green **HIDDEN**, blue **IN COVER**, red **SEEN** (someone within 16 m is looking your way with a clear view, or the cops can see you).
- **Hiding from police:** crouched, cops spot you at 70% of their normal range (28 m instead of 40 m). Down in cover behind a car or wall, they have to be within about 8 m.
- **Silent takedown:** crouch behind someone who hasn't noticed you (back turned, not fighting, fleeing or aiming) and press LMB.
  - With fists it's a 1.7 s chokehold that knocks them out.
  - With a knife it's a quick kill.
  - It only reaches the police if someone sees it. Crouched, witnesses have to be within 16 m.
  - Cops can be taken down too, but not while they can see you during a chase.

**Delivery trucks**
- **The truck:** a 7.4 m box truck in four invented liveries: ParcelPoint (parcels), FreshFare (groceries), VoltMart (boxed TVs, rare and worth the most) and Hopsworth (cases of beer). It has a roll-up back door with stacked boxes inside.
- **Deliveries:** trucks join traffic, and the game keeps about two near you in the city. Every 30–60 s one double-parks. The driver climbs out, rolls up the back door, carries two or three boxes to the kerb, then shuts up and drives on.
- **Stealing:** while the truck is parked, hold E at the back to take the cargo one load at a time (5–9 loads; 3–6 on a VoltMart). Everything sells to the fence.
  - Values: parcels $40–220, groceries $15–60, TVs $150–480, beer $30–110.
- **Getting caught:** the driver catches you if he's close or turns round and sees you (crouching makes that less likely). Tough drivers fight; the rest run and call the police. With a gun aimed at him, he gives up.
- **Taking the whole truck:** drive off in it, park up anywhere, and unload it the same way.
- **On the map:** they were marked with a **D** in build 21; since build 22 they're unmarked.

**Police helicopter**
- The searchlight has no shadows, so it used to light houses from inside through the roof. It's now off while you're indoors, and its beam is hidden too.
- Outside, it's about a third as bright as before. The beam fades when the camera is standing in it.
- A second cone that was always pointed at you, day and night, is gone.

## 1v. Update (build 20): a readable map, lived-in homes, police who have to come in

**Map (M)**
- **Map key:** a sidebar lists every kind of place with its icon: fence (sell loot here), shops, bank, jeweller, gun shop, costume shop, hospital, police, chop shop, gang turf, bars, the armoured truck, taxis, stashes, the airport and the army base. The sidebar hides on screens narrower than 900 px.
- **Hover a marker** for its name, what it's for, whether it's closed or already robbed, and how far away it is.
- **Labels:** key places (fence, bank, jeweller, truck, gun shop and the rest) are always labelled. Zoom in (3× and up) to label everything. Labels no longer pile on top of each other: lower-priority ones give way.

**Minimap**
- It uses the same icons as the big map.
- Nearby key places get a label; the fence reads "Fence · sell loot".
- Important places off the edge (fence, bank, truck, active job) are pinned to the rim pointing toward them. The airport and base pin from up to 2.5 km away.
- Your waypoint or job target shows its distance in the corner ("◆ 879 m").

**Homes**
- Some houses are empty (the family is away). Others have one or two people in, sometimes asleep.
- Each house now has a back room behind a partition wall with a doorway. Most residents are in the back room or kitchen; some are in the front room.
- **Noticing you:** residents notice if they can see you (within 12 m, clear line of sight, same floor), hear you (running without crouching within 13 m, or a gunshot within 30 m), or you bump into them.
- **Scaring them:** point a gun at a resident who sees you and most put their hands up and stay put for 8–12 s. Some fight back: tough ones sometimes, and people who keep a gun often draw it. Anyone who runs instead calls the police, and their shout warns everyone else in the house.

**Police and buildings**
- **No shooting through walls:** cops can't hurt you inside a home, shop or the bank until one is in the same room, and the helicopter never fires at you indoors. Upstairs you're safe until they're upstairs too.
- **Breaching:** cops only come for a building if they saw you near it (SWAT always come). They stack up on a closed front door, one kicks it in after about 2 s ("The cops kicked the door in!"), then they come through. For shops and the bank they use the open side.
- In testing: the door was kicked at 4 s, the first cop was inside at 5 s, and no damage got through before that.

## 1u. Update: fewer draw calls

**Where the calls came from** (a downtown main pass, about 940 calls)
- Static city pieces, one mesh per tile per material: about 380.
- Cars: about 180, because each wheel was two calls (tyre, rim) and each driver five meshes.
- Characters about 90, instanced props about 100, the rest small objects.

**Changes**
- **City tiles:** static city geometry now merges in 352 m tiles instead of 176 m, so there are a quarter as many tile-and-material meshes. Props still cull in 176 m tiles. The trade-off is that bigger tiles cull less finely, so more off-screen triangles reach the graphics card.
- **Car wheels:** tyre and rim are one vertex-coloured mesh, so one call per wheel instead of two.
- **Car drivers:** two vertex-coloured meshes (body, and head and hair) instead of five, shared between drivers who look the same. The head is still hidden in first person.
- **Bank cash carts and gold pallet:** one mesh each instead of nine.

**Results**
- Draw calls: about 25% fewer downtown (spawn street about 900 → about 690).
- Frame time: 0.2–1.4 ms faster in interleaved A/B runs (five-to-ten-per-cent range). Timing in the test pane swings a lot between page loads, so only back-to-back pairs were compared.

## 1t. Update: downtown performance pass

Profiled with timing that waits for the graphics card to finish.

**Where the frame went**
- Redrawing the sun's shadow map every frame cost about 3.4 ms.
- Window glass, window frames and front doors were each one city-wide instanced mesh that was never culled. Frames alone were 810k triangles (16,878 copies), glass another 192k, and they were drawn every frame from anywhere.

**Fixes**
- **Shadow map every other frame:** static city shadows don't need a redraw every frame. Moving things' shadows lag by one frame at most, and the shadow matrix only changes when the map is redrawn, so nothing jumps.
- **Tiled windows and doors:** glass, frames and doors are now built after generation as instanced meshes in 176 m tiles. Each tile is culled when off screen and dropped beyond about 330–350 m, and the door tiles cull in the shadow pass too. Breaking glass and swinging doors update their own tile.

**Results** (same views, 1000×750, before → after)

| View | Frame | Triangles |
|---|---|---|
| Spawn street | 8.4 → 6.7 ms (-20%) | 5.9M → 3.5M |
| High downtown | 8.0 → 6.7 ms (-16%) | |
| Suburbs | 4.5 → 4.4 ms | 4.7M → 2.6M |

**What's left**
- Bloom costs about 0.1 ms, characters about 0.3 ms, and render resolution makes no difference.
- The remaining cost is the number of draw calls (about 900–1,500 downtown): the game is now limited by the processor, not the graphics card.
- Further gains would mean merging more of the city's separate meshes.

## 1s. Update (build 19): bikes, city life, smarter police, fences, a bank job

**Motorbikes and bicycles**
- A sport motorbike (to about 165 km/h) and a city bicycle. Both lean into corners.
- Hold **Shift** on the motorbike for a wheelie; on the bicycle, Shift pedals hard (about 1.5× speed).
- You sit on the bike, tucked in on the motorbike and pedalling on the bicycle. Traffic bikes have helmeted riders.
- A hard hit (above about 25 km/h into a wall or vehicle) throws the rider off and ragdolls them. AI riders are thrown too.
- Bikes appear in traffic and parked at the kerb (about 1 in 10 vehicles).

**City life**
- **Taxis:**
  - On foot, press the horn key (**H**) to flag down a cab. The nearest taxi (or a new one) drives to you and shows as a yellow **T** on the minimap.
  - **F** gets in the back. It drives you to your map waypoint, or asks "Where to?" if none is set.
  - **Space** skips the ride. The fare is charged on arrival (about $4 + 3.5¢ per metre, $8 minimum).
- **Buses:** white city buses with a green livery band, side windows, an upright windscreen and a lit destination board. They pull in every 15–25 s for 6 s; a few people step off and some climb aboard.
- **Parking wardens:** by day (8:00–19:00) a warden walks to parked cars and writes tickets, leaving a slip on the windscreen. If it's the car you last parked, -$40.
- **Opening hours:**
  - AMMO & ARMS 7:00–22:00, MASKS & COSTUMES 9:00–21:00 ("Closed. Opens at …").
  - The jeweller has staff 9:00–20:00; after hours it's empty but still alarmed.
  - The 24/7 stores stay open.

**Police tactics**
- **Spike strips** (2+ stars, driving fast): laid across the road a block or two ahead, round a corner from view, with a cruiser beside them. Any wheel crossing a strip goes flat.
- **Helicopter searchlight** at night (4+ stars): a spotlight and visible beam that track you, or your last known position. Caught in the beam, they know where you are.
- **SWAT** (3+ stars, hiding indoors for about 7 s):
  - A black van pulls up outside and four armoured officers (rifles and a shotgun, 170 HP) stack on the front door.
  - Once SWAT arrives they know which building you're in, so you can't lose your stars by hiding there.
  - They breach with a flashbang and come in after you.
- **Blockades:** with 3+ stars, crossing the bridge or the causeway puts two cruisers across the far end and a spike strip in front.

**Fences and hot goods**
- From break-ins, the jewellery box, gold watch, painting, games console, graphics cards and family silver are now goods, not cash. So is the bank's gold.
- **Sal the fence** stands behind the chop shop (**F** on the map). Press **E** to sell everything.
- Sal pays by how hot the goods are: about 52% straight off a job, rising to 100% after 5 minutes.
- He won't deal while you have stars. Goods are lost if you're wasted or busted.
- A GOODS readout under the top bar shows the count, value and HOT/COOL.

**First Sprawl Bank** (downtown, ▣ on the map)
- Open 9:00–17:00, with two tellers, an armed guard and customers. Closed at night, but a motion sensor can trip.
- Drawing a gun or firing inside sets off the silent alarm (2 stars): tellers put their hands up, customers cower, and the guard pulls a pistol.
- From the lobby side of the counter, **hold E** to make the tellers empty their drawers ($700–1,400).
- Go through the staff gate at the right-hand end of the counter, then **hold E** at the round vault door to rig a thermal drill (3 stars).
  - It cuts for 45 s, with sparks and a progress bar.
  - It jams twice. Get back to it and **hold E** to clear it.
- The vault door swings open. Four cash carts ($2,200–3,800 each) and a pallet of gold bars (goods, about $3,000–4,200) sparkle inside.
- It resets about 10 minutes after the robbery, once you're well away.

**Cost:** load is about 5.1 s.
- Bikes are drawn lean: parts that share a material are merged, with colours baked into the vertices, and each bike type's geometry is built once and shared. A traffic rider is one mesh.
- About 8.5 meshes a bike, down from 19. With 20 bikes in view, draw calls fell from 1,428 to 1,039 and frame time from 8.3 to 8.0 ms in testing.
- Most of the remaining draw time downtown is the city itself, not the bikes.

## 1r. Update (build 18): jet targeting, HUD and camera feeds

- **The seeker prefers threats.**
  - Tanks, SAM sites, armed aircraft, police cars, the police helicopter and the armoured truck are picked up up to about 26° off the nose.
  - Civilian traffic only locks when it's within about 6° of dead ahead, and a threat in the cone always wins over it.
  - It keeps the target it already has unless something much better appears.
  - A lock takes 0.9 s to build, with fast beeps while acquiring. A missile fired before the lock completes flies straight.
- **Jet HUD** (anything with missiles: the F-29 and the Hunter attack helicopter):
  - Speed and altitude boxes either side of the gunsight, and a compass tape across the top.
  - Diamond markers on threats in view: red for military, blue for police.
  - Corner brackets on the target. They're amber with a filling ring while acquiring and red when LOCKED, with the target's name and range underneath.
  - An arrow at the screen edge when the target is out of view.
  - A weapons panel showing GUN, missile state (ready / lock / reloading) and flares.
- **TGP · FLIR feed** (right): a targeting-pod camera under the nose.
  - Grey thermal picture, zoomed to fit the target, with the target glowing white-hot even behind buildings.
  - A tracking box, zoom factor and range, and SLEW / TRACK status.
- **MSL CAM feed** (left): rides your missile in, with distance to target. The feed dies with "IMPACT · SIGNAL LOST" static.
- **Cost:** each feed renders into its own small texture at 30 fps, taking turns, and the city-wide window meshes are skipped. In testing that was about +1.8 ms per frame while a feed was up.

## 1q. Update (build 17): armoured truck heist

- **When it appears:** about every 3.5 minutes, when you're in the city with no stars, a security truck starts its rounds 90–180 m away.
  - It drives with ordinary traffic and shows on the minimap and the big map as a green **$**.
  - It's heavy (4.2 t, 900 HP), dark green-grey, with armour bands, a grille guard, an amber beacon and real rear doors on hinges.
- **When you attack it:** hit it (bullets or ramming) and it makes a run for it at about 60 km/h, ignoring red lights.
- **Stopping it:** shoot out two tyres, knock it below half health, or box it in for a few seconds.
  - Two guards climb out, one with a pistol and one with an SMG, 150 HP each. They take cover and fight.
  - The panic button goes straight to dispatch: 2 stars.
  - Its alarm horn sounds for 25 s.
- **Getting the cash:**
  - Behind the stopped truck, **hold E** for 2 s to plant a charge, which beeps for 5 s. A grenade or rocket at the back doors works too.
  - The doors blow open and seven cash bags ($2,600–4,600 in all) spill onto the road with loose notes.
  - The truck survives the blast. You go to at least 3 stars.
- Trying to carjack it makes the guards bail out armed instead.
- Burglar alarms and the truck's panic button now report straight to the police, not through a witness.

## 1p. Update (build 16): break-ins, two-storey homes, distinct interiors

**Homes**
- Every home has real window openings with framed glass you can see through.
- About 40% have a second floor:
  - Stairs inside with a handrail, and a balustrade round the stairwell upstairs.
  - An open back bedroom window, with a drainpipe up to it.
- Six interior themes, each with its own furniture and loot (there are two of every family home):

| Theme | Downstairs | Loot |
|---|---|---|
| Family | sofa, TV, toys, kitchen, dining table | cookie jar, games console, jewellery box (kids' room upstairs) |
| Rich | cream sofa, fireplace, painting, piano, a bust, dark dining table | family silver, art, a safe (upstairs or in the study), gold watch. Always alarmed |
| Elderly | armchairs, tea table, grandfather clock, bookshelf, cat tree | cash under the mattress, cookie jar, jewellery |
| Gamer | dark walls, RGB light strips, beanbags, big TV, three-screen PC, energy drinks | console, PC graphics cards, cash |
| Artist | easels, canvases, paint spills, plants, concrete floor | canvases, gold watch |
| Bachelor | worn sofa, pizza boxes, cans, weight bench, home bar | sofa stash, a safe upstairs |

**Who's home**
- When you come near, a home decides who's in:
  - By day, some homes are out (door locked) and some are home (as before: they fight, pull a gun or flee and call the cops).
  - After dark, everyone's asleep and the door is locked.

**Getting in**
- Hold **E** at a locked door to pick the lock (3 s).
- **E** at a window smashes it, and **E** again climbs through.
- **E** at the drainpipe climbs to the open upstairs window and swings in. From inside, **E** at that window climbs back out and down.
- Upstairs, a broken window lets you jump out onto the lawn.

**Inside**
- Loot sparkles nearby. **Hold E** to take it. A safe takes 9 s and is noisy.
- In a sleeping house a NOISE meter fills:
  - Crouching makes no noise, walking a little, sprinting a lot.
  - Smashing glass, looting and gunshots add more.
  - When it fills, one or two residents come down (the rich ones are more often armed).
- If you're upstairs, armed residents cover the stairs and shout rather than shooting through the ceiling; others run out and call the cops.
- **Alarms** (every rich home, and some others):
  - Open the front door and you have 11 s to **hold E** at the panel by the door.
  - Breaking a downstairs window sets it off at once. Then the cops are called (2 stars) and sleepers wake.
  - The upstairs back window isn't wired.
- Leaving shows your haul. Broken glass and stolen loot reset about 10 minutes after the burglary.

**Cost**
- About 2,100 homes, 16,800 windows. Glass and frames are two instanced meshes.
- About 1.4 s longer to load.
- About 1.4 M more triangles in suburbs, with draw time about +0.3 ms in testing.

## 1o. Update (build 15): cars rebuilt (fourth version)

- **Body shell:** the nose and tail round off in plan and in profile, so there are no flat brick faces.
  - Corner radius in plan: about 0.42 m on cars, 0.5 m on sports cars, 0.24 m on vans and trucks.
  - The end faces roll over top and bottom, and the bumpers tuck up.
  - The sides are slightly barrelled, with a character line and tumblehome.
  - Roofs and bonnets are crowned, and the wheel arches are flared.
- **Glasshouse:** body-coloured A and C pillars, a black B pillar on four-doors, and a dark belt line where the glass meets the paint.
  - Vans have a windscreen and cab side windows lying on the body, and the van driver sits behind the upright windscreen.
- **Mirrors:** painted housings on a black arm, with mirror glass.
- **Front and rear:**
  - A grille with a surround and slats, a lower intake, a front lip, fog lamps and a rear diffuser.
  - Headlights, running-light strips, corner indicators, tail lights and reverse lights sit on the curved surface and turn to follow it.
- **Wheels:** a ten-spoke rim with a lip, hub and brake disc, set into a dark hollow barrel, so the face reads as open spokes rather than a flat plate.
- **Side details:**
  - Arch lips are body-coloured; SUVs, vans and trucks get black plastic ones.
  - There are dark sills between the arches.
  - Police cars have black two-tone doors that follow the body side. The ambulance band follows the body too.
  - Racing stripes follow the bonnet and boot lid, and come off after a heavy hit.
- **Cost:** draw calls are unchanged; every part is still merged into the same per-car meshes. Triangles are about 5% higher downtown.

## 1n. Update (build 14): natural walking, sensible pedestrians, doors that shut, better car fronts

**Walking**
- Legs reach further forward than they trail behind. The trailing leg no longer kicks up behind people.
- Stride timing comes from real ground speed, so feet stay planted. A walk is about two steps a second.
  - Planted-foot slip as a share of walking speed: crowd about 12%, player jog about 10–16%, sprint about 11%.
- Legs track the stride more tightly when running.

**Pedestrians**
- They no longer turn round, switch sides or cross the street on a random timer. Walkers always have somewhere to go.
- They cross at the corner, on the zebra, straight across.
  - At the kerb they look both ways and wait for a gap in traffic (12 s at most).
  - Mid-block jaywalking fell from 6.5% of walking time to 1.7%.
- Walkers stuck behind a pole, bench or parked car aim past it, then turn back if that fails. Before, some spun on the spot.
- Walking to a bench, shop or bus stop gives up after 4 s if the spot can't be reached.
- Fleeing people run straight away (no sine-wave zig-zag). They swerve round walls instead of spinning against them and ease to a jog once 40 m clear.

**Doors**
- Front doors swing shut about 3 s after nobody is in the doorway.
- When residents run out, the door stays open until the last one has left the house.

**Cars**
- Black slab bumpers replaced by body-coloured ends with a slim dark lower lip and an intake.
- Headlights sit in a dark housing and wrap round onto the wings. Tail lights wrap onto the rear quarters.
- Lamp lenses are dimmer by day and only glow at night.

## 1m. Update (build 13): smoother play, a new HUD, a GTA-style look

**Smoothness**
- The camera eases between on-foot, aiming, scope, car and death views instead of snapping. Going into aim used to jump the camera about 0.6 m in one frame; the biggest single-frame move is now about 0.17 m.
- Camera shake uses smooth noise instead of a random jolt every frame.
- The chase camera swings behind the car on a smooth curve. It turns faster the faster you drive, up to a cap.
- Small differences in frame time are evened out. A real hitch still passes straight through, so the game never runs slow.
- Shadow texels snap to the actual shadow-map size, so shadows don't crawl on Low quality.
- Road paint was boxes (12 triangles each, the whole map drawn every frame). It is now flat quads in 352 m tiles, one draw call per tile, and far tiles are culled.
  - Triangle counts: downtown 4.0M → 3.2M; Pinewood 1.7M → 0.85M.
- Adaptive quality: if frames stay slow at the lowest resolution, ambient occlusion turns off, then shadow detail drops. Both come back after a good run of fast frames.

**HUD and menus**
- Fonts: Barlow Condensed for numbers and titles, Inter for text. Both load from Google Fonts and fall back to system fonts offline. All HUD colours and spacing come from one set of CSS tokens.
- The radar is a rounded rectangle with your arrow low in the frame, so you see more of the road ahead. It zooms out with speed and flashes red/blue round the edge when you're wanted.
- Health, armour and vehicle bars sit under the radar.
- Top right:
  - Outlined wanted stars that pop in.
  - A larger cash total, with a +$ / −$ line under it whenever money comes in or goes out.
  - A weapon panel showing name, ammo and a magazine bar. It pops when you switch weapons.
- Help notices slide in. Prompts rise into place, and their key caps have depth.
- Hit markers have a dark outline. A kill marker is red and pops outward.
- WASTED / BUSTED appear on a dark band across the screen.
- Start screen, pause menu and map screen restyled.
  - The pause menu's controls list is three columns, so it fits.
  - Its RESUME button stays pinned at the bottom.

**Graphics**
- A new sky replaces three's Sky: deep blue overhead fading to the same haze as the fog, a sun disc and glow, a warm band at dusk, drifting clouds that thicken with the weather, and stars at night. Reflections in glass and paint use it too.
- Lighting rebalanced:
  - Stronger warm sun with a cooler fill, slightly higher exposure, more contrast.
  - Rough surfaces (asphalt, concrete, walls) take less of the blue sky light, so shade reads grey rather than navy.
- Nights:
  - Softer, wider light pools under streetlamps, lying on the road.
  - Brighter cool ambient light.
  - A warm glow around you, so you aren't a black silhouette.
- Smoke, dust, sparks and blood are soft round puffs that face the camera and fade out. They used to be solid white cubes. Smoke darkens at night.
- Scorch marks and blood pools no longer mirror the sky (they used to show as white ovals).
- The death camera no longer buries itself in your body when you die next to a wall.

**Walking and poses (follow-up)**
- Feet stay planted. The stride is timed from how fast someone is really covering ground. Each leg sweeps back at that speed while its foot is down, then swings forward; running spends less of the cycle on the ground.
  - Planted-foot slip, as a share of walking speed: crowd 0.76 → 0.15, player jog 0.16, sprint 0.2.
- People pushing against a wall or a crowd stop walking instead of marching in place.
- The hips rise and fall with the planted leg. Side-to-side sway moves the chest instead of the whole body, so it no longer drags the feet sideways.
- Pose changes blend in on a spring: cowering, surrendering, idle habits, glances and getting into a crouch.
  - Biggest one-frame limb jump: about 52° → 10°.
  - Punches, kicks, aiming and hit reactions use a stiff spring, so they stay sharp.
- Witness calls no longer say "Corner of [object Object]"; they name the street.

**Debug**
- `game.freeze()` / `game.freeze(false)` stops and restarts the live loop, for still screenshots.
- `game.gfx` exposes the renderer, scene, lights, sky and post-processing passes. `game.gfx.LOOK` holds the daytime look (sun, ambient, exposure, haze, fog colour, saturation, contrast) and can be tuned live.

---

## 1l. Update (build 12): smarter people, new moves, real fights, gun handling, crash damage, a bigger map

**People**
- People hear a gunshot and look towards it before they react. Nearer people react sooner.
- What they do next depends on the situation: duck behind a parked car, cower, or run.
- Crimes are only reported by a witness who sees or hears them. A cop reports it straight away.
  - Anyone else backs off, gets their phone out and calls it in after a few seconds.
  - Stop them, or get out of sight, and nobody comes.
- People who saw you commit a crime back away when you come near them later.
- When a car heads straight at them, most bystanders notice a beat late and sprint clear. About a quarter freeze and get hit.
- Fixed: the old dive left people with missing arms and glitchy limbs. Posing now ignores missing or invalid angles and repairs a rig that has gone wrong.
- Drivers floor it when shooting starts near them.
- A fist fight draws a crowd. People stand round in a ring, cheer, and some film it on their phones. A gunshot scatters them.
- Fist fighters read your swing: they cover up or step back, counter when you miss, and keep their distance.
  - When they're losing badly they give up or run.
- Armed people and gang members take cover behind cars. They pop up to fire, reload behind cover, and miss more often when you keep moving.
- Cops tackle you if you run from them at one or two stars.

**Movement**
- Z crouches. You move quietly and fewer people notice you.
  - Next to a car or a wall, you're in cover and most rounds miss you. RMB pops up to aim; LMB blind-fires.
  - Pressing Z while sprinting slides you along the ground. You can shoot during the slide.
- Space next to a parked car or a low wall vaults over it.
- Sprint and swing with your fists to do a diving tackle.
- Deep water is swum through, not drowned in. Hold Shift to swim faster. NPCs swim back to shore.

**Fighting**
- There are five kicks:
  - front kick (standing)
  - roundhouse (while moving)
  - leg sweep (crouched)
  - flying kick (in the air)
  - spinning back kick (straight after punches)
- A knockout depends on the blow that landed it:
  - stiff fall: straight over like a plank
  - twist and fold: turns round as the knees go
  - dazed stumble: a few steps back, then a fall forward
  - launch: lifted off the feet
- Every knockout you land plays in brief slow motion, with a camera punch-in.

**Guns**
- Pistols, shotguns, the sniper rifle and the RPG fire once per click.
- Automatic weapons climb as you hold the trigger, and you pull them back down.
- The crosshair shows the real cone of fire. It opens up as you shoot, move, jump or slide, and tightens when you crouch or aim.
- Rounds lose damage over distance.
- Bullets leave holes in walls, and blood when they pass through someone first.
- Aim at a tyre to blow it.
- The sights sway while aiming. Through the sniper scope, hold Shift to steady your breath.

**Cars**
- Every knock dents and creases the panels where it hit and scrapes the paint.
- Bits come off and lie in the road: bumpers, headlight glass, window glass. Passing cars kick them along.
- A hard enough crash tears a wheel off, and the wheel rolls away.
- Damage changes how the car drives:
  - a beaten-up car loses top speed
  - a flat or missing tyre pulls the car to that side and throws sparks
- A damaged engine steams first, then smokes, then catches fire.

**Map**
- The city grid is 32×32 blocks (it was 28).
- The mainland is one landmass. Its coast carries on from the city's shores instead of ending in a straight edge.
- New places:
  - Hollis Farms: a patchwork of fields, a red barn, silos and a farmhouse, up a dirt track from the highway
  - Pinewood: a small town on the highway with a diner, general store, motel, sheriff's office, saloon, church and water tower
- Silver Lake and the start of the highway moved west to make room.
- Each lake's water level is set just below its own shoreline, so lakes no longer flood the low ground round them.
- Streets closed by the coast end cleanly at the kerb, with red-and-white barriers. Before, the road surface ended in jagged slopes.
- No fake beach inland: sand only appears next to real water.
- Pinewood:
  - 12 townsfolk walk the boardwalks.
  - The diner and the general store are walk-in shops with clerks, and you can rob them.
  - Sheriff Boone patrols the street. He turns on you if you rob a shop, fire a gun or show up wanted.
  - The highway runs level through town.
- Hollis Farms:
  - Farmhands, some of them armed, walk the farmyard.
  - Old Man Hollis warns you off his land twice, then shoots.
  - The strongbox by the barn door holds his moonshine money. Press E, wait four seconds, and take $450–900.
- Unique characters have name tags, gold or red when angry. The map marks the stash and the sheriff's office.
- The full map shows place names.
- Shops, bars and towers show as dots until you zoom in.
- The snowline is smooth, and Fort Kessler is drawn as a base.

**Avatars**
- Limbs taper and have muscle shape: calves, biceps, deltoids.
- The torso has a chest, a narrower waist, and the shoulders slope up to the neck.
- Hands have fingers and a thumb. Shoes have soles.
- Heads are slightly smaller, and beards sit on the jaw.

## 1k. Update (build 11): bigger city with a real coastline, new car bodies, skyscrapers, doors, a road to the base

- **Bigger city, no longer a box:**
  - The grid grew from 22×22 to 28×28 blocks, about 28% wider. Everything that already existed kept its exact position.
  - The edge is now an organic coastline: rounded eastern corners, six coves, and sandy beaches that slope into the sea, with palms, sun umbrellas and lawns behind them.
  - The west side runs on into the foothills.
  - Streets that would end in the sea stop short. Traffic, parked cars, road markings and traffic lights only use streets on land.
  - You can walk or drive into the sea: cars sink and people drown, as before.
  - The pier, the bridge and the causeway each start from a dry approach.
- **Cars rebuilt (third version):**
  - Flat sides and a shoulder that tucks in toward the glass, with rounded top edges and corners.
  - Real wheel-arch cut-outs. Wheel size is capped so the tyres never poke through the bodywork.
  - A fitted roof skin instead of a thick lid.
- **Roads:**
  - City hills are now gentle rises (the observatory hill went from 33 m to 11 m).
  - The highway's height solver was rewritten: no 17 m wall where it leaves the city, no 6 m dip and bump at the lake-road junction.
  - The highway now climbs all the way to the Fort Kessler gate at 150 m, so you can drive into the base.
- **Planes:** faster than any car and easier to fly.
  - Jet: about 540 km/h, about 715 km/h with **Shift**. Prop plane: about 290 km/h.
  - Quicker roll, pitch and turn rates.
  - Near the ground the nose won't drop unless you throttle back to land.
- **Police:**
  - Units drive out from the police station one at a time, so it takes a while for them to reach you.
  - Units arriving from elsewhere start 150–260 m away.
  - A cap on officers per wanted level: 2, 4, 6, 9, then 12 at 5 stars.
  - Fixed the bug that kept spawning cars whenever officers got out, which caused the swarms.
- **Homes have front doors:** every door is closed until you press **E**. Residents open it when they flee.
- **Skyscrapers you can go into:** Meridian Tower (150 m), Atlas Plaza (175 m) and Skyline One (200 m), marked ▲ on the map.
  - Each has a glass lobby with a reception desk and elevators. **E** at the elevator takes you to the roof: a pool, sun loungers and a helipad.
  - Walk off the edge to base-jump; **Space** opens the parachute.
  - The view opens up with height.
- **serve.py and the build number:** see "Run it" above.

## 1j. Latest update: cars rebuilt, calmer nights, every house a home, curved boulevards, real-feeling flight

- **Cars:**
  - The window section is now a tapered shape sitting on the body's shoulder, narrower at the roof, with a painted roof skin over it. It used to bulge out past the body.
  - The body is less pillow-shaped.
  - Headlights, tail lights, indicators, number plates, grille and bumpers are placed from the body's real surface, so nothing floats off the rounded corners. Mirrors sit on a short arm at the base of the windscreen.
  - Smaller, darker alloy rims, so the tyres read as tyres.
- **Night:**
  - Unlit windows and facades go dark after sunset.
  - Lit windows are fewer, dimmer and warmer, and office towers no longer glow pale blue.
  - Bloom, signs, neon and street-lamp glow are toned down, and exposure no longer rises at night.
- **Every house is enterable:** all 1,188 houses are furnished homes with residents. Houses facing the other street are mirrored copies, so every front door faces the road. Residents appear in the nearest homes first, up to 14 people at a time, so frame rate holds.
- **Crescent Blvd and Sunset Pkwy:**
  - Crescent Blvd is a curved boulevard about 1.2 km long that sweeps across the grid from the north edge to the south-east.
  - Sunset Pkwy runs down the west side and curves along the south of the city to meet it, so together they make a loop.
  - It has sidewalks, kerbs, a dashed centre line and street lamps.
  - The blocks they cross (about 90) are green strips with trees, benches and flower beds.
  - The HUD names whichever one you're on.
- **Detailed maps:**
  - The minimap and full map are drawn from the real world at 2 px per metre: rounded kerbs, lots coloured by district, every building footprint with a height-based shadow, roof colours, trees, park paths and ponds, lane lines and zebra crossings.
  - The full map zooms with the mouse wheel and shows street names when zoomed in.
- **Rain and night flying:**
  - From the air, fog stays far away at night and in rain, instead of closing to about 250 m and turning everything black.
  - Rain streaks are fainter from the cockpit, and wet streets darken less.
  - Aircraft have red and green wingtip lights, a white tail strobe, a landing light and a soft glow, so you can see your plane at night.
- **Flight model:**
  - Slower top speeds: the jet cruises at about 320 km/h and reaches about 420 km/h on afterburner (hold **Shift**); the prop plane tops out at about 165 km/h.
  - The plane banks toward where you look, and the bank angle turns it. Roll and pitch move at realistic rates.
  - Climbing bleeds speed, diving gains it, tight turns cost energy, and below stall speed the nose drops.
  - After take-off it climbs out on its own for a few seconds.
  - The camera's speed zoom is smaller.

## 1i. Latest update: heists, masks, homes, first person, weather, a sharper look

- **Jewelry heist (DIAMOND DISTRICT, ◆ on the map, downtown):**
  - A glass-fronted store with eight display cases.
  - Walk up to a case and press **E** to smash it for $380–950.
  - The first case trips the alarm: 3 stars, the armed guard by the door opens fire, and the clerk cowers. The cases restock a few minutes after you leave.
- **Masks (MASKS & COSTUMES, M on the map):**
  - **E** buys a mask: balaclava, hockey, skull or clown; press again for the next one. **X** puts it on or takes it off.
  - Commit crimes masked, then take the mask off where no cop can see you, and the wanted level drops by 2–3 stars ("they're looking for a masked suspect").
  - If they watch you take it off, or you did anything bare-faced, it doesn't work.
- **Homes you can walk into:** about a third of the houses whose doors face the street are hollow and furnished: sofa, TV, rug, kitchen, dining table, bed and lamp.
  - **Residents:** they potter between rooms.
  - **Walk in uninvited:** some fight you, some pull a pistol, shotgun or bat ("Get out of my house!"), and others run out shouting for help and call the police.
- **First-person view (B):** on foot from your eyes, with your hands in view. In a car, from the driver's seat, looking over the dashboard and steering wheel.
- **Fighting feels better:**
  - People speed up and slow down with momentum instead of snapping.
  - Punches turn you toward the nearest opponent in front and step you into range.
  - Every landed blow has a short hit-stop, an impact puff and a camera kick (bigger on hooks, uppercuts and bat swings).
- **Weather:** clear, overcast and rain spells.
  - **Rain:** streaks fall around you, and roads and pavements turn dark and glossy.
  - **Under cloud:** the light goes flat and grey.
  - **Storms:** lightning flashes.
  - **Umbrellas:** about half the people on the street put one up while it rains.
- **Look and speed:**
  - **Post-processing:** antialiasing again (it was lost when bloom arrived), a filmic grade (contrast, warm highlights, cool shadows), a vignette and fine film grain. The screen edges redden and colour drains when you're badly hurt.
  - **Graphics setting in the pause menu:**
    - **Low:** fastest.
    - **Medium:** the default.
    - **High:** adds ambient occlusion for contact shading in corners and under objects.
  - **Dynamic resolution:** lowers the render resolution when frames get slow and raises it again when there's headroom. The pause menu shows the FPS.
  - **Trees:** leaf-cluster crowns instead of smooth blobs.
  - **Clothing:** woven cotton, denim and leather textures; open jackets over shirts; wristwatches; earrings.
- **A less square city:**
  - Every block now has rounded corners with curved kerbs.
  - Parks are landscaped: a winding loop path, curving entrance paths, an irregular pond with a stone rim, flower beds, hedges, benches and lamps.

## 1h. The Kessler Range, real cars, ragdolls, easy flying

- **The Kessler Range:** a new mountain region west of the city, about 3.4 km by 3.3 km.
  - **Terrain:** ridged peaks with snow caps, rock faces, dry grass, sand at the shorelines.
  - **Forests:** about 12,000 pines, in dense stands with meadows between.
  - **Lakes:** Silver Lake (cabins and a dock), Mirror Lake high in the range, and Pine Lake. You can swim and drown in them, and cars sink.
  - **Kessler Highway:** winds in from the city's west edge at a gentle grade, with guard rails along drops, side roads, a Gas & Go and a row of wind turbines.
  - **Traffic:** highway traffic and police patrols. Pedestrians walk the paths.
- **Fort Kessler moved into the mountains:** it now sits on a plateau at 150 m, entered through a gate on the highway.
  - **Layout:** a grass infield with concrete aprons and a 600 m runway with a control tower; barracks, tent lines, a container yard and grassed ammunition bunkers; sandbag positions, watchtowers and a fence.
  - **Equipment:** a radar dome and a rotating dish, helipads, a motor pool with three tanks, two SAM sites, and three jets (two lined up on the runway).
  - **Patrols:** trucks and SUVs drive the base's ring road.
- **The airport stays by the city** and is now busy:
  - **Grounds:** a cargo terminal, a hotel, a parking garage, a rental office with a fleet you can take, and a fuel farm.
  - **Traffic:** shuttles, taxis and baggage tugs drive its roads, and travellers walk to the terminal.
  - **Airliners:** they land, taxi to a gate, wait, taxi out and take off again.
- **Cars:**
  - **Bodies and cabin:** bodies are now lofted from smooth cross-sections, with rounded corners, curved sides and a proper glass cabin with tumblehome, so they no longer look like extruded slabs.
  - **Paint and parts:** glossy clear-coated paint, darker tinted glass, real tyres with sidewalls around alloy rims, and bumpers tucked into the body.
  - **Interior and driver:** seats, headrests, a dashboard and a steering wheel. The driver is seated below the roofline, so nobody's head sticks out while driving.
- **Ragdolls:** dead and knocked-out people go limp and are simulated, falling over and crumpling on slopes and kerbs.
  - Bullets, kicks, stomps, cars and explosions all push the body around.
  - Blood pools where the body comes to rest.
  - Knocked-out people stand back up from wherever they landed.
- **Flying is much easier:**
  - **Planes:** look where you want to go and the plane banks and turns there by itself. Hold W on the runway and it lifts off on its own. Look up to climb and down to dive. A/D still roll.
  - **Helicopters:** they turn to face where you look.
  - **Camera:** a free orbit camera that pulls back with speed.
  - **More room:** with the mountains the map is much bigger to fly over, and you can see about 2–4 km depending on altitude.
- **Visuals and map:**
  - Soft bloom on bright lights (neon, streetlights, headlights), stronger at night.
  - The map and minimap show the mountains with shaded relief, the lakes, the highway and the base. In an aircraft the minimap zooms out.

## 1g. Kessler Field (airport and army base), flying, skydiving, missiles, street life

- **Kessler Field:** a new landmass north of the city, over the Kessler Causeway (straight up the middle avenue).
  - **Sprawl International:** an 880 m runway, taxiway and apron, a glass terminal with jet bridges, a control tower, hangars and a parked airliner.
  - **Fort Kessler:** fenced, with a guard gate, watchtowers, barracks, hangars, fuel tanks, a helipad and a SAM site.
  - Trespassing sets off the alarm: 4 stars, soldiers with rifles open fire, the tanks turn their turrets on you, and the SAM fires homing missiles at any aircraft over the base.
- **Vehicles to steal:**
  - Two prop planes and a helicopter at the airport.
  - Two fighter jets, an attack helicopter and two tanks in the base.
- **Flying:**
  - Planes: W/S throttle, the mouse pitches and banks, A/D roll (steer on the ground), Space brakes.
  - Helicopters: W/S forward/back, A/D strafe, Shift up, Space down, the mouse turns.
  - Jet and attack helicopter: LMB cannon, RMB homing missile (locks onto whatever is near the nose), E drops flares (jet).
  - You crash into buildings, the bridge and the sea. Helicopters can land on rooftops. Press F to get out on the ground, or bail out in the air.
- **Skydiving:** bail out above about 8 m and you free-fall. Space or F opens the parachute; steer with A/D, W to dive, S to flare. Landing in free fall kills you. Hit a roof and you slide off the edge.
- **Tank:** the turret follows your view; LMB fires the main gun (big explosions). It's heavy enough to shove cars aside.
- **Missiles:** the RPG now locks onto vehicles and aircraft near the crosshair. Explosions damage aircraft and the police helicopter.
- **Gunshots:** a headshot drops them: 40% die on the spot, the rest die where they lie within about 10 seconds. You can still kick, stomp or shoot bodies afterwards, and they jerk and move.
- **Street life:**
  - People walk to real places: shop windows, bus stops, park benches, hot dog carts. They go round the block, cross at the corners, then window-shop, wait, sit, eat or take photos. Sometimes they go inside or catch the bus.
  - Groups of 2–4 stand chatting with hand gestures.
  - Regulars on busy corners: hot dog vendors (press E to buy one: $5, +25 HP), street musicians with guitars (people stop to watch and clap) and doom-sayers with signs.
  - About 1 in 12 walkers has a dog on a lead. At night some people stagger home drunk.
- **People fight back more:**
  - Rear-end someone and they may get out and come at you (sometimes armed).
  - Steal a parked car and the owner may come running.
- **Police on Coral Key:** they come over the bridge and patrol the loop road, and patrol cars in traffic join a chase when you're wanted.
- **Clipping fixes:**
  - Cars are proper boxes for people to bump into.
  - Trees, palms, lamp posts, signal poles, hydrants, bins, benches and meters are solid.
  - The island's grass no longer pokes through its roads.
  - People keep full detail out to 40 m.
- **Visuals:**
  - Smoother characters (more rounded limbs, torso and head).
  - Leafy, lumpy tree crowns.
  - Car bodies with rounded profiles.
  - A rippling sea.

## 1f. Latest update: wounds, stomps, detailed cars, careful cops

- **Gunshots:**
  - A headshot kills.
  - Two pistol rounds to the body usually drop a person wounded rather than dead (about 15% die outright).
  - Wounded people lie face down, crawl away calling for help, and bleed out after about 30 s unless an ambulance gets there. One more shot, kick or stomp finishes them. Sniper rounds and point-blank shotgun blasts still kill outright.
- **Stomp:** when someone is on the ground (knocked down, knocked out or wounded) and you have fists or a bat, the prompt shows **LMB / V Stomp**.
- **Cars:**
  - New detail: wheel arches, door seams and handles, window pillars, grille slats, number plates, indicators, reverse lights, exhaust pipes, spoked rims, softer body edges and a soft shadow under each car.
  - Brake lights come on when a car slows down, and tail lights glow at night.
  - Hard crashes dent the panels where the car was hit, and badly damaged cars get shattered, frosted windows.
- **Police and ambulance drivers:**
  - When you're on foot they pull up about 20 m away and the officers get out on foot; they no longer drive at you.
  - They brake for anyone in front of them. Ordinary traffic already did.

## 1e. Latest update: Coral Key, crowds, smarter NPCs, knockouts and headshots

- **Coral Key:**
  - A resort island across the bay, reached by the Sprawl Bay Bridge: a red suspension bridge, 9 m above the water at its high point, with lamps and cables.
  - On the island:
    - Ocean Drive: a coastal loop road with pavements, lamps and palms.
    - A main street through a central plaza with a fountain.
    - Pastel art-deco hotels with neon names along the east beach.
    - About 20 villas with pools.
    - A lighthouse on the north hill whose beam sweeps at night.
    - A marina with docks and bobbing boats.
  - The island has its own crowd and cars circling Ocean Drive. Palms also line the main city's beaches.
  - The minimap, the full map and GPS routes cover the island; routes go over the bridge.
- **Water:** nobody can swim. Drive into the sea and the car sinks; you bail out and drown after a few seconds unless you reach land.
- **Bigger crowds:** 170 pedestrians, kept within about 100 m of you, so streets feel busy; the island adds up to 45 more.
  - People switch to a simple model beyond 30 m and only nearby characters cast shadows.
  - Kerbside props are only drawn nearby, and cars hide beyond 300 m. Frame time stayed about the same.
- **Smarter movement:** people, cops, medics and gang members look ahead and steer round walls, kiosks and cars. If they still get stuck they back off and try another way. People fleeing gunfire no longer pile into buildings.
- **Ambulances:** fewer of them. Only some incidents call one, it waits about 10 s, and there's a 1.5–2.5 minute gap between call-outs.
- **Fist fights:**
  - It takes about 8 punches (or a few punches and a stomp) to put someone down.
  - Fists and kicks knock people out instead of killing them; they lie limp with their eyes shut and come round after 20–40 s.
  - Kick or stomp someone who's out cold to finish them off. Bats and knives are still lethal.
- **Gunfire hit zones:**
  - Free aim hits where the crosshair is. A headshot kills a civilian outright, with a HEADSHOT marker and a body that drops instantly.
  - Two pistol rounds to the body kill. A leg hit does less damage and may put them down. A shot clearly over the head misses.
  - Lock-on aim hits mostly the body.
- **People:**
  - Many more types:
    - Men: business, casual, worker, jogger, elderly, street (hoodies, backwards caps, gold chains), tourist (Hawaiian shirts, sun hats, cameras), biker (leather jacket, bandana, beard, shades), hipster (plaid, beanie, glasses), gym (big arms), beach (often shirtless).
    - Women: business (skirt or trouser suit), casual, jogger, elderly, street, tourist, party (dresses), hipster, beach.
  - Body types vary: slim, average, heavy, muscular.
  - Faces are now painted in detail:
    - Coloured irises, eyelids and lashes, nose shading and nostrils, shaped lips, chin shadow.
    - Stubble, make-up, freckles or wrinkles.
    - Scared, angry or calm expressions, and eyes shut when knocked out or dead.
  - Heads have ears, a smaller nose and a stronger jaw for men.
  - New hairstyles: afro, curly, mohawk, slicked back, long with side strands. Plaid, striped and Hawaiian shirt prints.

## 1d. Latest update: hills, street fights, carjacking, ambulances, smarter police

- **Terrain:**
  - The outer districts roll into hills; the biggest rises about 33 m, with an observatory and a blinking radio mast on top.
  - Downtown and the shoreline stay flat. Roads, pavements, lawns and kerbs follow the ground, and buildings sit on it with foundations on the low side.
  - Cars pitch and roll with the slope, slow down climbing and speed up going down.
- **New landmarks:**
  - A pier off the south beach with food stalls, lamps and a turning Ferris wheel that lights up at night.
  - Three stunt ramps on the beach. Airtime pays a stunt bonus.
- **People:**
  - Outfits by type: office workers in suits (some with ties, some in skirt suits), hi-vis workers with hard hats, joggers, older people who walk slower and stoop.
  - Women have their own build, hair and skirts. Accessories include glasses, sunglasses, beards, backpacks and handbags. Hands have thumbs.
  - Faces change expression: scared, angry or calm.
  - Idle habits: arms folded, hands in pockets, checking the time, smoking.
  - People look at you when you walk past. Hurt people limp, and crowds cower with their hands over their heads at gunfire.
- **Fighting:**
  - Punches chain into a jab, cross, hook and uppercut combo; the uppercut floors people.
  - Hits land mid-swing, heads snap back, and heavy hits stagger.
  - Hold right-click with fists to block; a blocked punch throws the attacker off balance, and kicks break a guard.
  - Punching or kicking someone who's down becomes a stomp. New baseball bat and knife (in parks, or dropped by people who carry them).
- **People fight back:**
  - About 1 in 14 pedestrians carries a hidden pistol (more in the industrial area and at night), and some tough ones carry a bat or knife.
  - They pull it when you attack them, aim at them, or fight them. Friends walking together back each other up.
  - Badly hurt people collapse and crawl, calling for help. Everyone shouts lines in speech bubbles.
- **Carjacking:**
  - You walk to the driver's door, drag the driver out, then climb in; you can't grab a moving car. About 1 in 5 drivers floors it when they see you coming.
  - Some drivers fight you for the car, and will drag you back out if you're still parked, or pull a gun. About a third of parked cars are locked: you smash the window and the alarm goes off.
- **Ambulances:** they come to people who are hurt or killed. Paramedics kneel and do CPR, often revive them, then drive off. Steal an ambulance to start the paramedic job: pick up injured people and get them to the hospital for cash.
- **Police:**
  - At 1–2 stars they come to arrest you: weapons drawn, shouting, holding fire unless you shoot, aim at them or hurt one. They'll pull you out of a stopped car.
  - With lethal force on, only two or three officers press the attack at a time (rotating). The rest hang back behind cars and pop up to shoot, or work round your flank.
- **Fixes:**
  - Arrests now work at 2 stars.
  - Bodies no longer vanish in plain view.
  - Car crashes take weight into account, so a truck shoves a compact.
  - The crosshair, health bars and lock-on marker were drawn in the wrong place on high-resolution screens.

## 1c. Latest update: bigger city, crowds, interiors, weapons

- **Map:** 22×22 blocks (about 1.2 km across), up from 16×16, with more parks. The hand-placed landmarks stay centred.
- **Crowds:** 110 pedestrians, spawned near you and weighted toward downtown. Some walk in pairs; some are on the phone.
- **Traffic:** 44 moving cars and 140 parked.
- **Distance detail:**
  - People past 48 m switch to a one-mesh stand-in.
  - Cars past 100 m drop their trim, wheels and shadows.
- **Street detail:**
  - Kerbstones and green street-name signs at every intersection.
  - Kerbside props: parking meters, news boxes, mailboxes, payphones, bus shelters and manholes.
  - Shop signs and awnings over storefronts, and rooftop billboards.
- **Interiors you can walk into:**
  - Every robbable shop: shelves, counter, fridges, clerk.
  - AMMO & ARMS: pegboard, display cases, gun keeper.
  - Six bars (B on the map): bar, stools, pool table, jukebox, neon, bartender and drinkers. The camera stays under the ceiling indoors.
- **Weapons:** new detailed multi-part models.
  - SMG (32 rounds).
  - Sniper rifle: scope view, one-shot kills.
  - RPG: rockets explode on impact.
  - Cops and gangs now carry SMGs too. A sniper and an RPG are hidden in the industrial district; all three are also sold at AMMO & ARMS.
- **Aiming:**
  - Lock-on reticle with the target's health.
  - The crosshair turns red over a person.
  - Tab weapon wheel.
- **World:**
  - A 20-minute day/night cycle (clock under the cash): lit windows, glowing streetlights with light pools, headlights at night.
  - Three procedural radio stations in cars.

## 1b. Systems added in the latest update

### Combat realism
- **Rifles and shotguns:** shouldered when aiming (bent elbow, support hand on the handguard), carried across the chest otherwise.
- **Recoil and reloads:** recoil kicks the arms and camera, and reloading has its own animation.
- **Movement:** strafing and backpedalling turn the hips toward the direction of travel while the chest keeps facing the aim.
- **Hit reactions:** the body gives way in the direction the hit came from. On death, the knees often buckle before the body falls.
- **Blood pools and shell casings:** blood spreads under bodies, and guns eject casings.
- **Dropped guns:** the dead drop the gun they were carrying, with ammo. It lies on the ground; walk over it to take it.

### Explosions
- One shared explosion handles cars, grenades, barrels and the helicopter: fire, smoke and debris, a scorch mark, people thrown, cars damaged and pushed.
- **Grenades:** proper arcs with gravity, bouncing off the ground and walls, on a 2.4 s fuse.
- **Explosive barrels:** clusters at the port, the gang yard and the GAS & GO. Shoot them, ram them or catch them in a blast, and they chain-react.

### Cars and chases
- **New cars:**
  - Verano X1 supercar: rear wing, splitter, side intakes, 216 km/h.
  - Brute 440 muscle car: hood scoop, racing stripes.
  - Ridgeback SUV.
  - Police interceptors, from 3 stars.
- **Driving:** nitro on Shift with blue exhaust flame, a wider view and speed lines. Exhaust backfires when you lift off at speed, and drivers are visible through the tinted glass.
- **Police search:**
  - Once the cops lose sight of you, they sweep a search circle around your last known position. It shows on the minimap.
  - Getting outside the circle drops your stars much faster.
  - While they can see you, cruisers predict where you're heading and aim PIT manoeuvres at your rear quarter, using a speed boost to catch up.
- **Roadblocks:** at 3+ stars while you're driving fast, two cruisers park across the road a couple of blocks ahead, with officers behind them.

### Jobs (press T)
1. **Car to order:** steal the marked car and drive it to the chop shop (C on the map). It has a tracker half the time, and the buyer won't take a car while the cops are on you. Pay drops with damage.
2. **Hit:** a loan shark with two armed bodyguards. When spotted, he runs to his getaway car and flees, always turning away from you. Wreck the car, or box it in until he bails out on foot.
3. **Courier:** collect a package, then beat the clock to the drop-off. Pay scales with time left.

Every job gets a marker in the world, a blip and a GPS route on the minimap, an objective line on the HUD, and a MISSION PASSED or MISSION FAILED banner. Street and district names show next to the minimap (for example "Central Ave / Midtown").

---

## 1. Core mechanics

### Camera (section 14)
- **On foot:** over the right shoulder, about 3.8 m back. Right mouse pulls it in to about 2 m and narrows the view to 48°.
- **In a car:** a chase camera that follows the car's heading. It pulls back and widens the view with speed.
- **Walls:** the camera is pulled in whenever a wall gets between it and you, so the view never ends up inside a building.
- **Aiming:** the crosshair is a ray from the camera. Bullets travel from your gun to whatever that ray hits, so you hit what the crosshair is on.
- **Recoil:** each shot kicks the camera. The crosshair widens while you move.

### Driving (section 7)
- **Arcade model:** velocity is split into forward and sideways parts, and grip removes the sideways part. The nose turns *after* the velocity is applied, so momentum lags behind it and you get drift. **Space** drops the grip for handbrake slides with skid marks and tyre smoke.
- **Vehicle types:** sedan, hatchback, sports car, van, pickup, taxi, police. Bodies are extruded side profiles with glass cabins, metallic paint, bumpers, mirrors, and tyres with rims.
- **Damage:** crashes damage cars, which smoke, catch fire, then explode and throw people nearby.

### Combat (section 8)
- **Weapons:**
  - Fists: alternating punches, with a chance of a knockdown.
  - Pistol.
  - Shotgun: 7 pellets.
  - Carbine: automatic.
- **Feedback:** hit markers (red on a kill), a muzzle-flash sprite and light, tracers.
- **Dodge roll:** makes you a smaller target while it lasts.

### Robbery
There are 12 shops, shown as **$** on the minimap and a green ring outside each door. Hold **E** with a gun out for 4 s. That pays $350–800 plus a bonus per wanted star. The silent alarm gives 1 star, and finishing the robbery raises it to 2. Shops restock after 3 minutes. Pedestrians can be held up for their cash.

### Wanted level (section 10)
- Crimes only count if a pedestrian (within 28 m) or a cop (within 45 m) sees them.
- **Police by star level:**

  | Stars | Police cars | Response |
  |---|---|---|
  | 1 | 1 | Officers try to arrest you |
  | 2 | 2 | Shooting starts |
  | 3 | 4, two officers each | Some officers carry shotguns |
  | 4 | 5 | Rifles, plus a **helicopter** |
  | 5 | 7 | Rifles, plus the helicopter |

- **The helicopter** circles you with a searchlight and fires from above. Shoot it down with the camera roughly level or looking up: it spins out and explodes.
- **Police cars** drive the road grid toward you, ram your car, or park and send officers out on foot.
- **Losing them:** break line of sight for `7 + 2.5 × stars` seconds to drop one star.
- **WASTED** sends you to the hospital (10% bill). **BUSTED** sends you to the police station (20% bail, long guns taken). Both fade the screen to grayscale.

### The city (section 3)
- **Size:** a 16×16-block island (about 760 m across) with beaches and sea.
- **Districts:**
  - Downtown: glass towers on podiums, with setbacks and antennas.
  - Commercial: brick and plaster mid-rises with lit shopfronts and rooftop water tanks.
  - Suburbs: houses with pitched roofs, chimneys, yards and driveways.
  - Industrial port: warehouses and stacked shipping containers.
  - Parks with fountains and benches.
- **Street details:** lane markings, crosswalks and stop lines, streetlights, street trees, hydrants, bins, benches.
- **Traffic lights:** they run on a 16 s cycle, and AI traffic stops at red.
- **Performance:**
  - Static geometry is merged per 176 m chunk and street furniture is instanced per chunk, which keeps it to roughly 850 draw calls.
  - Obstacles sit in a 20 m grid for fast collision and line-of-sight checks.
  - Distant people skip shadows and are hidden beyond 150 m.
  - NPCs only spawn out of the player's view.
- **Looks:** a physical sky with matching reflections, filmic tone mapping, sun shadows centred on the player, and generated textures for asphalt, concrete, glass, brick, siding and metal.

### People (section 6)
- **Bodies:** each person is built with joints (hips, knees, shoulders, elbows, neck), a painted face, and different hairstyles and outfits.
- **Variety:** height, build, posture, stride and arm swing differ per person.
- **Movement:**
  - Natural walk and run cycles, weight shifts and breathing at idle.
  - Two-handed aiming that follows the camera's pitch, a boxing guard and punch combos.
  - Flinching, hands-up surrenders, panicked fleeing.
  - Falls that topple and go limp, knockdowns followed by getting back up.

---

## 2. Tech stack

| Layer | Choice |
|---|---|
| Rendering | Three.js r160 via an import map: core, `BufferGeometryUtils`, post-processing passes; the sky is a custom shader (build 13) |
| Simulation | Plain JS on a 2D plane (x, z) |
| Audio | Web Audio API, all sounds generated in code |
| UI | HTML/CSS HUD, a 2D canvas overlay (crosshair, health bars), a canvas minimap |
| Hosting | Any static host: GitHub Pages, Netlify, Cloudflare Pages |

**Debug handle** (`window.game` in the browser console):
- `step(n)`: advance n frames
- `look(yaw, pitch)`: point the camera
- `aimAt(x, z)`: aim at a world position
- `setHeat(v)`: set the wanted level
- `cam(px,py,pz, tx,ty,tz)`: free camera
- `info()`: render stats

---

## 3. Roadmap

**Done:**
1. Sandbox foundation
2. Vehicles and combat
3. Crime loop
4. Third-person rewrite, bigger city and visual overhaul

**Next ideas:**
- Save the game to `localStorage`.
- Missions (getaway timers, car deliveries).
- A day and night cycle with working streetlights and headlights.
- Somewhere to spend money: weapons, armour, a paint shop that clears your stars.
- Rigged glTF character models.
- Move the code to Vite modules along the 15 section markers.
