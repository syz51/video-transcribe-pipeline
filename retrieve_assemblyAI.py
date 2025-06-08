import assemblyai as aai

aai.settings.api_key = "9393ac3a53354593bcaf4bd65323c45b"
# aai.settings.base_url = "https://api.eu.assemblyai.com"

transcript = aai.Transcript.get_by_id("71038186-086b-41c5-a8f3-4534aec6dbab")
