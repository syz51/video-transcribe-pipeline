#!/usr/bin/env python3
"""
Advanced Audio Extraction Pipeline for Video Processing
Optimized for transcription accuracy with noise reduction and format optimization
"""

import ffmpeg
import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

# Force UTF-8 encoding for subprocess operations on Windows
if platform.system() == "Windows":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AudioExtractor:
    """
    Advanced audio extraction pipeline using FFmpeg with container support.
    Optimized for transcription accuracy with noise reduction and format optimization.
    """

    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    }
    # Supported audio output formats
    SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

    def __init__(
        self,
        container_engine: bool = True,
        container_runtime: str = "auto",  # auto, podman, docker
        container_image: str = "linuxserver/ffmpeg:latest",
        timeout: int = 600,  # 10 minutes default timeout
    ) -> None:
        """
        Initialize the AudioExtractor with optimal settings for transcription.

        Args:
            container_engine: Whether to use container-based FFmpeg
            container_runtime: Container runtime to use (auto, podman, docker)
            container_image: Container image to use for FFmpeg
            timeout: Timeout in seconds for audio extraction operations

        Raises:
            RuntimeError: If FFmpeg is not available
        """
        self.container_engine = container_engine
        self.container_runtime = self._detect_container_runtime(container_runtime)
        self.container_image = container_image
        self.timeout = timeout

        # Optimal settings for transcription accuracy
        self.target_sample_rate = 16000  # 16kHz - optimal for most speech recognition
        self.target_channels = 1  # Mono - reduces file size and complexity

        # Verify FFmpeg availability
        self._verify_ffmpeg()

    def _detect_container_runtime(self, runtime: str) -> str:
        """Detect available container runtime."""
        if runtime != "auto":
            return runtime

        # Check for available container runtimes
        for rt in ["podman", "docker"]:
            if shutil.which(rt) is not None:
                logger.info(f"Detected container runtime: {rt}")
                return rt

        logger.warning("No container runtime detected")
        return "podman"  # Default fallback

    def _verify_ffmpeg(self) -> None:
        """Verify FFmpeg is available (locally or via container)."""
        if self.container_engine:
            try:
                result = subprocess.run(
                    [
                        self.container_runtime,
                        "run",
                        "--rm",
                        self.container_image,
                        "ffmpeg",
                        "-version",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30,
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"{self.container_runtime.title()} FFmpeg not available: {result.stderr}"
                    )
                logger.info(
                    f"{self.container_runtime.title()} FFmpeg verified successfully"
                )
            except subprocess.TimeoutExpired:
                raise RuntimeError(
                    f"{self.container_runtime.title()} FFmpeg verification timed out"
                )
            except FileNotFoundError:
                raise RuntimeError(
                    f"{self.container_runtime.title()} not found. Please install {self.container_runtime} or set container_engine=False"
                )
        else:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10,
                )
                if result.returncode != 0:
                    raise RuntimeError("FFmpeg command failed")
                logger.info("Local FFmpeg verified successfully")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                raise RuntimeError(
                    "FFmpeg not found in PATH. Please install FFmpeg or use container mode."
                )

    def _validate_paths(self, input_path: str, output_path: str) -> tuple[Path, Path]:
        """
        Validate input and output paths.

        Args:
            input_path: Path to input video file
            output_path: Path to output audio file

        Returns:
            Tuple of validated input and output Path objects

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If paths are invalid or formats unsupported
        """
        input_file = Path(input_path).resolve()
        output_file = Path(output_path).resolve()

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not input_file.is_file():
            raise ValueError(f"Input path is not a file: {input_path}")

        # Check file size (warn for very large files)
        file_size_mb = input_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 1000:  # Warn for files > 1GB
            logger.warning(
                f"Large input file detected ({file_size_mb:.1f}MB). Processing may take a while."
            )

        # Validate input file format
        if input_file.suffix.lower() not in self.SUPPORTED_VIDEO_FORMATS:
            logger.warning(
                f"Input format {input_file.suffix} may not be supported. "
                f"Supported formats: {', '.join(self.SUPPORTED_VIDEO_FORMATS)}"
            )

        # Validate output file format
        if output_file.suffix.lower() not in self.SUPPORTED_AUDIO_FORMATS:
            raise ValueError(
                f"Output format {output_file.suffix} not supported. "
                f"Supported formats: {', '.join(self.SUPPORTED_AUDIO_FORMATS)}"
            )

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        return input_file, output_file

    def _get_container_paths(
        self, input_file: Path, output_file: Path
    ) -> tuple[str, str, str, str]:
        """
        Get container-compatible paths for volume mounting.

        Args:
            input_file: Input file path
            output_file: Output file path

        Returns:
            Tuple of (input_mount, output_mount, input_container_path, output_container_path)
        """
        if platform.system() == "Windows":
            # Improved Windows path handling
            def convert_windows_path(path: Path) -> str:
                """Convert Windows path to container-compatible format."""
                path_str = str(path.parent.absolute())

                # Handle Windows drive letters properly
                if len(path_str) >= 2 and path_str[1] == ":":
                    drive = path_str[0].lower()
                    remainder = path_str[2:].replace("\\", "/")
                    return f"/{drive}{remainder}"

                # Handle UNC paths
                if path_str.startswith("\\\\"):
                    return path_str.replace("\\", "/")

                return path_str.replace("\\", "/")

            input_dir = convert_windows_path(input_file)
            output_dir = convert_windows_path(output_file)
        else:
            input_dir = str(input_file.parent.absolute())
            output_dir = str(output_file.parent.absolute())

        return (
            input_dir,
            output_dir,
            f"/input/{input_file.name}",
            f"/output/{output_file.name}",
        )

    def extract_basic_audio(self, input_path: str, output_path: str) -> bool:
        """
        Extract audio with basic settings matching:
        ffmpeg -i input.mp4 -acodec pcm_s16le -ac 1 -ar 16000 output.wav

        Args:
            input_path: Path to input video file
            output_path: Path to output audio file

        Returns:
            True if extraction successful, False otherwise
        """
        try:
            logger.info(f"Starting basic audio extraction from {input_path}")

            # Validate paths
            input_file, output_file = self._validate_paths(input_path, output_path)

            if not self.container_engine:
                # Local FFmpeg version
                try:
                    stream = ffmpeg.input(str(input_file))
                    output = ffmpeg.output(
                        stream,
                        str(output_file),
                        acodec="pcm_s16le",  # 16-bit PCM
                        ac=self.target_channels,  # Mono (1 channel)
                        ar=self.target_sample_rate,  # 16kHz sample rate
                        loglevel="info",  # Show progress
                    )
                    ffmpeg.run(output, overwrite_output=True, quiet=False)
                except ffmpeg.Error as e:
                    stderr_msg = ""
                    if e.stderr:
                        try:
                            stderr_msg = e.stderr.decode("utf-8", errors="replace")
                        except (UnicodeDecodeError, AttributeError):
                            stderr_msg = str(e.stderr)
                    logger.error(f"FFmpeg error: {stderr_msg or str(e)}")
                    return False

            else:
                # Container FFmpeg version with improved path handling
                input_mount, output_mount, input_container, output_container = (
                    self._get_container_paths(input_file, output_file)
                )

                cmd = [
                    self.container_runtime,
                    "run",
                    "--rm",
                    "-v",
                    f"{input_mount}:/input:ro",  # Read-only input mount
                    "-v",
                    f"{output_mount}:/output",
                    self.container_image,
                    "-i",
                    input_container,
                    "-acodec",
                    "pcm_s16le",
                    "-ac",
                    str(self.target_channels),
                    "-ar",
                    str(self.target_sample_rate),
                    "-loglevel",
                    "info",  # Show progress
                    "-y",  # Overwrite output file
                    output_container,
                ]

                logger.debug(f"Running command: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout,
                )
                if result.returncode != 0:
                    logger.error(
                        f"{self.container_runtime.title()} FFmpeg failed: {result.stderr}"
                    )
                    return False

            # Verify output file was created and has content
            if not output_file.exists():
                logger.error("Output file was not created")
                return False

            if output_file.stat().st_size == 0:
                logger.error("Output file is empty")
                return False

            logger.info(f"Basic audio extraction completed: {output_path}")
            return True

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return False
        except ValueError as e:
            logger.error(f"Invalid input: {e}")
            return False
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            return False
        except subprocess.TimeoutExpired:
            logger.error(f"Audio extraction timed out after {self.timeout} seconds")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            return False
        except Exception as e:
            logger.error(f"Basic audio extraction failed: {e}")
            return False


def main() -> None:
    """Example usage of the AudioExtractor."""

    # Initialize with container engine (change to container_engine=False for local FFmpeg)
    try:
        extractor = AudioExtractor(container_engine=True)
    except RuntimeError as e:
        logger.error(f"Failed to initialize AudioExtractor: {e}")
        return

    # Example: Extract audio from a video file
    input_video = "input/input.mp4"  # Replace with your video file
    output_audio = "output/output.wav"

    try:
        # Basic extraction (equivalent to: ffmpeg -i input.mp4 -acodec pcm_s16le -ac 1 -ar 16000 output.wav)
        logger.info("=== Basic Audio Extraction ===")
        success = extractor.extract_basic_audio(input_video, output_audio)
        if success:
            logger.info(f"✓ Basic audio extraction successful: {output_audio}")
        else:
            logger.error("✗ Basic audio extraction failed")

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
