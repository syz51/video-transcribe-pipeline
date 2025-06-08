import os
import assemblyai as aai
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    name="Audio Transcription Server",
    instructions="""
    This server provides audio transcription capabilities using AssemblyAI.
    Call transcribe_audio_to_srt() with a local audio file path to get SRT subtitles.
    The server is optimized for Korean content but can handle other languages too.
    """,
)

# Configure AssemblyAI settings
aai.settings.api_key = "API_KEY"
aai.settings.base_url = "https://api.eu.assemblyai.com"


@mcp.tool()
def transcribe_audio_to_srt(audio_file_path: str, language_code: str = "ko") -> str:
    """
    Transcribe a local audio file and return SRT subtitle content.

    Args:
        audio_file_path (str): Path to the local audio file to transcribe
        language_code (str): Language code for transcription (default: "ko" for Korean)

    Returns:
        str: SRT subtitle content
    """
    try:
        # Validate that the audio file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Optimized configuration for audio with background music
        config = aai.TranscriptionConfig(
            # Use the best speech model for highest accuracy
            speech_model=aai.SpeechModel.best,
            # Set language
            language_code=language_code,
            # Enable speaker labels to distinguish different speakers
            speaker_labels=True,
            # Enable punctuation and formatting for better readability
            punctuate=True,
            format_text=True,
        )

        # Create transcriber and transcribe
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file_path)

        # Check for transcription errors
        if transcript.status == "error":
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        # Generate SRT content
        srt_content = transcript.export_subtitles_srt()

        if not srt_content:
            raise RuntimeError("No transcription content generated")

        return srt_content

    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Transcription Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"


@mcp.tool()
def transcribe_audio_to_vtt(audio_file_path: str, language_code: str = "ko") -> str:
    """
    Transcribe a local audio file and return VTT subtitle content.

    Args:
        audio_file_path (str): Path to the local audio file to transcribe
        language_code (str): Language code for transcription (default: "ko" for Korean)

    Returns:
        str: VTT subtitle content
    """
    try:
        # Validate that the audio file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Optimized configuration for audio with background music
        config = aai.TranscriptionConfig(
            # Use the best speech model for highest accuracy
            speech_model=aai.SpeechModel.best,
            # Set language
            language_code=language_code,
            # Enable speaker labels to distinguish different speakers
            speaker_labels=True,
            # Enable punctuation and formatting for better readability
            punctuate=True,
            format_text=True,
        )

        # Create transcriber and transcribe
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file_path)

        # Check for transcription errors
        if transcript.status == "error":
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        # Generate VTT content
        vtt_content = transcript.export_subtitles_vtt()

        if not vtt_content:
            raise RuntimeError("No transcription content generated")

        return vtt_content

    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Transcription Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"


@mcp.tool()
def get_supported_languages() -> list[str]:
    """
    Get a list of commonly supported language codes for transcription.

    Returns:
        list[str]: List of supported language codes
    """
    return [
        "en",  # English
        "ko",  # Korean
        "ja",  # Japanese
        "zh",  # Chinese
    ]


if __name__ == "__main__":
    mcp.run()
