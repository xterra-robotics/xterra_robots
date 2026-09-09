# dhav1 — DHAV v1.3 legged

> **This directory was updated in place (2026-09-03).** The previous model is
> preserved verbatim under [`v0/`](v0/) as a complete snapshot (`urdf/`,
> `mujoco/`, `meshes/`, `config/`). Nothing in `v0/` was altered — it is a
> rollback point.
>
> One pre-existing break was fixed while carrying it forward:
> `scene_big_uneven.xml` failed to load in the old model too, because MuJoCo
> resolves `<hfield file=...>` relative to `meshdir` (`../meshes/`) but
> `terrain_big_world.png` sat in `mujoco/`. The png now lives in `meshes/`;
> `v0/` keeps the original layout. This is the same fix dhav1w v1.3 needed.

Sources used, in order of authority:

| source | what it is | what it is trusted for |
|---|---|---|
| `XTR_Dummy_DHAV_1.3_L_1` | SW2URDF 1.6.0-4-g7f85cfe, exported **2026-08-27** | COMs, joint frames, inertia **signs** |
| `dhav1w_description` v1.3 | Aug-27 wheeled CAD, materials assigned, operator-confirmed | base / hip / thigh **mass + magnitudes** |
| original `dhav1` CAD export (git `527c115`, `0dd1250`) | materials assigned (calf ρ=1043, foot ρ=783) | calf / foot **mass + magnitudes** |
| the STL meshes | outer geometry | **signs and principal-axis directions** |

Total mass **17.061 → 17.808 kg**.

---

# 0. The Aug-27 legged export has no material assignment — its masses are unusable

Every part in `XTR_Dummy_DHAV_1.3_L_1` comes out at **1000 kg/m³**, SolidWorks'
default. Measured against the STL volumes:

| part | mesh volume (m³) | export mass (kg) | implied density |
|---|---|---|---|
| base_link | 8.5943e-04 | 0.859852 | **1000.5** |
| FL_hip_link | 8.1711e-05 | 0.081756 | **1000.6** |
| FL_thigh_link | 1.1335e-04 | 0.112340 | **991.1** |
| FR_thigh_link | 1.1577e-04 | 0.115837 | **1000.6** |
| FL_calf_link | 2.0992e-04 | 0.209449 | **997.8** |
| FL_foot | 8.9426e-05 | 0.089574 | **1001.7** |

Confirmed independently by integrating the STLs directly (divergence-theorem
tetrahedron sum). The export's normalised inertia `I/m` matches the
**uniform-density mesh** `I/V` to 0.3–0.5 % on every link — e.g. the base:

| | ixx | ixy | ixz | iyy | iyz | izz |
|---|---|---|---|---|---|---|
| mesh `I/V` | 8.444e-03 | -1.785e-08 | -1.312e-08 | 1.444e-02 | 1.725e-09 | 1.764e-02 |
| export `I/m` | 8.448e-03 | 4.255e-10 | -5.319e-19 | 1.444e-02 | 2.010e-18 | 1.763e-02 |
| real part (dhav1w) `I/m` | 4.574e-03 | -1.752e-05 | -9.441e-06 | 1.204e-02 | 3.500e-06 | 1.476e-02 |

Total export mass is **2.839 kg**. The magnitudes are discarded wholesale.

**What the export IS good for:** its COMs, joint frames and inertia **signs** are
correct — see §1, where it is one of the three sources that agree.

**Geometry is unchanged from the model already in the repo.** md5 of every
`base/hip/thigh/calf` STL is byte-identical to `v0/meshes/`. The four `*_foot.STL`
differ in bytes only: same 3034 triangles, same volume to 1e-10, same COM to
<1e-6 m, same bbox. So no mesh was replaced.

# 1. Inertia signs — three sources agree, the two files in the repo did not

Every off-diagonal sign was audited against the mesh. `X` marks disagreement:

| link | source | ixy | ixz | iyz |
|---|---|---|---|---|
| FL_hip | mesh / Aug-27 export | − | ~0 | ~0 |
| | **dhav1w v1.3** | **+ X** | | |
| | v0 dhav1 (FL) | − | | |
| FL_thigh | mesh / Aug-27 export / original CAD export | + | − | + |
| | **dhav1w v1.3** | **− X** | **+ X** | **− X** |
| | **v0 dhav1** | **− X** | **+ X** | **− X** |
| FL_calf | mesh / Aug-27 export / original CAD export | 0 | + | 0 |
| | **v0 dhav1** | | **− X** | |
| FL_foot | mesh / Aug-27 export / original CAD export | 0 | + | 0 |
| | **v0 dhav1** | | **− X** | |

The calf and foot sign errors were **introduced by this repo**, not by CAD. Commit
`8306ccf` "Updated mass parameters and basic collision shapes" hand-edited values
that `0dd1250` had correct:

| | calf COM | calf ixz | foot ixz | calf mass |
|---|---|---|---|---|
| `0dd1250` (correct) | `0.024118, 0, -0.13096` | **+0.0002523** | **+2.4e-06** | 0.2189873 |
| `8306ccf` (v0, wrong) | `0.01887, 0.0000357, -0.12` | **-0.000251** | **-2e-06** | 0.215 |

`8306ccf` also reverted the calf COM to a stale frame — the Aug-27 export gives
`0.0241186, ~0, -0.1309662`, matching `0dd1250` to **1e-6 m**.

**Independent confirmation the corrections are right.** Angle between each
tensor's minimum-inertia (long) axis and the mesh's:

| link | v0 dhav1 | dhav1w v1.3 | **this model** |
|---|---|---|---|
| FL_thigh | 12.61° | 13.29° | **4.52°** |
| FL_calf | 17.47° | — | **0.76°** |
| FL_foot | 57.78° | — | **0.50°** |
| FL_hip | 1.15° | 3.22° | **0.57°** |

## What was actually written, per link

* **base** — dhav1w v1.3 verbatim. The mesh cannot inform base signs (its
  off-diagonals are ~1e-8, i.e. the shell is symmetric and the internals carry
  all the asymmetry), so there is no better source. See (A).
* **hip** — dhav1w v1.3 magnitudes; `ixy` **sign flipped** to match the mesh and
  the Aug-27 export (both negative for FL, dhav1w is positive). `ixz`/`iyz` set
  **exactly zero**: the part is symmetric about z=0 (mesh COM z ≈ -1e-6) so they
  must vanish, and the ~1e-7 values in both files are noise that also broke
  mirror symmetry.
* **thigh** — dhav1w v1.3 magnitudes; all three off-diagonals set to the mesh
  pattern FL = `(ixy +, ixz −, iyz +)`. This restores exactly the pattern
  dhav1w's own NOTES §2 prescribed and which its Aug-27 re-base then lost.
* **calf, foot** — the original dhav1 CAD export verbatim (it was already
  correct); COM from the Aug-27 export.
* **left/right** — FR/RR are exact mirrors of FL/RL by construction
  (`com_y`, `ixy`, `iyz` negated). Front/rear are **not** mirrored for
  thigh/calf/foot — the Aug-27 export confirms RL ≡ FL exactly — but the hip
  **is** x-mirrored front-to-rear. v0 had the thigh COM x-mirrored front/rear,
  which contradicts the CAD.
* **all four feet unified** — a quadruped foot is not a handed part. The export
  ships FL≡RR and FR≡RL differing by 0.37 mm in COM x at identical volume, which
  is a tessellation artefact.

# 2. Verification performed

* All 17 links positive-definite and satisfying the triangle inequality.
* Left/right mirror error **exactly 0.0**.
* URDF and MJCF carry identical mass, COM and inertia — including the inertial
  frame *orientation* (full tensor reconstructed from MuJoCo's `body_iquat` +
  `diaginertia`; max relative error 2.2e-07, which is float round-trip only).
* All **32** MuJoCo XMLs compile.
* Both keyframes rest on the floor with **zero penetrating contacts**.
* 62,500-pose sweep (25³ per leg × 4 legs) over the full hip × thigh × calf range.
  The collision model is v0's (see C), so v0's known primitive overlaps are
  present and unchanged: **11,356 same-leg penetrating contacts, worst
  -15.079 mm** (`*_hip_collision` ↔ `*_calf_collision3`).
* Both keyframes rest on the floor with **zero floor penetration**. The sleep
  pose carries 12 self-overlap contacts (worst -0.885 mm), which are the same
  hip↔calf primitive overlap — see (D).

---

# Things to check manually — deliberate judgement calls and CAD issues

### A. `dhav1w_description` v1.3 disagrees with the mesh on hip and thigh signs

**Not changed — dhav1w was explicitly out of scope.** But §1 shows dhav1w v1.3
carries FL hip `ixy = +0.00001172` and FL thigh `(ixy −, ixz +, iyz −)`, while
the mesh, the Aug-27 legged export (same CAD session, byte-identical parts) and
the original dhav1 CAD export all say the opposite. dhav1w's own NOTES §2
prescribes the pattern this model now uses; the Aug-27 re-base appears to have
dropped it on the assumption that "the new export did not reproduce those
defects". The wheeled Aug-27 raw export is not in the repo, so it cannot be
checked directly. **Worth re-auditing dhav1w against its raw export.**

### B. Base mass and inertia taken from the wheeled robot

The torso STL is byte-identical across dhav1, dhav1w and the Aug-27 export, and
the base COM z matches to 5e-7 m, so the shell is certainly the same part. The
**mass** (7.87906 kg) is nonetheless the *wheeled* robot's. If the legged
variant carries different internals — different battery, no wheel drivers in the
torso — this figure is wrong and only a materials-assigned legged export can
settle it. `ixy = -0.00013803` and `iyz = 0.00002758` are non-zero while base
COM y is exactly 0, which is odd for a near-symmetric body; small (0.15 % of
`iyy`) and left alone, same as dhav1w flagged.

### C. Collision model is v0's, restored on operator instruction

The collision primitives are **v0's, not refitted**. One decision had to be made
to get there: **v0's URDF and v0's MJCF did not carry the same primitives.** They
differed on five of the six families:

| primitive | v0 **URDF** | v0 **MJCF** | used here |
|---|---|---|---|
| hip cylinder | r 0.046, half-len 0.05, y ±0.06 | **r 0.055, half-len 0.0625, y ±0.05** | MJCF |
| thigh box 1 | 0.03×0.02×0.15 @ (-0.025,0,-0.13) | **0.04×0.04×0.15 @ (-0.02,0,-0.15)** | MJCF |
| thigh box 2 | 0.03×0.02×0.09 @ (0,0,-0.1), pitch 0.3 | **0.02×0.04×0.12 @ (0,0,-0.13), pitch 0.24** | MJCF |
| torso box | 0.3062 × 0.20 × **0.114** | 0.3062 × 0.20 × **0.10** | MJCF |
| foot sphere | r **0.03** @ (0.01, 0, 0.02) | r **0.025**, same centre | MJCF |
| calf cylinders, torso corner stubs | identical | identical | — |

**The MJCF values are used in both files**, because the MJCF is the model the
simulations actually ran, and because its hip cylinder is the closer fit to the
hip mesh (which reaches radius 0.0675, against the URDF cylinder's 0.046).
Verified geom-by-geom: the compiled collision model is now **identical to
`v0/mujoco/dhav1.xml`** in body, type, size, position and orientation for all 33
collision geoms. The URDF now agrees with it, which v0's did not.

*If the URDF numbers were the intended ones instead, this is a one-line change
per primitive — say so and it will be swapped.*

The only residual difference is the foot sphere's absolute position: it sits at
`(0.01, 0, 0.02)` in the foot frame in both v0 and here, but the foot link itself
moved 0.44 mm with the CAD joint origin (H), so the sphere's position in the calf
frame is `0.01` rather than v0's `0.00956`. That is the kinematic change, not a
collision change.

**Known limitation carried over from v0, unchanged:** the torso box spans only
z = ±0.05 while the torso mesh reaches z = -0.1075, so the lowest ~50 mm of the
torso has no collision geometry beyond the four corner stubs. A belly-grounding
event on a stair nose will not be detected between the stubs.

### D. The hip↔calf primitive overlap is real and is NOT filtered by MuJoCo

v0's hip cylinder is deliberately oversized — r 0.055, half-length 0.0625 at
y = ±0.05, so it spans y -0.0125…0.1125 in the hip frame — because it covers both
the hip link (mesh y -0.018…0.037) and the thigh actuator housing
(y 0.039…0.110). That bulge sits in the folded leg's path.

Measured over the 62,500-pose sweep: **`*_hip_collision` ↔ `*_calf_collision3`
overlaps by up to 15.1 mm**, and the hardware sleep pose (`calf = -2.720`) sits
in it at **-0.885 mm**.

**This matters more than the analogous note in dhav1w.** dhav1w's NOTES (G)
describes a thigh↔calf overlap that MuJoCo never generates, because the thigh is
the calf's **parent** and `filterparent` is on by default. Here the pair is
**hip ↔ calf**, i.e. grandparent/grandchild — `filterparent` does **not** apply,
so MuJoCo *does* generate these contacts. At the sleep pose that is a small
permanent contact force on all four legs.

The real geometry is clear at every pose: at full knee flexion the meshes are
apart by **+31.6 mm (foot↔hip)**, **+37.1 mm (calf↔hip)** and **+3.3 mm
(foot↔thigh)**. So the contact is purely a primitive artefact.

It is left in place because the collision model is v0's by instruction. If it
needs to go, the options are (a) shorten the hip cylinder to the hip link's own
extent — the calf/foot never enters y -0.018…0.037 at any pose, so that removes
the overlap completely — at the cost of the housing's lateral envelope, or
(b) add an explicit `<contact><exclude>` pair per leg, which keeps the envelope
and costs nothing in fidelity.

**Why the housing cannot simply be modelled at its true radius:** the calf nests
into the thigh housing with **+0.54 mm** real clearance at full knee flexion, so
any convex primitive enclosing that pocket collides permanently.

### E. Actuator change: 40 N·m output on the same motor (gear ratio ×1.176)

DHAV 1.3 fits the 40 N·m (80 N·m knee) actuator against 34 / 68 N·m before,
using the same motor — only the reduction changed, `k = 40/34 = 1.176471`.
Applied identically to dhav1w v1.3:

| quantity | law | v0 | now |
|---|---|---|---|
| output torque | × k | 34 / 68 N·m | **40 / 80 N·m** (in the CAD export) |
| output velocity | × 1/k | 30 rad/s (URDF) | **6.8 rad/s** — placeholder, see below |
| reflected rotor inertia | × k² = 1.384083 | armature 0.01 | **armature 0.013841** |

`armature = J_rotor × N²`, so a 17.6 % ratio increase is a **38.4 % increase in
reflected inertia** — at these ratios comparable to the link inertia itself.

**Every velocity figure in this repo is a placeholder.** The Aug-27 legged export
is the worst of the available sources — it declares **30 rad/s on FL/RL hip and
thigh but 10 rad/s on FR**, i.e. different limits on different legs of the same
robot. v0's URDF carried a flat 30 rad/s on hip/thigh and 10 on the calf, with
no stated basis. `config` carried 21.0 rad/s from a commercially available
robot's published spec. The files now carry 6.8 rad/s (URDF/MJCF) and
17.85 rad/s (config) so the k relationship is at least self-consistent, both
marked as placeholders. **What is certain regardless of baseline: the new
actuator's no-load joint speed is 0.85 × whatever the old one's was.**

Not scaled: MuJoCo `damping` (0.1) and `frictionloss` (0.2). Motor-side viscous
damping would scale by k² and Coulomb friction by k, but these are round numbers
shared with dhav1w and are plainly hand-picked stabilisation values, not
identified parameters. Scaling a placeholder by a precise factor is false
precision.

**Needed from the mechanical side:** the absolute reduction ratios, and the
`armature` baseline of 0.01 which is itself an unmeasured inherited placeholder.
The *scaling* applied here is correct; the absolute reflected inertia is not
known.

### F. Knee sign convention and range kept from the repo, not the CAD

The Aug-27 export gives `[-1.796, -0.212]` for every calf joint. v0's URDF
carried that, but v0's **MJCF used `[-2.80, -0.212]`** and `config/dhav1.yaml`'s
sleep pose is `calf = -2.720` — which the URDF's own range forbade. All three
now use `[-2.80, -0.212]`, matching dhav1w. Note the shared `-0.212` endpoint:
the CAD limit looks like the same joint expressed with the opposite sign
convention, but the other endpoint (1.796 vs 2.80) does not correspond, so
**the usable knee travel still needs confirming.**

Hip and thigh limits *were* taken from the new CAD (`±0.8378`,
`[-1.7169, 2.5758]`); they agree with v0's values to within ~1°.

### G. Asymmetric thigh joint origin in the CAD — symmetrised

The Aug-27 export still has `FL/RL_thigh_joint` at `y = +0.09435` and
`FR/RR_thigh_joint` at `y = -0.09300` — a **1.35 mm left/right asymmetry**, and
the right thigh mesh is a different revision (910 triangles vs 1726, COM 2.35 mm
different in z). This is the same unresolved CAD issue dhav1w v1.3 documented;
the Aug-27 export shows it was **never fixed upstream**.

Symmetrised to `y = ±0.09435` here, matching dhav1w's decision, and the right
thigh's inertia is mirrored from the left. v0 used `±0.09345` on both sides —
a third value, matching neither CAD side. **Worth confirming with the mechanical
team which thigh revision is current.**

### H. Foot collision sphere — v0's, and the two v0 files disagreed

v0's URDF used `r = 0.03` at `(0.01, 0, 0.02)` in the foot frame and v0's MJCF
`r = 0.025` at the same centre. Per (C) the MJCF value `r = 0.025` is used in
both files here.

Note what that radius implies: the sphere's lowest point is z = -0.005 against
the foot mesh's -0.008, so the collision surface sits **3 mm above** the visual
foot and the foot will appear to sink into the ground by that much. (v0's URDF
radius of 0.03 had the opposite sign of error: 2 mm below the mesh, so the foot
would float.) A least-squares fit to the mesh's contact surface gives
`r = 0.0315` at `(0.0152, 0, 0.0238)` — recorded here as the measured value, not
applied.

The foot **joint** origin did move to the CAD value `(0.0004778, 0, -0.27889)`
from v0's `(0, 0, -0.27872)`. That is kinematics, not collision.

### I. Keyframes

Both base heights re-solved so the lowest collision geom sits exactly on z = 0:
**stand 0.4074**, **sleep 0.1070**. v0's MJCF had no keyframes at all.

* The stand pose is **nose-down**: `config`'s rear thighs (0.87) against the
  front (0.65) sit the rear feet ~4.7 mm higher. Inherited, not changed.
* In the sleep pose the lowest geometry is a torso corner stub, so the robot
  rests on those rather than on its feet — consistent with the tucked pose
  (`thigh 1.153, calf -2.720`). The pose also sits inside the hip↔calf primitive
  overlap described in (D), at -0.885 mm on all four legs.

### J. `config/dhav1.yaml` corrections

| field | was | now |
|---|---|---|
| `position_lower/upper` | `[-0.863,-0.686,-2.818]` / `[0.863,3.829,-0.888]` | matched to URDF/MJCF |
| `effort_max` | `[34, 34, 68]` | `[40, 40, 80]` |
| `velocity_max` | `[21, 21, 21]` (foreign spec) | `[17.85, …]` placeholder |
| `total_mass` | `12.0` | `17.80831` (computed) |
| `inertial.inertia` diag | `[0.07, 0.26, 0.242]` | `[0.3119, 0.7616, 0.8400]` (computed) |
| `hip_offsets` | `[±0.19, ±0.11, 0]` | `[±0.2235, ±0.0535, 0]` |
| `contact_frames` | `FL_foot` … (no such link) | `FL_foot_link` … |
| `standing_height` / `stand.base_pos` | `0.3` / `0.45` | `0.4074` (solved) |
| `rl.action.scales_per_group` | `[0.2125, 0.2125, 0.425]` | `[0.25, 0.25, 0.5]` (follows effort_max) |

The old `inertial` block was **5–10× out** on every axis — the same foreign-spec
seeding dhav1w v1.3 identified. `safety.max_torque` (25 N·m) is left alone but
flagged in the file: it is below the 40 N·m rating and 31 % of the 80 N·m knee,
so it will saturate the knee well before the hardware limit.

`rl.action.scales_per_group` follows mechanically from `0.25 × effort_max /
stiffness`; **any policy trained against the old 34/68 N·m scaling must be
retrained or re-scaled.**

### K. Structural changes to be aware of

* The MJCF now has a **separate body per URDF link** (18 bodies incl. world,
  matching dhav1w's structure) instead of lumping each foot into its calf. Code
  that indexes MuJoCo bodies **by number** rather than by name will need
  updating; joint, actuator, sensor and site names are unchanged.
* `mujoco/dhav1.xml` gains a `<keyframe>` block. Collision geoms are v0's,
  unchanged (C).
* The 30 stair/terrain scene XMLs only `<include file="dhav1.xml"/>` and needed
  no edits.
