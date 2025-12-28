from mcu_meson_setup import setup

setup("builddir-native", vsenv=True)
setup(
    "builddir",
    ["main:gcc-arm-none-eabi.ini", "main:gcc-cortex-m3.ini"],
    link_script="src/my_link.ld",
    output_map="app.map",
)
# setup(
#     "builddir",
#     ["../gcc-arm-none-eabi.ini", "../gcc-cortex-m3.ini"],
#     link_script="src/my_link.ld",
#     output_map="app.map",
#     wipe=True,
# )
# setup(
#     "builddir",
#     ["main:armclang.ini", "tag:v0.3.0:clang-cortex-m3.ini"],
#     link_script="src/my_link.sct",
#     output_map="app.map",
# )
