# Audio Transcriber with SRT Caption Generation

This project provides a complete solution for transcribing audio files using [Deepgram's API](https://deepgram.com) and converting the transcription results into SRT (SubRip Subtitle) caption files using the [deepgram-python-captions](https://github.com/deepgram/deepgram-python-captions) library.

## Features

- **Audio Transcription**: Transcribe local audio files or audio from URLs
- **SRT Caption Generation**: Automatically convert transcriptions to properly formatted SRT files
- **Multiple Audio Formats**: Support for various audio formats (WAV, MP3, MP4, etc.)
- **Flexible Configuration**: Customize transcription models, languages, and options
- **Speaker Diarization**: Optional speaker identification in transcriptions
- **Command-Line Interface**: Easy-to-use CLI for batch processing
- **Programmatic API**: Use as a Python library in your own projects

## Installation

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install deepgram-sdk>=3.0.0
pip install deepgram-captions>=1.0.0
pip install python-dotenv>=1.0.0  # Optional, for .env file support
```

### 2. Get a Deepgram API Key

1. Sign up for a free account at [Deepgram Console](https://console.deepgram.com/)
2. Create a new API key in your dashboard
3. Set the API key as an environment variable:

**Linux/macOS:**

```bash
export DEEPGRAM_API_KEY="your-api-key-here"
```

**Windows:**

```cmd
set DEEPGRAM_API_KEY=your-api-key-here
```

Or create a `.env` file in your project directory:

```
DEEPGRAM_API_KEY=your-api-key-here
```

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Transcribe a local audio file
python audio_transcriber.py path/to/audio.wav

# Transcribe audio from a URL
python audio_transcriber.py https://example.com/audio.mp3

# Specify output file
python audio_transcriber.py audio.wav -o my_captions.srt
```

#### Advanced Options

```bash
# Use different model and language
python audio_transcriber.py audio.wav -m nova-3 -l es

# Enable speaker diarization
python audio_transcriber.py audio.wav --diarize

# Set custom line length for captions
python audio_transcriber.py audio.wav --line-length 50

# Enable verbose logging
python audio_transcriber.py audio.wav -v

# Use API key from command line
python audio_transcriber.py audio.wav -k your-api-key-here
```

#### Complete Options

```bash
python audio_transcriber.py --help
```

### Programmatic Usage

```python
import os
from audio_transcriber import AudioTranscriber

# Initialize transcriber
api_key = os.getenv("DEEPGRAM_API_KEY")
transcriber = AudioTranscriber(api_key=api_key, verbose=True)

# Transcribe and generate SRT in one step
transcription, srt_content = transcriber.transcribe_and_caption(
    audio_source="path/to/audio.wav",
    output_path="output.srt",
    model="nova-3",
    language="en-US",
    diarize=True
)

# Or do it step by step
transcription_response = transcriber.transcribe_audio(
    audio_source="path/to/audio.wav",
    model="nova-3",
    smart_format=True,
    punctuate=True
)

srt_captions = transcriber.convert_to_srt(transcription_response)
transcriber.save_srt_file(srt_captions, "output.srt")
```

## Configuration Options

### Transcription Models

- `nova-3` (default): Latest and most accurate model
- `nova-2`: Previous generation model
- `enhanced`: Enhanced model for better accuracy
- `base`: Basic model for faster processing

### Languages

Support for 30+ languages including:

- `en-US` (English - US, default)
- `en-GB` (English - UK)
- `es` (Spanish)
- `fr` (French)
- `de` (German)
- `it` (Italian)
- `pt` (Portuguese)
- `zh` (Chinese)
- `ja` (Japanese)
- `ko` (Korean)

### Additional Options

- **Smart Formatting**: Automatically format numbers, dates, and currency
- **Punctuation**: Add punctuation to transcriptions
- **Paragraphs**: Detect and format paragraph breaks
- **Utterances**: Detect utterance boundaries
- **Diarization**: Identify different speakers

## Example Output

### Sample Audio Transcription

Input: Audio file with speech

```
"Yeah. As much as it's worth celebrating, the first spacewalk with an all female team,
I think many of us are looking forward to it just being normal..."
```

### Generated SRT File

```
1
00:00:00,080 --> 00:00:03,220
Yeah. As as much as, it's worth celebrating,

2
00:00:04,400 --> 00:00:07,859
the first, spacewalk, with an all female team,

3
00:00:08,475 --> 00:00:10,715
I think many of us are looking forward

4
00:00:10,715 --> 00:00:14,235
to it just being normal and I think
```

## Supported Audio Formats

The script supports various audio formats including:

- WAV
- MP3
- MP4
- M4A
- FLAC
- OGG
- WebM
- And many more

## Error Handling

The script includes comprehensive error handling for:

- Missing API keys
- Invalid audio files
- Network connectivity issues
- API rate limits
- File permission errors

## Examples

See `example_usage.py` for more detailed programmatic examples.

### Basic Example

```bash
python audio_transcriber.py https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav
```

### Advanced Example with All Options

```bash
python audio_transcriber.py \
    my_audio.wav \
    -o my_captions.srt \
    -m nova-3 \
    -l en-US \
    --line-length 60 \
    --diarize \
    --verbose
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed

   ```bash
   pip install deepgram-sdk deepgram-captions
   ```

2. **API Key Errors**: Verify your API key is set correctly

   ```bash
   echo $DEEPGRAM_API_KEY
   ```

3. **Audio File Not Found**: Check file paths and permissions

4. **Network Errors**: Verify internet connectivity for URL-based audio

### Getting Help

- Check the [Deepgram Documentation](https://developers.deepgram.com/)
- Review the [Deepgram Python SDK](https://github.com/deepgram/deepgram-python-sdk)
- See the [Deepgram Python Captions Library](https://github.com/deepgram/deepgram-python-captions)

## License

This project is open source. Please check individual library licenses:

- [Deepgram Python SDK](https://github.com/deepgram/deepgram-python-sdk/blob/main/LICENSE)
- [Deepgram Python Captions](https://github.com/deepgram/deepgram-python-captions/blob/main/LICENSE)

## Contributing

Feel free to submit issues and enhancement requests!
