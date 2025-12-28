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
    print(green("Modifying:"), file.as_posix(), flush=True)
    if str(file).endswith("armclang.ini"):
        arm_cmd = "armclang"
    else:
        arm_cmd = "arm-none-eabi-gcc"

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


def download_file(url: str, file: Path) -> None:
    print(green("Downloading:"), f"{url} -> {file.as_posix()}", flush=True)
    urllib.request.urlretrieve(url, file)


def prepare_cross_files(build_dir: Path, cross_files: list[str]) -> list[str]:
    cross_dir = build_dir.joinpath("cross_files")
    os.makedirs(cross_dir, exist_ok=True)

    repo = "https://raw.githubusercontent.com/JalonWong/mcu_meson"

    rst_list = []
    for f in cross_files:
        if f.startswith("main:"):
            filename = cross_dir.joinpath(f.rsplit(":", maxsplit=1)[1])
            download_file(
                f.replace("main:", f"{repo}/refs/heads/main/"),
                filename,
            )
        elif f.startswith("tag:"):
            tag_list = f.split(":")
            filename = cross_dir.joinpath(tag_list[2])
            download_file(
                f"{repo}/{tag_list[1]}/{tag_list[2]}",
                filename,
            )
        elif f.startswith("http"):
            filename = cross_dir.joinpath(f.rsplit("/", maxsplit=1)[1])
            download_file(f, filename)
        else:
            filename = cross_dir.joinpath(Path(f).name)
            print(green("Copying:"), f"{f} -> {filename.as_posix()}", flush=True)
            shutil.copy(f, filename)

        rst_list.append(filename.as_posix())

    return rst_list


def setup(
    build_dir: str,
    cross_files: list[str] = [],
    link_script: str = "",
    output_map: str = "",
    reconfigure: bool = True,
    wipe: bool = False,
    vsenv: bool = False,
    args: list[str] = [],
) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm_path", help="Path of arm toolchain", type=str)
    opts, extra = parser.parse_known_args()

    if wipe and os.path.exists(build_dir):
        print(green("Wipe:"), f"Removing {build_dir}", flush=True)
        shutil.rmtree(build_dir)

    cross_files = prepare_cross_files(Path(build_dir), cross_files)
    if len(cross_files) > 0:
        modify_cross_file(Path(cross_files[0]), link_script, output_map, opts.arm_path)

    cmd = f"meson setup {build_dir}".split() + [f"--cross-file={f}" for f in cross_files]
    if reconfigure:
        cmd += ["--reconfigure"]
    if vsenv and platform.system() == "Windows":
        cmd += ["--vsenv"]

    print(green("Running:"), " ".join(cmd + args + extra), flush=True)
    subprocess.run(cmd)
