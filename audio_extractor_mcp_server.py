#!/usr/bin/env python3
"""
Audio Extraction MCP Server
A Model Context Protocol server that provides audio extraction from video files.
"""

import asyncio
import logging
from pathlib import Path

from fastmcp import FastMCP

# Import the AudioExtractor class from our existing module
from audio_extractor import AudioExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP(
    name="Audio Extraction Server",
    instructions="""
    This server provides audio extraction capabilities from video files.
    Use the extract_audio tool to convert video files to audio files optimized for transcription.
    The server supports various video formats and outputs audio in formats suitable for speech recognition.
    """,
)

# Initialize the AudioExtractor (we'll make this configurable)
audio_extractor = None


@mcp.tool()
async def extract_audio(
    input_video_path: str,
    output_audio_path: str,
    use_container: bool = True,
    container_runtime: str = "auto",
    timeout: int = 600,
) -> dict:
    """
    Extract audio from a video file using optimized settings for transcription.

    Args:
        input_video_path: Path to the input video file
        output_audio_path: Path where the extracted audio file will be saved
        use_container: Whether to use container-based FFmpeg (default: True)
        container_runtime: Container runtime to use ('auto', 'podman', 'docker')
        timeout: Timeout in seconds for the extraction process

    Returns:
        Dictionary containing extraction results and metadata
    """
    try:
        # Initialize extractor with current parameters
        global audio_extractor
        audio_extractor = AudioExtractor(
            container_engine=use_container,
            container_runtime=container_runtime,
            timeout=timeout,
        )

        logger.info(
            f"Starting audio extraction: {input_video_path} -> {output_audio_path}"
        )

        # Validate input file exists
        input_path = Path(input_video_path)
        if not input_path.exists():
            return {
                "success": False,
                "error": f"Input video file not found: {input_video_path}",
                "input_path": input_video_path,
                "output_path": output_audio_path,
            }

        # Get input file size for metadata
        input_size_mb = input_path.stat().st_size / (1024 * 1024)

        # Run the extraction in an executor to avoid blocking
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None,
            audio_extractor.extract_basic_audio,
            input_video_path,
            output_audio_path,
        )

        # Check if output file was created and get its size
        output_path = Path(output_audio_path)
        output_size_mb = 0
        if output_path.exists():
            output_size_mb = output_path.stat().st_size / (1024 * 1024)

        result = {
            "success": success,
            "input_path": input_video_path,
            "output_path": output_audio_path,
            "input_size_mb": round(input_size_mb, 2),
            "output_size_mb": round(output_size_mb, 2),
            "settings": {
                "sample_rate": 16000,
                "channels": 1,
                "codec": "pcm_s16le",
                "container_engine": use_container,
                "container_runtime": container_runtime,
            },
        }

        if not success:
            result["error"] = "Audio extraction failed. Check server logs for details."

        logger.info(
            f"Audio extraction {'completed' if success else 'failed'}: {output_audio_path}"
        )
        return result

    except Exception as e:
        error_msg = f"Audio extraction error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "input_path": input_video_path,
            "output_path": output_audio_path,
        }


@mcp.tool()
async def get_supported_formats() -> dict:
    """
    Get information about supported video input and audio output formats.

    Returns:
        Dictionary containing supported formats and optimal settings
    """
    return {
        "supported_video_formats": list(AudioExtractor.SUPPORTED_VIDEO_FORMATS),
        "supported_audio_formats": list(AudioExtractor.SUPPORTED_AUDIO_FORMATS),
        "optimal_settings": {
            "sample_rate": 16000,
            "channels": 1,
            "codec": "pcm_s16le",
            "recommended_output_format": ".wav",
        },
        "description": "Formats and settings optimized for speech recognition and transcription",
    }


@mcp.tool()
async def validate_video_file(video_path: str) -> dict:
    """
    Validate a video file for audio extraction compatibility.

    Args:
        video_path: Path to the video file to validate

    Returns:
        Dictionary containing validation results and file information
    """
    try:
        video_file = Path(video_path)

        if not video_file.exists():
            return {
                "valid": False,
                "error": f"File not found: {video_path}",
                "path": video_path,
            }

        if not video_file.is_file():
            return {
                "valid": False,
                "error": f"Path is not a file: {video_path}",
                "path": video_path,
            }

        # Check file extension
        file_extension = video_file.suffix.lower()
        is_supported_format = file_extension in AudioExtractor.SUPPORTED_VIDEO_FORMATS

        # Get file size
        file_size_bytes = video_file.stat().st_size
        file_size_mb = file_size_bytes / (1024 * 1024)
        file_size_gb = file_size_mb / 1024

        result = {
            "valid": True,
            "path": video_path,
            "filename": video_file.name,
            "extension": file_extension,
            "supported_format": is_supported_format,
            "size_bytes": file_size_bytes,
            "size_mb": round(file_size_mb, 2),
            "size_gb": round(file_size_gb, 3),
            "warnings": [],
        }

        # Add warnings for potential issues
        if not is_supported_format:
            result["warnings"].append(
                f"File format {file_extension} may not be supported. "
                f"Supported formats: {', '.join(AudioExtractor.SUPPORTED_VIDEO_FORMATS)}"
            )

        if file_size_gb > 1:
            result["warnings"].append(
                f"Large file detected ({file_size_gb:.1f}GB). Processing may take a while."
            )

        return result

    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "path": video_path,
        }


@mcp.resource("config://server/settings")
async def get_server_settings() -> dict:
    """
    Get current server configuration and status.
    """
    global audio_extractor

    settings = {
        "server_name": "Audio Extraction Server",
        "version": "1.0.0",
        "extractor_initialized": audio_extractor is not None,
        "default_settings": {
            "container_engine": True,
            "container_runtime": "auto",
            "timeout": 600,
            "target_sample_rate": 16000,
            "target_channels": 1,
        },
    }

    if audio_extractor:
        settings["current_extractor_config"] = {
            "container_engine": audio_extractor.container_engine,
            "container_runtime": audio_extractor.container_runtime,
            "timeout": audio_extractor.timeout,
            "target_sample_rate": audio_extractor.target_sample_rate,
            "target_channels": audio_extractor.target_channels,
        }

    return settings


if __name__ == "__main__":
    # Run the server
    logger.info("Starting Audio Extraction MCP Server...")
    mcp.run()
