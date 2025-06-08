# Audio Transcription MCP Server

This is a Model Context Protocol (MCP) server that provides audio transcription capabilities using AssemblyAI. It converts your original script into a reusable MCP server that can transcribe audio files and return SRT or VTT subtitle formats.

## Features

- **Audio Transcription**: Transcribe local audio files to text with timestamps
- **Multiple Output Formats**: Generate both SRT and VTT subtitle formats
- **Language Support**: Configurable language codes (optimized for Korean, supports many others)
- **Advanced Configuration**: Includes speaker labels, punctuation, and entity detection
- **Error Handling**: Comprehensive error handling with meaningful messages
- **MCP Integration**: Built with FastMCP for easy integration with AI assistants

## Installation

1. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

2. **Set up AssemblyAI API Key**:
   - The current script includes an API key, but you should replace it with your own
   - Get your API key from [AssemblyAI](https://www.assemblyai.com/)
   - Update the key in `transcribe_mcp_server.py`

## Usage

### Running the Server

**Option 1: Direct execution**

```bash
python transcribe_mcp_server.py
```

**Option 2: Using FastMCP CLI**

```bash
fastmcp run transcribe_mcp_server.py
```

**Option 3: For development with inspector**

```bash
fastmcp dev transcribe_mcp_server.py
```

### Available Tools

The server provides three main tools:

1. **`transcribe_audio_to_srt`**

   - **Purpose**: Transcribe audio file and return SRT subtitle content
   - **Parameters**:
     - `audio_file_path` (string): Path to your local audio file
     - `language_code` (string, optional): Language code (default: "ko" for Korean)
   - **Returns**: SRT formatted subtitle text

2. **`transcribe_audio_to_vtt`**

   - **Purpose**: Transcribe audio file and return VTT subtitle content
   - **Parameters**:
     - `audio_file_path` (string): Path to your local audio file
     - `language_code` (string, optional): Language code (default: "ko" for Korean)
   - **Returns**: VTT formatted subtitle text

3. **`get_supported_languages`**
   - **Purpose**: Get list of supported language codes
   - **Parameters**: None
   - **Returns**: List of language codes (en, ko, ja, zh, etc.)

### Testing the Server

Run the test script to verify everything works:

```bash
python test_transcription_server.py
```

Make sure you have an audio file at `output/output.wav` or update the path in the test script.

### Using with AI Assistants

#### Claude Desktop Integration

1. **Install via FastMCP CLI** (recommended):

```bash
fastmcp install transcribe_mcp_server.py --name "Audio Transcription"
```

2. **Manual Configuration**:
   Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "audio-transcription": {
      "command": "python",
      "args": ["path/to/transcribe_mcp_server.py"]
    }
  }
}
```

#### Programmatic Usage

```python
import asyncio
from fastmcp import Client

async def transcribe_my_audio():
    client = Client("transcribe_mcp_server.py")

    async with client:
        result = await client.call_tool("transcribe_audio_to_srt", {
            "audio_file_path": "my_audio.wav",
            "language_code": "en"
        })

        srt_content = result[0].text
        print(srt_content)

asyncio.run(transcribe_my_audio())
```

## Configuration

### Language Codes

- `en` - English
- `ko` - Korean (default)
- `ja` - Japanese
- `zh` - Chinese
- `es` - Spanish
- `fr` - French
- `de` - German
- And more...

### Audio Formats

AssemblyAI supports most common audio formats:

- WAV
- MP3
- MP4
- M4A
- FLAC
- And more...

## Technical Details

### Transcription Configuration

The server uses optimized settings for high-quality transcription:

- **Speech Model**: Best quality model
- **Speaker Labels**: Distinguishes different speakers
- **Punctuation**: Adds proper punctuation
- **Text Formatting**: Improves readability
- **Entity Detection**: Identifies names, places, etc.

### Error Handling

The server includes comprehensive error handling for:

- File not found errors
- Transcription failures
- Network issues
- Invalid parameters

## Differences from Original Script

This MCP server version offers several advantages over the original script:

1. **Reusable**: Can be called multiple times with different files
2. **Parameterized**: Language and file path are configurable
3. **Integrated**: Works with AI assistants and other MCP clients
4. **Error Handling**: Better error messages and recovery
5. **Multiple Formats**: Both SRT and VTT output options
6. **No File Output**: Returns content directly (no need to manage output files)

## Troubleshooting

### Common Issues

1. **Import Error for fastmcp**: Install with `pip install fastmcp`
2. **AssemblyAI API Error**: Check your API key and internet connection
3. **File Not Found**: Verify the audio file path is correct and accessible
4. **Transcription Failed**: Check audio file format and quality

### Getting Help

- Check the FastMCP documentation: https://github.com/jlowin/fastmcp
- AssemblyAI documentation: https://www.assemblyai.com/docs
- File an issue if you encounter problems

## License

This project uses the same license as your original transcription script.
