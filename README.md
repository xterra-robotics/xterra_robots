# xterra_robots

`xterra_robots` stores robot description assets used across the xterra stack. It is the source of URDFs, MuJoCo scenes, and meshes consumed by projects such as `xterra_sim`, `xterra_dynamics`, and `xterra_ros2`.

## How to use it

This repository is not a CMake package. Tools locate models through `XTERRA_ROBOTS_PATH`.

```bash
export XTERRA_ROBOTS_PATH=/path/to/xterra_robots
```

Example paths:

```text
$XTERRA_ROBOTS_PATH/models/dhav1_description/urdf/dhav1_description.urdf
$XTERRA_ROBOTS_PATH/models/dhav1_description/mujoco/scene.xml
```

## Available model directories

- `models/dhav1_description/`
- `models/dhav1w_description/`
- `models/m2_metal_description/`
- `models/Scorp_URDF/`
- `models/Scorp_URDF_2/`

In normal use, the main models are:

- `dhav1_description` (12-motor quadruped)
- `dhav1w_description` (16-motor quadruped + foot-wheels — branch `feat/dhav1w`)
- `m2_metal_description`
- `Scorp_URDF`

## Expected layout

Most consumers expect robot assets under this structure:

```text
models/<robot_name>/
├── urdf/
├── mujoco/
├── meshes/
└── config/<robot_name>.yaml      # canonical robot config (optional)
```

The `config/<robot_name>.yaml` file follows the schema in
[`robot_config_template.yaml`](robot_config_template.yaml) at the repo root —
a single source of truth for poses (sleep, stand), per-group joint limits,
inertial properties, actuator gains, RL/MBC tuning, safety thresholds, and
the hardware motor map. Consumers that have migrated read it via
`XTERRA_ROBOTS_PATH`-relative paths so a robot's URDF, meshes, and config
travel as one bundle.

Examples in this repo:

- `dhav1_description` has `urdf/`, `mujoco/`, and `meshes/`
- `dhav1w_description` has `urdf/`, `mujoco/`, `meshes/`, and
  `config/dhav1w.yaml` (canonical schema; carries the calibrated sleep
  pose and spawn-hold gains)
- `m2_metal_description` has `urdf/`, `mujoco/`, and `meshes/`
- `Scorp_URDF_2` has `urdf/` and `meshes/`, but no MuJoCo scene in the checked in layout

## Consumers

- `xterra_sim`, resolves named robots such as `dhav1`, `dhav1w`, and
  `m2_metal`. Reads `poses.sleep.q` and `actuators.sleep_kp/kd` from
  `config/<robot>.yaml` when `sim.xterra_robots_config:` is set, so spawn
  pose and gains stay in lock-step with the controller.
- `xterra_dynamics` tests and examples, loads URDFs from this repo
- `xterra_ros2`, uses `XTERRA_ROBOTS_PATH` to find robot descriptions for example nodes

## Notes

There are also archive files and historical exports under `models/`. If you are wiring up code, prefer the description directories above instead of the zip files.
