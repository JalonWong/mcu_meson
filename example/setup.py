from mcu_meson_setup import setup

setup("builddir", ["../gcc-arm-none-eabi.ini", "../gcc-cortex-m3.ini"])
# setup("builddir", ["../armclang.ini", "../clang-cortex-m3.ini"])
# setup(
#     "builddir",
#     [
#         "https://raw.githubusercontent.com/JalonWong/mcu_meson/refs/heads/main/gcc-arm-none-eabi.ini",
#         "https://raw.githubusercontent.com/JalonWong/mcu_meson/refs/heads/main/gcc-cortex-m3.ini",
#     ],
# )
