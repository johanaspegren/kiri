from kiri.modules.routines import KiriRoutines
from kiri.modules.swivel import SwivelController
from kiri.modules.piper_tts import TTS
from kiri.modules.motions import KiriMotions

def main():
    sw = SwivelController().open()
    tts = TTS()
    motions = KiriMotions(sw)
    routines = KiriRoutines(motions, tts)
    routines.wake_up()

if __name__ == "__main__":
    main()