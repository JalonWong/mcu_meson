# Meson Cross compilation for MCUs

Cross files for [Meson build system](https://mesonbuild.com).

## Usage
1. Get python wheel from (release page)(https://github.com/JalonWong/mcu_meson/releases)
2. `pip install ./mcu_meson_setup-xxx.whl`
3. Copy [example/setup.py](example/setup.py) to your project, and modify it.
4. Run `python setup.py`
  1. You can see options via `python setup.py --h`
5. Use meson

See also [example](example).

## Known issues
- Currently, armclang doesn't work. It needs this [PR](https://github.com/mesonbuild/meson/pull/15426)
