from setup_helper import setup

# setup(["gcc-arm-none-eabi.ini", "cortex-m4.ini"], True)
setup(
    [
        "https://raw.githubusercontent.com/JalonWong/mcu_meson/refs/heads/main/gcc-arm-none-eabi.ini",
        "https://raw.githubusercontent.com/JalonWong/mcu_meson/refs/heads/main/cortex-m4.ini",
    ],
    True,
)
