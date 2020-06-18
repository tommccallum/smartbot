"""
Makes all speech sounds

- Reads in from a file in .config/smartbot/speech.json
- reads in "say" and replaces %T with name of track, %N with name
- writes out to .config/smartbot/speech/[voice]
- saves in speech.json

Designed to be run either on a cron or after get_iplayer crontab
"""
import personality
import config_io
import voice_library as voice

def make_speech():
    g_config = config_io.Configuration.get()
    g_personality = personality.Personality(g_config)
    v = g_personality.voice_library
    v.update()

if __name__ == "__main__":
    make_speech()