#!/usr/bin/env python3
"""
Audio Transcriber with SRT Caption Generation

This script transcribes audio files using Deepgram's API and converts the
transcription to SRT caption format using the deepgram-captions library.

Requirements:
    - deepgram-sdk
    - deepgram-captions
    - python-dotenv (optional, for environment variables)

Usage:
    python audio_transcriber.py path/to/audio.wav
    python audio_transcriber.py https://example.com/audio.mp3
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

try:
    from deepgram import (
        DeepgramClient,
        DeepgramClientOptions,
        PrerecordedOptions,
        ClientOptionsFromEnv,
        UrlSource,
        FileSource,
    )
    from deepgram_captions import DeepgramConverter, srt
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install required packages:")
    print("pip install deepgram-sdk deepgram-captions")
    sys.exit(1)

# Optional: Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional


class AudioTranscriber:
    """Audio transcription and SRT caption generation class."""

    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize the AudioTranscriber.

        Args:
            api_key: Deepgram API key. If None, will use DEEPGRAM_API_KEY env var.
            verbose: Enable verbose logging.
        """
        self.verbose = verbose
        self._setup_logging()

        # Initialize Deepgram client
        if api_key:
            config = DeepgramClientOptions(
                verbose=logging.DEBUG if verbose else logging.WARNING,
            )
            self.deepgram = DeepgramClient(api_key, config)
        else:
            # Use environment variables for API key
            if verbose:
                config = DeepgramClientOptions(verbose=logging.DEBUG)
                self.deepgram = DeepgramClient("", config)
            else:
                self.deepgram = DeepgramClient("", ClientOptionsFromEnv())

        self.logger.info("AudioTranscriber initialized successfully")

    def _setup_logging(self):
        """Setup logging configuration."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def _is_url(self, path: str) -> bool:
        """Check if the provided path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def transcribe_audio(
        self,
        audio_source: str,
        model: str = "nova-3",
        language: str = "en-US",
        smart_format: bool = True,
        punctuate: bool = True,
        paragraphs: bool = True,
        utterances: bool = True,
        diarize: bool = False,
    ) -> Dict:
        """
        Transcribe audio using Deepgram API.

        Args:
            audio_source: Path to local audio file or URL to audio file.
            model: Deepgram model to use (nova-3, nova-2, enhanced, base).
            language: Language code (e.g., 'en-US', 'es', 'fr').
            smart_format: Enable smart formatting.
            punctuate: Enable punctuation.
            paragraphs: Enable paragraph detection.
            utterances: Enable utterance detection.
            diarize: Enable speaker diarization.

        Returns:
            Dictionary containing the transcription response.
        """
        self.logger.info(f"Starting transcription of: {audio_source}")

        # Configure transcription options
        options = PrerecordedOptions(
            model=model,
            language=language,
            smart_format=smart_format,
            punctuate=punctuate,
            paragraphs=paragraphs,
            utterances=utterances,
            diarize=diarize,
        )

        try:
            if self._is_url(audio_source):
                # Transcribe from URL
                self.logger.info("Transcribing from URL")
                audio_url = UrlSource(url=audio_source)
                response = self.deepgram.listen.rest.v("1").transcribe_url(  # type: ignore
                    audio_url, options
                )
            else:
                # Transcribe from local file
                self.logger.info("Transcribing from local file")
                audio_path = Path(audio_source)

                if not audio_path.exists():
                    raise FileNotFoundError(f"Audio file not found: {audio_source}")

                with open(audio_path, "rb") as audio_file:
                    buffer_data = audio_file.read()

                payload: FileSource = {
                    "buffer": buffer_data,
                }
                response = self.deepgram.listen.rest.v("1").transcribe_file(  # type: ignore
                    payload, options
                )

            self.logger.info("Transcription completed successfully")
            return response  # type: ignore

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise

    def convert_to_srt(
        self, transcription_response: dict, line_length: Optional[int] = None
    ) -> str:
        """
        Convert Deepgram transcription response to SRT format.

        Args:
            transcription_response: Response from Deepgram transcription.
            line_length: Optional line length for captions.

        Returns:
            SRT formatted string.
        """
        self.logger.info("Converting transcription to SRT format")

        try:
            # Create DeepgramConverter instance
            converter = DeepgramConverter(transcription_response)

            # Generate SRT captions
            if line_length:
                srt_captions = srt(converter, line_length)
            else:
                srt_captions = srt(converter)

            self.logger.info("SRT conversion completed successfully")
            return srt_captions

        except Exception as e:
            self.logger.error(f"SRT conversion failed: {e}")
            raise

    def save_srt_file(self, srt_content: str, output_path: str) -> None:
        """
        Save SRT content to a file.

        Args:
            srt_content: SRT formatted string.
            output_path: Path where to save the SRT file.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(srt_content)
            self.logger.info(f"SRT file saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save SRT file: {e}")
            raise

    def transcribe_and_caption(
        self,
        audio_source: str,
        output_path: Optional[str] = None,
        **transcription_options,
    ) -> tuple[dict, str]:
        """
        Complete workflow: transcribe audio and generate SRT captions.

        Args:
            audio_source: Path to local audio file or URL.
            output_path: Optional path for SRT file. If None, generates automatically.
            **transcription_options: Additional options for transcription.

        Returns:
            Tuple of (transcription_response, srt_content).
        """
        # Transcribe audio
        transcription = self.transcribe_audio(audio_source, **transcription_options)

        # Convert to SRT
        srt_content = self.convert_to_srt(transcription)

        # Save SRT file if output path is provided or generate one
        if output_path is None:
            if self._is_url(audio_source):
                output_path = "transcription.srt"
            else:
                audio_path = Path(audio_source)
                output_path = str(audio_path.with_suffix(".srt"))

        self.save_srt_file(srt_content, output_path)

        return transcription, srt_content


def main():
    api_key = "DEEPGRAM_API_KEY"
    audio_source = "output/output.wav"
    output_path = "transcription_deepgram.srt"
    try:
        # Initialize transcriber
        transcriber = AudioTranscriber(api_key=api_key, verbose=True)

        # Prepare transcription options
        transcription_options = {
            "model": "nova-2",
            "language": "ko",
        }

        # Transcribe and generate captions
        print(f"Transcribing: {audio_source}")
        transcriber.transcribe_and_caption(
            audio_source, output_path=output_path, **transcription_options
        )

        # Display results
        print("\n" + "=" * 60)
        print("TRANSCRIPTION COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
