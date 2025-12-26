import argparse
import os
import platform
import re
import shutil
import subprocess
import urllib.request
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


def write_path(file: Path, arm_path: str | None) -> None:
    if str(file).endswith("gcc-arm-none-eabi.ini"):
        arm_cmd = "arm-none-eabi-gcc"
    else:
        arm_cmd = "armclang"

    if arm_path:
        p = Path(arm_path)
        if p.name != "bin":
            p = p.joinpath("bin")
        path = p.as_posix()[:-3]
    else:
        tmp = find_path(arm_cmd)
        if tmp is None:
            exit(1)
        path = tmp

    text = re.sub(r"cross_toolchain = '[\S]+'", f"cross_toolchain = '{path}'", file.read_text())
    file.write_text(text)


def download_files(cross_files: list[str]) -> list[str]:
    path = Path("cross_files")
    if not path.exists():
        os.mkdir(path)

    rst_list = []
    for f in cross_files:
        if f.startswith("http"):
            filename = path.joinpath(f.rsplit("/", maxsplit=1)[1])
            urllib.request.urlretrieve(f, filename)
            rst_list.append(str(filename))
        else:
            rst_list.append(f)

    return rst_list


def setup(cross_files: list[str], msvc: bool = True) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", help="Setup for native at the same time", action="store_true")
    parser.add_argument("--arm_path", help="Path of arm toolchain", type=str)
    opts = parser.parse_args()

    # Native
    if opts.native:
        if os.path.exists("builddir-native"):
            shutil.rmtree("builddir-native")
        cmd = "meson setup builddir-native".split()
        if msvc and platform.system() == "Windows":
            cmd += ["--vsenv"]
        print(green("Run:"), " ".join(cmd), flush=True)
        subprocess.run(cmd)

    # Cross
    if os.path.exists("builddir"):
        shutil.rmtree("builddir")
    cross_files = download_files(cross_files)
    write_path(Path(cross_files[0]), opts.arm_path)
    cmd = "meson setup builddir".split() + [f"--cross-file={f}" for f in cross_files]
    print(green("Run:"), " ".join(cmd), flush=True)
    subprocess.run(cmd)
