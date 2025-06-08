# Audio Extraction MCP Server

A Model Context Protocol (MCP) server that provides audio extraction capabilities from video files, optimized for transcription and speech recognition workflows.

## Features

- **Extract audio from video files** using FFmpeg with optimized settings for transcription
- **Container-based processing** with support for Docker and Podman
- **Format validation** for input video files and output audio files
- **Multiple audio output formats** (WAV, MP3, FLAC, M4A, OGG)
- **Optimized settings** for speech recognition (16kHz, mono, 16-bit PCM)
- **Comprehensive error handling** and logging
- **Async processing** to avoid blocking operations

## Supported Formats

### Input Video Formats

- MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V

### Output Audio Formats

- WAV (recommended for transcription), MP3, FLAC, M4A, OGG

## Installation

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure FFmpeg is available:**

   - **Container mode (recommended):** Install Docker or Podman
   - **Local mode:** Install FFmpeg locally and ensure it's in your PATH

3. **Install the MCP server** (if using with Claude Desktop or other MCP clients):
   ```bash
   fastmcp install audio_extractor_mcp_server.py --name "Audio Extraction Server"
   ```

## Usage

### Running the Server

**Standalone:**

```bash
python audio_extractor_mcp_server.py
```

**Via FastMCP CLI:**

```bash
fastmcp run audio_extractor_mcp_server.py
```

**Development mode with auto-reload:**

```bash
fastmcp dev audio_extractor_mcp_server.py
```

### Available Tools

#### 1. `extract_audio`

Extract audio from a video file with settings optimized for transcription.

**Parameters:**

- `input_video_path` (string): Path to the input video file
- `output_audio_path` (string): Path where the extracted audio will be saved
- `use_container` (boolean, optional): Use container-based FFmpeg (default: true)
- `container_runtime` (string, optional): Container runtime ("auto", "podman", "docker")
- `timeout` (integer, optional): Timeout in seconds (default: 600)

**Example:**

```python
await client.call_tool("extract_audio", {
    "input_video_path": "/path/to/video.mp4",
    "output_audio_path": "/path/to/output.wav"
})
```

#### 2. `get_supported_formats`

Get information about supported video and audio formats.

**Returns:** Dictionary with supported formats and optimal settings.

#### 3. `validate_video_file`

Validate a video file for compatibility and get file information.

**Parameters:**

- `video_path` (string): Path to the video file to validate

**Returns:** Validation results and file metadata.

### Available Resources

#### `config://server/settings`

Get current server configuration and status information.

## Configuration

The server can be configured through tool parameters:

- **Container Engine:** Choose between Docker and Podman for FFmpeg processing
- **Timeout:** Set processing timeout for large files
- **Runtime Detection:** Automatic detection of available container runtimes

## Audio Settings

The server uses optimal settings for transcription:

- **Sample Rate:** 16kHz (optimal for speech recognition)
- **Channels:** Mono (1 channel)
- **Codec:** PCM 16-bit signed little-endian
- **Format:** WAV (recommended) or other supported formats

## Examples

### Basic Audio Extraction

```python
import asyncio
from fastmcp import Client

async def extract_audio_example():
    async with Client("audio_extractor_mcp_server.py") as client:
        result = await client.call_tool("extract_audio", {
            "input_video_path": "input/meeting.mp4",
            "output_audio_path": "output/meeting_audio.wav"
        })
        print(f"Extraction successful: {result['success']}")
        print(f"Output file: {result['output_path']}")
        print(f"File size: {result['output_size_mb']} MB")

asyncio.run(extract_audio_example())
```

### File Validation

```python
async def validate_file_example():
    async with Client("audio_extractor_mcp_server.py") as client:
        result = await client.call_tool("validate_video_file", {
            "video_path": "input/video.mp4"
        })

        if result["valid"]:
            print(f"File is valid: {result['filename']}")
            print(f"Size: {result['size_mb']} MB")
            if result["warnings"]:
                print("Warnings:", result["warnings"])
        else:
            print(f"File is invalid: {result['error']}")

asyncio.run(validate_file_example())
```

## Integration with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "audio-extraction": {
      "command": "python",
      "args": ["path/to/audio_extractor_mcp_server.py"]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found:**

   - Install FFmpeg locally or ensure Docker/Podman is available
   - Check that the container runtime is properly installed

2. **Permission errors:**

   - Ensure the output directory exists and is writable
   - Check file permissions for input video files

3. **Container runtime issues:**

   - Verify Docker or Podman is installed and running
   - Try setting `container_runtime` explicitly instead of "auto"

4. **Large file processing:**
   - Increase the `timeout` parameter for very large video files
   - Monitor disk space for output files

### Logging

The server provides detailed logging. To enable debug logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Dependencies

- `fastmcp`: MCP server framework
- `ffmpeg-python`: FFmpeg Python wrapper
- `aiofiles`: Async file operations
- FFmpeg: Audio/video processing (via container or local installation)
- Docker or Podman: Container runtime (if using container mode)

## License

This project uses the same license as the original audio extractor module.
