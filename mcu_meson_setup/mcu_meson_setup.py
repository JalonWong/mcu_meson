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


def find_path(cmd: str) -> Path | None:
    if platform.system() == "Windows":
        PATH = os.environ["PATH"].split(";")
        cmd += ".exe"
    else:
        PATH = os.environ["PATH"].split(":")

    for P in PATH:
        p = Path(P)
        cmd_p = p.joinpath(cmd)
        if cmd_p.exists():
            # print(green("Found:"), cmd_p, flush=True)
            return p

    return None


def modify_cross_file(file: Path, link_script: str, output_map: str, arm_path: str | None) -> None:
    if str(file).endswith("gcc-arm-none-eabi.ini"):
        arm_cmd = "arm-none-eabi-gcc"
    else:
        arm_cmd = "armclang"

    if arm_path:
        path = Path(arm_path)
        if path.name != "bin":
            path = path.joinpath("bin")
    else:
        tmp_path = find_path(arm_cmd)
        if tmp_path is None:
            print(red("Can not find:"), arm_cmd, flush=True)
            exit(1)
        path = tmp_path

    rst = subprocess.run(
        [path.joinpath(arm_cmd), "--version"], text=True, capture_output=True, check=True
    )
    # print(rst.stdout, flush=True)

    path_str = path.parent.as_posix()
    text = re.sub(
        r"cross_toolchain = '[^']+'", f"cross_toolchain = '{path_str}'", file.read_text(), count=1
    )

    additional_c_link_args: list[str] = []
    if arm_cmd == "arm-none-eabi-gcc":
        ver = re.search(r"\) ([\d\.]+) ", rst.stdout)
        if ver and int(ver.group(1).split(".")[0]) >= 12:
            additional_c_link_args.append("-Wl,-no-warn-rwx-segments")
        if link_script:
            additional_c_link_args.append(f"-T../{link_script}")
        if output_map:
            additional_c_link_args.append(f"-Wl,-Map={output_map},--cref")
    else:
        if link_script:
            additional_c_link_args.append(f"--scatter=../{link_script}")
        if output_map:
            additional_c_link_args += "--info summarysizes --map --load_addr_map_info --xref --callgraph --symbols --info sizes --info totals --info unused --info veneers --list".split()
            additional_c_link_args.append(output_map)

    if len(additional_c_link_args) > 0:
        args_str = "','".join(additional_c_link_args)
        text = re.sub(
            r"additional_c_link_args = \[[^\[]*\]",
            f"additional_c_link_args = ['{args_str}']",
            text,
            count=1,
        )

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


def setup(
    build_dir: str,
    cross_files: list[str],
    link_script: str = "",
    output_map: str = "",
    msvc: bool = True,
) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rm", help="Remove builddir before setup", action="store_true")
    parser.add_argument("--native", help="Setup for native at the same time", action="store_true")
    parser.add_argument("--arm_path", help="Path of arm toolchain", type=str)
    opts = parser.parse_args()

    # Native
    if opts.native:
        if opts.rm and os.path.exists(f"{build_dir}-native"):
            shutil.rmtree(f"{build_dir}-native")
        cmd = f"meson setup {build_dir}-native".split()
        if msvc and platform.system() == "Windows":
            cmd += ["--vsenv"]
        print(green("Run:"), " ".join(cmd), flush=True)
        subprocess.run(cmd)

    # Cross
    if opts.rm and os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    cross_files = download_files(cross_files)
    modify_cross_file(Path(cross_files[0]), link_script, output_map, opts.arm_path)
    cmd = f"meson setup {build_dir}".split() + [f"--cross-file={f}" for f in cross_files]
    print(green("Run:"), " ".join(cmd), flush=True)
    subprocess.run(cmd)
