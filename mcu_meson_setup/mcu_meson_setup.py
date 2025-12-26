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


def find_path2(cmd: str) -> Path | None:
    if platform.system() == "Windows":
        PATH = os.environ["PATH"].split(";")
        cmd += ".exe"
    else:
        PATH = os.environ["PATH"].split(":")

    for P in PATH:
        p = Path(P)
        cmd_p = p.joinpath(cmd)
        if cmd_p.exists():
            print(green("Found:"), cmd_p, flush=True)
            return p

    return None


def write_path(file: Path, arm_path: str | None) -> None:
    if str(file).endswith("gcc-arm-none-eabi.ini"):
        arm_cmd = "arm-none-eabi-gcc"
    else:
        arm_cmd = "armclang"

    if arm_path:
        path = Path(arm_path)
        if path.name != "bin":
            path = path.joinpath("bin")
    else:
        tmp = find_path2(arm_cmd)
        if tmp is None:
            print(red("Can not find:"), arm_cmd, flush=True)
            exit(1)
        path = tmp

    rst = subprocess.run(
        [path.joinpath(arm_cmd), "--version"], text=True, capture_output=True, check=True
    )
    print(rst.stdout, flush=True)

    text = file.read_text()
    if arm_cmd == "arm-none-eabi-gcc":
        ver = re.search(r"\) ([\d\.]+) ", rst.stdout)
        if ver and int(ver.group(1).split(".")[0]) >= 12:
            text = text.replace(
                "base_c_link_args2 = []",
                "base_c_link_args2 = ['-Wl,-no-warn-rwx-segments']",
                count=1,
            )

    path_str = path.parent.as_posix()
    text = re.sub(r"cross_toolchain = '[^']+'", f"cross_toolchain = '{path_str}'", text, count=1)
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
