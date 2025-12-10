# downloader/ffmpeg.py

import subprocess
from pathlib import Path
from utils import get_logger

logger = get_logger("ffmpeg")


def run_ffmpeg_command(args: list):
    """
    Run an ffmpeg command and log output.
    Raises CalledProcessError if ffmpeg fails.
    """
    logger.info(f"[ffmpeg] Running: ffmpeg {' '.join(args)}")

    completed = subprocess.run(
        ["ffmpeg", "-y"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if completed.returncode != 0:
        logger.error(f"[ffmpeg] Error: {completed.stderr}")
        raise subprocess.CalledProcessError(
            completed.returncode, completed.args, completed.stdout, completed.stderr
        )

    logger.info("[ffmpeg] Done.")
    return completed.stdout, completed.stderr


def convert_to_wav(
    input_path: str,
    output_path: str,
    sample_rate: int = 22050,
    mono: bool = True,
):
    """
    Convert any audio file to a normalized WAV file.
    - sample_rate: target sample rate (e.g., 22050)
    - mono: convert stereo -> mono
    """

    in_p = Path(input_path)
    out_p = Path(output_path)

    if not in_p.exists():
        raise FileNotFoundError(f"Input audio file does not exist: {input_path}")

    args = ["-i", str(in_p)]

    if mono:
        args += ["-ac", "1"]  # 1 channel
    if sample_rate is not None:
        args += ["-ar", str(sample_rate)]  # sample rate

    args += [str(out_p)]

    run_ffmpeg_command(args)

    return str(out_p)
