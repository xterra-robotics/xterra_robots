# dhav1w — DHAV v1.3 wheeled

> **This directory was updated in place.** The previous model is preserved verbatim
> under [`v0/`](v0/) as a complete snapshot (`urdf/`, `mujoco/`, `meshes/`, `config/`,
> `launch/`, `CMakeLists.txt`, `package.xml`). Nothing in `v0/` was altered — it is a
> rollback point, and `v0/mujoco/mjmodel.xml` is the old compiled dump.
>
> Carried forward unchanged from the old model into the top level:
> `CMakeLists.txt`, `package.xml`, `launch/`,
> `config/joint_names_dhav1w_description.yaml`, and the two non-stair scenes
> `mujoco/uneven_scene .xml` and `mujoco/scene_big_uneven.xml`.
>
> One pre-existing break was fixed while carrying it forward:
> `scene_big_uneven.xml` failed to load in the old model too, because MuJoCo resolves
> `<hfield file=...>` relative to `meshdir` (`../meshes/`) but `terrain_big_world.png`
> sat in `mujoco/`. The png now lives in `meshes/`; `v0/` keeps the original layout.

Source CAD export: `XTR_Dummy_Wheeled_DHAV_1.3_4 - V1.1` (SW2URDF 1.6.0-4-g7f85cfe,
exported 2026-08-19), robot name `XTR_Dummy_Wheeled_DHAV_1.3_4`.

The raw export is **not** used verbatim. This document records every deviation so
each one can be checked independently.

## Method used for the inertia corrections

The CAD inertia **magnitudes** are authoritative — the STL meshes are exported with
internal parts stripped, so a mesh-derived inertia has the wrong magnitude. The STL
meshes *are* authoritative for **signs and principal-axis directions**, since those
follow from the outer geometry. Every correction below takes magnitudes from CAD and
signs/orientation from the mesh.

Mesh inertias were computed by direct closed-mesh integration (divergence-theorem
tetrahedron sum) at uniform density, scaled to the CAD mass.

## 1. Calf inertia — wrong pose (fixed)

The exported calf tensor is expressed in the wrong frame. Its minimum-inertia
(long) axis sits **58.5° away from +z**, whereas the calf geometry's long axis is
**3.7° from +z**:

| | ixx | ixy | ixz | iyy | iyz | izz |
|---|---|---|---|---|---|---|
| CAD export | 0.00127095 | -0.00002023 | **-0.00161981** | 0.00408761 | 0.00001266 | 0.00291971 |
| corrected (FL/RL) | 0.00389888 | 0.00000698 | 0.00021114 | 0.00408667 | 0.00010058 | **0.00029272** |

The error is a **pure frame rotation about the knee axis**. The rotation taking the
mesh's principal frame to the exported tensor's principal frame is **62.6° about an
axis that is 98.3 % aligned with +y** — and `+y` is exactly the calf joint's own
rotation axis. The CAD/mesh principal-moment ratios are also consistent across all
three axes (1.369 / 1.269 / 1.282, a 7.8 % spread, which is just non-uniform density).
A rotation about the joint axis with consistent magnitudes is the signature of a tensor
written in the part's own frame at some assembly angle rather than in the link frame —
not of noise or corrupt data.

Fix: the frame-invariant CAD principal moments `[2.778e-4, 3.910e-3, 4.090e-3]` were
kept and re-expressed on the calf mesh's principal-axis frame. Ordering both the moments and
the mesh axes ascending pairs them unambiguously, and the consistent ratios above
confirm the pairing is not silently permuted. Verified after the rebuild: the principal
moments match the CAD export to 3.9e-9, and the rebuilt long axis matches the mesh long
axis to 1e-4 degrees. `izz` is now the small one, as it must be for a link that is long
in z.

Left/right calves are exact mirrors (`ixy`, `iyz` negated), which the raw export was
not: it gave both sides identical off-diagonals.

## 2. Thigh inertia — wrong left/right symmetry (fixed)

The export gave **all four** thighs identical off-diagonals, so the left thighs were
not mirrored. The meshes show the correct signs — left `(ixy, ixz, iyz) = (+, −, +)`,
right `(−, −, −)`:

| | ixy | ixz | iyz |
|---|---|---|---|
| CAD export (all four) | -0.00012487 | +0.00069759 | -0.00099393 |
| corrected FL, RL | **+0.00012487** | **-0.00069759** | **+0.00099393** |
| corrected FR, RR | -0.00012487 | **-0.00069759** | -0.00099393 |

Two independent checks support the `ixz` sign flip: it moves the tensor's long axis
from 10.2° to 5.2° away from the mesh's long axis, and the mesh gives `ixz < 0` on
both sides (`ixz` is invariant under a left/right mirror, so it must match on both).

**`FL_thigh_link` `ixz` in the raw export is `0.01255517`** — larger than `ixx` and
`iyy`, which makes the tensor indefinite (eigenvalue `-0.0083`, i.e. negative inertia).
The other three thighs carry `0.00069759`. This is corrupt data in the export and is
replaced by the corrected value above.

## 3. Hip inertia — one sign slip, and noise zeroed

* `RR_hip_link` `ixy` was `+0.00000955` in the export. `RR` is a 180° rotation of `FL`
  about z, under which `ixy` is invariant, so it must match `FL`'s `-0.00000954`. The
  mesh agrees. Corrected.
* The hip part is symmetric about `z = 0` (mesh COM z ≈ -9e-7), so `ixz` and `iyz` are
  exactly zero. The export's `1.2e-7` / `4e-8` are numerical noise and are zeroed;
  they also broke mirror symmetry (`ixz` flipped between FL and FR when it should not).

## 4. Naming / structural fixes to the raw export

* Joints `FL_thigh_link` and `RR_thigh_link` are **named as links** in the export.
  Renamed to `FL_thigh_joint` / `RR_thigh_joint`.
* Root link `base_link` → `base`, and meshes renamed (`base_link.STL` → `torso.STL`,
  `FL_hip_link.STL` → `FL_hip.STL`, …) to match `dhav1_description` / `dhav1w_description`
  so the model is drop-in for the existing tooling.
* Mesh geometry is copied byte-for-byte from the export; only filenames changed.

## 5. Verification performed

* Every inertia tensor is positive-definite and satisfies the triangle inequality.
* Left/right pairs are exact mirrors in the inertia tensor (see the caveat below on
  thigh COM).
* URDF and MuJoCo XML carry identical mass, COM and inertia — including the inertial
  frame *orientation* (`body_iquat` matches to 0.0), which rules out a transposed
  `fullinertia` component order.
* All 29 MuJoCo XMLs compile; the model settles under gravity without NaNs.
* 62,500-pose sweep over the full hip x thigh x calf range: no same-leg self-collision.
* Both keyframes rest exactly on the floor with zero penetrating contacts.
* Reviewed by codex, which independently reproduced the mesh integration and confirmed
  the calf frame error, the thigh sign pattern, the indefinite raw FL thigh tensor, the
  RR hip sign slip, and the URDF/MJCF agreement. Its findings on the config limits,
  keyframe heights, IMU frame, per-side clearance and the parent/child primitive
  overlap are all folded in above.

---

# Things to check manually — deliberate judgement calls and CAD issues

These were **not** silently resolved.

### A. Thigh left/right COM and geometry genuinely differ in the CAD

The inertia *tensor* is now mirrored, but the COMs are not, because the two CAD parts
really are different:

| | COM x | COM y | COM z | mesh triangles |
|---|---|---|---|---|
| FL / RL thigh | -0.00746 | -0.00751 | **-0.07423** | 1726 |
| FR / RR thigh | -0.00762 | +0.00678 | **-0.07658** | 910 |

The meshes reproduce exactly this difference, so it is not an export artefact. The
right thigh mesh has ~half the triangles and is 1.35 mm shorter in its outboard
direction. **This looks like the two sides are at different CAD revisions, or different
internals were stripped from each side.** The CAD joint origins compensate (see B), so
the assembled inboard faces line up. Worth confirming with the mechanical team which
side is current; the COMs were left as exported rather than fabricating symmetry the
geometry does not have.

### B. Asymmetric thigh joint origin

`FL/RL_thigh_joint` is at `y = +0.09435`, `FR/RR_thigh_joint` at `y = -0.09300` —
a **1.35 mm left/right asymmetry**, exactly cancelling the mesh difference in (A).
`dhav1w_description` used `0.09345` on both sides. Left as exported (kinematics were
outside the scope of the inertia fix), but an asymmetric leg spacing will bias a
learned policy and should be resolved.

### C. Knee sign convention and range kept from the repo, not the CAD

The export gives `[-0.21276, +1.7972]` for every calf joint. This repo (`dhav1`,
`dhav1w`) uses `[-2.80, -0.212]`, and the hardware-calibrated sleep pose in
`config/dhav1w.yaml` is `calf = -2.630`, which the CAD range would forbid. The repo
convention is kept. Note the shared `-0.212` endpoint — the CAD limit looks like the
same joint expressed with the opposite sign convention, but the other endpoint
(1.797 vs 2.80) does not correspond, so **the usable knee travel needs confirming.**

Hip and thigh limits *were* taken from the new CAD (`±0.8378`, `[-1.7169, 2.5758]`);
they agree with the repo values to within ~1°. Efforts are the new CAD's
(40 / 40 / 80 / 14 N·m). Velocities are **not** the CAD's — see (J): the export's
10 rad/s contradicts the actuator change and was replaced by 6.8 rad/s.

### D. Base inertia left exactly as exported

`ixy = -0.00023907` and `iyz = 0.00001027` are non-zero while the base COM y is
exactly 0, which is a slightly odd combination for a body that should be near-symmetric
about the xz plane. They are small (0.26 % of `iyy`) and plausible for asymmetric
internals, so nothing was changed. Flagging in case the base was exported with
components stripped.

### E. Wheel is the native DHAV 1.3 wheel, not the go2w wheel

`dhav1w_description` had its wheels swapped for go2w wheels (r = 0.086 m, with a
`pos="0 ∓0.048 0"` visual offset). This model uses the native exported wheel:
**r = 0.077 m, 59 mm overall width** (52 mm of which is tread — see F), no visual
offset, and the wheel joint origin from CAD (`y = ±0.04597`, `z = -0.22088`; dhav1w
used `y = ±0.043`). Standing height at full leg extension is therefore **0.5479 m**,
~8 mm lower than dhav1w's go2w-wheeled 0.5569 m.

### F. Wheel collision cylinder is the tread, not the whole wheel

The wheel mesh is 59 mm wide overall, but the material at contact radius
(> 0.070 m) spans exactly **y in [-0.026, +0.026], centred on y = 0** — the outer
7 mm on the inboard side is the hub flange, at a radius that never touches ground.
The collision cylinder is therefore `size="0.077 0.026"` at `pos="0 0 0"`
(**52 mm tread width, radius 0.077 m**), which is the real tread, not a fudge.

This also resolves a self-collision. The hip collision cylinder inherited from
`dhav1w` (`r = 0.046`, half-length `0.05`, at `y = +-0.06` in the hip frame) reaches
`y = +-0.11`, well past the hip mesh which ends at `y = 0.0373`; it is deliberately
oversized to cover the thigh motor housing. Using the *full* 59 mm wheel width
centred on the mesh centroid (`y = -0.0035`) made the wheel overlap that cylinder:

| wheel collision | FL / RL | FR / RR |
|---|---|---|
| 59 mm wide, hub-centred (`pos y = -0.0035`) | **-2.68 mm** (overlap) | **-4.03 mm** (overlap) |
| 52 mm tread, centred on `y = 0` | **+4.32 mm** | **+2.97 mm** |

Note the two sides differ because the thigh joint origin is asymmetric (see B), so
any clearance figure has to be quoted per side. Because the hip and knee joints rotate
about x and y, this axial overlap was **constant in every configuration** — it showed
up as a permanent same-leg contact, most visible with the knee folded near -2.74 rad.

Verified after the change: 62,500 poses (25^3 per leg, all four legs) spanning the full
hip x thigh x calf ranges produce **zero same-leg contacts**.

### G. Thigh and calf collision primitives overlap at the very end of knee travel

`*_thigh_collision2` (box) and `*_calf_collision3` (cylinder) interpenetrate for the
last ~0.02 rad of knee travel: onset near **-2.778 rad**, reaching **4.2 mm** at the
-2.80 limit. MuJoCo never generates this contact because the thigh is the calf's parent
body and `filterparent` is on by default, so it has **no effect in MuJoCo**. It would
show up in a non-MuJoCo collision checker (a motion planner reading the URDF, or a sim
with parent filtering disabled). The hardware sleep pose (-2.630) is clear by ~13 mm.

Inherited from `dhav1w`'s tuned primitives, not introduced here.

### H. Collision primitives otherwise carried over unchanged

The hip / thigh / calf / torso meshes are *geometrically* identical to
`dhav1w_description` — same triangle sets, and volume / COM / inertia agree to machine
precision (1e-19 or better). They are **not** byte-identical: only `torso.STL` and
`RR_calf.STL` hash the same, the rest differ in STL triangle ordering and normals only.
Because the geometry is unchanged, its tuned collision primitives were reused verbatim.
Only the wheel collision cylinder was changed (see F). Worth an eyeball in the viewer.

### I. `config/dhav1w.yaml` is inherited and largely un-tuned

Poses, gains, safety thresholds and the `inertial:` lumped SRB model are copied from
`dhav1w`. What *was* corrected:

* `position_lower` / `position_upper`: dhav1w carried calf limits `[1.79, 7.50]`, in the
  opposite sign convention to the URDF/MuJoCo, and its own sleep pose (-2.630) violated
  them. Now matched exactly to the URDF/MJCF.
* `contact_frames`: referenced non-existent `*_wheel_link` names; now `*_wheel`.
* `imu_frame`: was `base_link`, which no longer exists; now `base`.

`velocity_max` / `effort_max` are deliberately left as dhav1w's motor limits and do
*not* equal the URDF's CAD-exported values — flagged in the file. `hip_offsets`
(`[0.19, 0.11, 0]`) does not match the URDF hip joints (`[0.2235, 0.0535, 0]`) — that
discrepancy is inherited from `dhav1w` and was left alone.
### J. Actuator change: 40 N·m output on the same motor (gear ratio ×1.176)

DHAV 1.3 fits a new hip/thigh/calf actuator rated **40 N·m** output (**80 N·m** at the
knee) against **34 / 68 N·m** on the previous robot, using the **same motor**. Only the
reduction changed:

    k = 40/34 = 68/80 inverse = 1.176471

With motor torque and motor speed unchanged, three quantities follow rigorously:

| quantity | law | v0 | now |
|---|---|---|---|
| output torque | × k | 34 / 68 N·m | **40 / 80 N·m** (already in the CAD export) |
| output velocity | × 1/k | 8 rad/s (URDF) | **6.8 rad/s** |
| output velocity | × 1/k | 21.0 rad/s (config) | **17.85 rad/s** |
| motor-limit torque | × k | 23.7 / 45.4 N·m (config) | **27.88 / 53.41 N·m** |
| reflected rotor inertia | × k² = 1.384083 | armature 0.01 | **armature 0.013841** |

The reflected-inertia term is the one that is easy to miss: `armature = J_rotor × N²`,
so a 17.6 % ratio increase is a **38.4 % increase in reflected inertia**. It changes the
effective joint mass the controller sees, and at these ratios it is comparable to the
link inertia itself, so leaving it at the old value would misrepresent the plant.

**The CAD export's velocity numbers are wrong and were overridden.** The export declares
`velocity="10"` for hip/thigh/calf, i.e. *faster* than the old robot's 8 rad/s. With the
same motor and more reduction the joint must get **slower**, not faster, so those are
exporter placeholders. The URDF now carries 6.8 rad/s.

Not touched — the wheel actuator is a different unit, unchanged at 14 N·m across both
revisions: wheel velocity (5 rad/s), effort (14 N·m) and armature (0.01) all stand.

Also not scaled: MuJoCo `damping` (0.1) and `frictionloss` (0.2). Motor-side viscous
damping would scale by k² and Coulomb friction by k, but these are round numbers shared
with `dhav1` and with the *wheel* joint, so they are plainly hand-picked stabilisation
values rather than identified parameters. Scaling a placeholder by a precise factor
would be false precision; they are left alone and flagged here instead.

**Needed from the mechanical side:** the absolute reduction ratios. Nothing in this repo
records them, so `config/dhav1w.yaml` carries `actuators.gearing.ratio: null` with the
scale factors alongside. The `armature` baseline of 0.01 is likewise an unmeasured
placeholder inherited from `dhav1` — the *scaling* applied here is correct, but the
absolute reflected inertia still needs measuring. Also worth confirming what 23.7 /
45.4 N·m represent (continuous rating?) versus the 34 / 68 N·m peak, since the two pairs
have never been consistent in this config.
