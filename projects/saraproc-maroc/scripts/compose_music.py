#!/usr/bin/env python3
"""Compose and master an original, deterministic 120 BPM instrumental score.

No pre-recorded samples, soundfonts, external music, or online services are used.
Usage: python3 scripts/compose_music.py [--pause-file scripts/pauses.json]
Pause-file JSON: a list of entry times, or {"entry_times": [...], "silence": 0.75}.
"""
from pathlib import Path
import argparse
import json
import math
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DURATION = 225.0
BEAT = 0.5
ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(240223)


def frequency(note):
    return 440.0 * 2.0 ** ((note - 69) / 12)


def t_for(duration):
    return np.arange(round(duration * SR), dtype=np.float32) / SR


def soft_edges(x, attack=0.005, release=0.04):
    na = min(len(x), round(attack * SR))
    nr = min(len(x), round(release * SR))
    if na:
        x[:na] *= np.linspace(0, 1, na, dtype=np.float32)
    if nr:
        x[-nr:] *= np.linspace(1, 0, nr, dtype=np.float32)
    return x


def keys(note, duration=1.6):
    t = t_for(duration)
    f = frequency(note)
    # A softly struck electric-piano voice: the transient grows less metallic.
    phase = 2 * np.pi * f * t
    modulation = 1.25 * np.exp(-t * 5) * np.sin(2 * phase)
    core = np.sin(phase + modulation) * np.exp(-t * 2.6)
    tine = 0.17 * np.sin(3 * phase) * np.exp(-t * 7)
    return soft_edges((core + tine).astype(np.float32), 0.004, 0.13)


def bell(note, duration=1.3):
    t = t_for(duration)
    phase = 2 * np.pi * frequency(note) * t
    x = (np.sin(phase) + .18 * np.sin(2 * phase) + .07 * np.sin(4 * phase))
    return soft_edges((x * np.exp(-3.8 * t)).astype(np.float32), .003, .12)


def bass(note, duration=.37):
    t = t_for(duration)
    phase = 2 * np.pi * frequency(note) * t
    x = np.sin(phase) + .17*np.sin(2*phase) + .07*np.sin(3*phase)
    x *= (1 - np.exp(-t * 100)) * np.exp(-t * 1.2)
    return soft_edges(x.astype(np.float32), .006, .09)


def pad(note, duration):
    t = t_for(duration)
    f = frequency(note)
    x = np.zeros((len(t), 2), np.float32)
    for side, detune in enumerate([-.0013, .0013]):
        phase = 2 * np.pi * f * (1 + detune) * t
        for harmonic, weight in [(1, 1), (2, .21), (3, .10), (5, .035)]:
            x[:, side] += weight * np.sin(phase * harmonic)
    envelope = (1 - np.exp(-t * 5)) * np.minimum(1, (duration - t) / .5)
    # A gentle rhythmic breath, rather than aggressive EDM pumping.
    envelope *= 1 - .15*np.exp(-(t % BEAT)/.075)
    x *= envelope[:, None]
    return x


def drum_voices():
    t = t_for(.46)
    phase = 2*np.pi*(47*t + 94*.026*(1-np.exp(-t/.026)))
    kick = np.sin(phase)*np.exp(-t*12)
    kick += .09*RNG.standard_normal(len(t))*np.exp(-t*170)
    t = t_for(.22)
    noise = RNG.standard_normal(len(t)).astype(np.float32)
    snare = sosfilt(butter(2,[1400,9500],btype='bandpass',fs=SR,output='sos'),noise)
    snare = .55*snare*np.exp(-t*23) + .25*np.sin(2*np.pi*185*t)*np.exp(-t*35)
    t = t_for(.13)
    noise = RNG.standard_normal(len(t)).astype(np.float32)
    hat = sosfilt(butter(3,7500,btype='highpass',fs=SR,output='sos'),noise)
    hat *= np.exp(-t*65)
    t = t_for(.32)
    noise = RNG.standard_normal(len(t)).astype(np.float32)
    openhat = sosfilt(butter(3,7000,btype='highpass',fs=SR,output='sos'),noise)
    openhat *= np.exp(-t*20)
    return [soft_edges(v.astype(np.float32),.001,.02) for v in [kick,snare,hat,openhat]]


def compose():
    score = np.zeros((round(DURATION*SR), 2), np.float32)

    def add(signal, at, gain=1., pan=0.):
        begin = round(at*SR)
        if begin >= len(score):
            return
        count = min(len(signal),len(score)-begin)
        if signal.ndim == 1:
            # Equal-power stereo positioning.
            lr = np.array([math.cos((pan+1)*math.pi/4), math.sin((pan+1)*math.pi/4)],np.float32)
            score[begin:begin+count] += signal[:count,None] * (gain*lr)
        else:
            score[begin:begin+count] += signal[:count] * gain

    kick,snare,hat,openhat=drum_voices()
    # Dadd9, Bm7, Gmaj7, Asus4/A: original voicings and melody, no quoted song.
    progressions = [
        [(38,[62,66,69,76]),(35,[59,62,66,69]),(31,[55,62,66,71]),(33,[57,62,64,69])],
        [(31,[55,62,66,69]),(38,[57,62,66,76]),(33,[57,61,64,71]),(35,[59,62,66,73])],
        [(35,[59,62,66,69]),(31,[55,59,62,69]),(38,[57,62,66,69]),(33,[57,61,64,69])],
    ]
    motifs = [
        [(0,81),(.75,78),(1.25,76),(1.75,78)],
        [(.25,78),(.75,74),(1.25,73),(1.75,74)],
        [(0,78),(.5,74),(1,71),(1.5,74)],
        [(0,76),(.75,73),(1.25,69),(1.75,73)],
    ]
    for bar in range(110):
        at = bar*2.
        section = next((i for i,b in enumerate([20,44,60,76,92,108,126,152,166,180,194,210]) if at < b),12)
        group = (bar//16)%3
        root,chord = progressions[group][bar%4]
        introduction = at < 8
        delicate = 126 <= at < 152 or 166 <= at < 174
        build = 8 <= at < 20 or 194 <= at < 210
        intensity = .65 if introduction else .82 if delicate else 1.0
        # Voiced pad chords overlap slightly so harmony remains continuous.
        for note in chord:
            add(pad(note-12,2.35),at,.027*intensity)
        # Piano accents: root voicing, then a lighter offbeat answer.
        for i,note in enumerate(chord):
            add(keys(note,1.8),at+i*.012,.065*intensity,(-.3+.2*i))
            if not introduction:
                add(keys(note,1.2),at+1.25+i*.009,.035*intensity,(-.3+.2*i))
        # Eighth-note arpeggio with alternating stereo motion, gently varied every bar.
        arp=[0,2,1,3,2,1,3,2] if bar%2==0 else [0,1,2,3,1,2,3,1]
        for step,index in enumerate(arp):
            if introduction and step%2:continue
            add(bell(chord[index]+12,.95),at+step*.25,.032*(.75 if delicate else 1),-.35 if step%2==0 else .35)
        # A sparse, singable motif enters only in selected four-bar phrases.
        if at >= 20 and (bar//4)%4 in [0,2] and not delicate:
            for offset,note in motifs[bar%4]:
                add(keys(note,1.5),at+offset,.043,-.05)
        if not introduction:
            for step in [0,1,2,3]:
                add(bass(root,.40),at+step*.5,.17*intensity)
            if bar%4 in [2,3]:add(bass(root+12,.18),at+1.75,.06)
        # Designed percussion, exclusively musical drum voices.
        if at >= 8:
            for step in [0,1,2,3]:
                add(kick,at+step*.5,.32*(.8 if delicate else 1))
            if at >= 12:
                for step in [1,3]:add(snare,at+step*.5,.12*(.65 if delicate else 1),.08)
            for step in range(8):
                add(hat,at+step*.25,.031 if step%2==0 else .047,.32 if step%2 else -.22)
            if not delicate and bar%2:
                add(openhat,at+1.75,.035,.4)
            # Restrained two-hit pickup at the end of an eight-bar phrase.
            if bar%8==7 and not delicate:
                add(snare,at+1.75,.045,-.2)
                add(snare,at+1.875,.035,.2)

    # A fresh downbeat for the official-logo reveal; D major rings naturally to 225s.
    add(kick,220,.26)
    add(bass(38,2.5),220,.15)
    for i,note in enumerate([50,57,62,66,69,76]):
        add(keys(note,5),220+i*.018,.075 if note>=62 else .05,-.4+i*.15)
        add(pad(note,5),220,.024)
    add(bell(81,3.2),220.5,.038,.25)

    # Small stereo delay provides depth without washing out the percussion.
    dry=score.copy()
    for delay,gain in [(.375,.065),(.750,.033)]:
        n=round(delay*SR)
        score[n:,0] += dry[:-n,1]*gain
        score[n:,1] += dry[:-n,0]*gain
    score=np.tanh(score*1.22).astype(np.float32)
    score[:round(.12*SR)] *= np.linspace(0,1,round(.12*SR))[:,None]
    n=round(2.8*SR)
    score[-n:] *= np.linspace(1,0,n,dtype=np.float32)[:,None]**1.4
    return score


def apply_pauses(samples, entries, silence):
    for entry in entries:
        end=float(entry)
        start=end-silence
        if not (0 <= start < end <= DURATION):
            raise ValueError(f'Invalid silence interval: {start}..{end}')
        a,b=round(start*SR),round(end*SR)
        ramp=round(.12*SR)
        aa=max(0,a-ramp)
        samples[aa:a] *= np.linspace(1,0,a-aa,dtype=np.float32)[:,None]**.7
        samples[a:b]=0
        bb=min(len(samples),b+round(.055*SR))
        samples[b:bb] *= np.linspace(0,1,bb-b,dtype=np.float32)[:,None]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pause-file',type=Path)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'assets')
    args=parser.parse_args()
    payload=json.loads(args.pause_file.read_text()) if args.pause_file else []
    entries=payload.get('entry_times',[]) if isinstance(payload,dict) else payload
    silence=payload.get('silence',.75) if isinstance(payload,dict) else .75
    args.output_dir.mkdir(parents=True,exist_ok=True)
    score=compose()
    # A two-pass loudness master. Silence is applied afterward to preserve true gaps.
    with tempfile.TemporaryDirectory(prefix='saraproc-score-') as td:
        raw=Path(td)/'raw.wav'; mastered=Path(td)/'mastered.wav'
        wavfile.write(raw,SR,score)
        analysis=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af',
            'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],
            check=True,capture_output=True,text=True)
        measurement=json.JSONDecoder().raw_decode(analysis.stderr[analysis.stderr.rfind('{'):])[0]
        filt=('loudnorm=I=-16:TP=-1.5:LRA=9:linear=true:'
            f'measured_I={measurement["input_i"]}:measured_TP={measurement["input_tp"]}:'
            f'measured_LRA={measurement["input_lra"]}:measured_thresh={measurement["input_thresh"]}:'
            f'offset={measurement["target_offset"]}')
        subprocess.run(['ffmpeg','-v','error','-i',str(raw),'-af',filt,'-ar',str(SR),
            '-c:a','pcm_f32le',str(mastered)],check=True)
        rate,score=wavfile.read(mastered)
        assert rate==SR and score.shape==(round(DURATION*SR),2), score.shape
        apply_pauses(score,entries,float(silence))
        peak=float(np.max(np.abs(score)))
        if peak > .89:score *= .89/peak
        wav=args.output_dir/'music-original.wav'
        wavfile.write(wav,SR,(np.clip(score,-1,1)*32767).astype(np.int16))
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','aac','-b:a','256k',
        '-movflags','+faststart',str(args.output_dir/'music-original.m4a')],check=True)
    # A short review excerpt is kept separately; the composition uses the full score.
    subprocess.run(['ffmpeg','-v','error','-y','-ss','22','-i',str(wav),'-t','20',
        '-c:a','aac','-b:a','192k',str(args.output_dir/'music-preview.m4a')],check=True)
    report={'duration_seconds':len(score)/SR,'sample_rate':SR,'channels':2,
        'peak_dbfs':round(20*np.log10(float(np.max(np.abs(score)))+1e-20),3),
        'clipped_samples':int(np.sum(np.abs(score)>=1)),
        'tempo_bpm':120,'entry_times':entries,'silence_seconds':silence,
        'silence_checks':[{'end':v,'max_absolute_sample':float(np.abs(score[round((v-silence)*SR):round(v*SR)]).max())} for v in entries],
        'master_target_lufs':-16,'original_synthesis':True}
    (args.output_dir/'music-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
