import argparse
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path


def green(s: str) -> str:
    return f"\033[1;32m{s}\033[0m"


def red(s: str) -> str:
    return f"\033[1;31m{s}\033[0m"


def blue(s: str) -> str:
    return f"\033[1;34m{s}\033[0m"


def find_path(cmd: str) -> str | None:
    if platform.system() == "Windows":
        PATH = os.environ["PATH"].split(";")
        cmd += ".exe"
    else:
        PATH = os.environ["PATH"].split(":")

    for P in PATH:
        p = Path(P).joinpath(cmd)
        if p.exists():
            print(green("Found:"), p, flush=True)
            subprocess.run([p, "--version"])
            return Path(P).as_posix()[:-3]

    print(red("Can not find:"), cmd, flush=True)
    return None


def write_path(file: Path, gcc_path: str | None) -> None:
    if gcc_path:
        p = Path(gcc_path)
        if p.name != "bin":
            p = p.joinpath("bin")
        path = p.as_posix()[:-3]
    else:
        tmp = find_path("arm-none-eabi-gcc")
        if tmp is None:
            exit(1)
        path = tmp

    text = re.sub(r"cross_toolchain = '[\S]+'", f"cross_toolchain = '{path}'", file.read_text())
    file.write_text(text)


def setup(cress_files: list[str], msvc: bool) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--native", help="Use the native toolchain of build machine", action="store_true"
    )
    parser.add_argument("--gcc_path", help="Path of gcc-arm-none-eabi", type=str)
    opts = parser.parse_args()

    if os.path.exists("builddir"):
        shutil.rmtree("builddir")

    if opts.native:
        cross_list = []
    else:
        write_path(Path(cress_files[0]), opts.gcc_path)
        cross_list = [f"--cross-file={f}" for f in cress_files]

    cmd = "meson setup builddir".split() + cross_list
    if msvc and platform.system() == "Windows":
        cmd += ["--vsenv"]
    print(green("Run:"), " ".join(cmd), flush=True)
    subprocess.run(cmd)


if __name__ == "__main__":
    setup(["gcc-arm-none-eabi.ini", "cortex-m4.ini"], True)
