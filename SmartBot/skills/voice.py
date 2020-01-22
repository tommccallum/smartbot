import hashlib
import os
import subprocess

def sayText(personality, text):
    if personality.has_saying(text):
        print("[Personality] using existing saying")
        file_path = personality.get_saying(text)
    else:
        file_path = personality.get_saying_path(text)
        print("[Personality] creating new saying in personality")
        cmd = "echo \""+text+"\" | text2wave -eval \"(voice_cmu_us_slt_arctic_clunits)\" -o \""+file_path+"\""
        subprocess.run(cmd, shell=True)
        personality.save_saying(text, file_path)
    playSaying(file_path)


def playSaying(file_path):
    subprocess.run("aplay -t raw -f s16 -c 1 \""+file_path+"\"", shell=True)
