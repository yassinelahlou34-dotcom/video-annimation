"""Real FFmpeg integration tests using temporary generated media, no licensed assets."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "media.py"


class MediaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.silent = cls.root / "silent.mp4"
        cls.voiced = cls.root / "voiced.mp4"
        cls.music = cls.root / "music.wav"
        cls.ffmpeg('-f', 'lavfi', '-i', 'color=c=navy:s=320x180:r=24:d=3',
                   '-c:v', 'libx264', '-threads', '2', '-pix_fmt', 'yuv420p', str(cls.silent))
        cls.ffmpeg('-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5', str(cls.music))
        cls.ffmpeg('-i', str(cls.silent), '-f', 'lavfi', '-i', 'sine=frequency=220:duration=3',
                   '-c:v', 'copy', '-c:a', 'aac', str(cls.voiced))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def ffmpeg(*args):
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-n', *args], check=True)

    def cli(self, *args, success=True):
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(r.returncode == 0, success, r.stderr)
        return r

    def inspect(self, path):
        return json.loads(self.cli('probe', path).stdout)

    def test_trim_and_preserve_original(self):
        before = hashlib.sha256(self.voiced.read_bytes()).digest()
        out = self.root / 'trim.mp4'
        self.cli('trim', self.voiced, out, '--start', '0.5', '--duration', '1')
        info = self.inspect(out)
        self.assertAlmostEqual(float(info['format']['duration']), 1, delta=0.1)
        self.assertEqual({s['codec_name'] for s in info['streams']}, {'h264', 'aac'})
        self.assertEqual(hashlib.sha256(self.voiced.read_bytes()).digest(), before)
        self.cli('trim', self.voiced, out, '--duration', '1', success=False)
        self.cli('trim', self.voiced, self.root/'invalid.mp4', '--duration', '20', success=False)
        self.assertFalse((self.root/'invalid.mp4').exists())

    def test_music_with_and_without_original_audio(self):
        for video in [self.silent, self.voiced]:
            with self.subTest(video=video.name):
                out = self.root / f'mix-{video.name}'
                self.cli('music', video, self.music, out)
                info = self.inspect(out)
                self.assertAlmostEqual(float(info['format']['duration']), 3, delta=0.1)
                audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
                self.assertEqual(audio['codec_name'], 'aac')
                self.assertGreater(float(audio['duration']), 2.9)
                self.ffmpeg('-i', str(out), '-f', 'null', '-')


if __name__ == '__main__':
    unittest.main()
