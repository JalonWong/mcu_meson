# Meson Cross compilation for MCUs

Cross files of gcc-arm-none-eabi and ARMClang for [Meson build system](https://mesonbuild.com).

## Usage
1. Get python wheel from [release page](https://github.com/JalonWong/mcu_meson/releases)
2. `pip install ./mcu_meson_setup-*.whl`
3. Copy [example/setup.py](example/setup.py) to your project, and modify it.
    1. the link of cross files can be a:
        - URL link: `https://*`
        - local relative path: `../*`
        - main branch of this repository: `main:gcc-arm-none-eabi.ini`
        - tag of this repository: `tag:v0.3.0:gcc-arm-none-eabi.ini`
4. Run `python setup.py`
    1. You can see options via `python setup.py --h`
    2. The extra arguments will be passed to meson `python setup.py --debug`
    3. You can also pass arguments via the function `setup(args=["--debug"])`

See also [example](example).

## Known issues
- Currently, armclang doesn't work. It needs this [PR](https://github.com/mesonbuild/meson/pull/15426)
