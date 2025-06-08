# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai

aai.settings.api_key = "API_KEY"
aai.settings.base_url = "https://api.eu.assemblyai.com"

audio_file = "output/output.wav"

# Optimized configuration for Korean TV show audio with background music
config = aai.TranscriptionConfig(
    # Use the best speech model for highest accuracy
    speech_model=aai.SpeechModel.best,
    # Set language to Korean
    language_code="ko",
    # Enable speaker labels to distinguish different speakers in the TV show
    speaker_labels=True,
    # Enable dual channel if your audio has stereo separation
    # dual_channel=True,  # Uncomment if needed
    # Enable punctuation and formatting for better readability
    punctuate=True,
    format_text=True,
    # Enable disfluencies to capture "um", "ah" sounds which are common in natural speech
    # disfluencies=True,
    # Enable entity detection to identify names, places, etc.
    entity_detection=True,
)

transcriber = aai.Transcriber(config=config)
transcript = transcriber.transcribe(audio_file)

if transcript.status == "error":
    raise RuntimeError(f"Transcription failed: {transcript.error}")


# Generate and save SRT subtitles
print("\n" + "=" * 50)
print("GENERATING SRT SUBTITLES...")
print("=" * 50)
srt_content = transcript.export_subtitles_srt()
with open("output/subtitles.srt", "w", encoding="utf-8") as f:
    f.write(srt_content)
print("✓ SRT subtitles saved to: output/subtitles.srt")

# Generate and save VTT subtitles (WebVTT format)
print("\n" + "=" * 50)
print("GENERATING VTT SUBTITLES...")
print("=" * 50)
vtt_content = transcript.export_subtitles_vtt()
with open("output/subtitles.vtt", "w", encoding="utf-8") as f:
    f.write(vtt_content)
print("✓ VTT subtitles saved to: output/subtitles.vtt")


print("\n" + "=" * 50)
print("PROCESSING COMPLETE!")
print("=" * 50)
print("Files generated:")
print("• output/subtitles.srt (SRT format)")
print("• output/subtitles.vtt (WebVTT format)")
