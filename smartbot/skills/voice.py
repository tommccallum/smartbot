import hashlib
import os
import subprocess

def sayText(personality, text):
    file_path=None
    if personality.voice_library.has_saying(text):
        print("[Personality] using existing saying")
        file_path = personality.voice_library.get_saying(text)
    if not file_path or not os.path.exists(file_path):
        file_path = personality.voice_library.get_saying_path(text)
        print("[Personality] creating new saying '"+text+"' in '"+file_path+"'")
        cmd = "echo \""+text+"\" | text2wave -eval \"(voice_cmu_us_slt_arctic_clunits)\" -o \""+file_path+"\""
        subprocess.run(cmd, shell=True)
        personality.voice_library.save_saying(text, file_path)
    playSaying(file_path)


def playSaying(file_path):
    subprocess.run("aplay -t wav \""+file_path+"\"", shell=True)