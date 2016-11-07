/*
    Copyright 2016 Holger Ballweg

    This file is part of chison.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

(
"Loading SynthDefs".postln;
q.makeSpatialisedSynthDef = {
	arg that, name, func;
	("Making SynthDef " ++ name).postln;
	that.pyaddr.sendMsg("/obj/refresh", name);
	SynthDef(name, {
		arg out=0, revOut=5, amp=0.5, az=0, ele=0, dist=0;
		var snd = SynthDef.wrap(func) * dist.linexp(0, 500, 1, 0.01) * amp;
		Out.ar(revOut, snd);
		Out.ar(out,
			FoaProximity.ar(
				FoaPanB.ar(
					HPF.ar(snd,
						freq: 20),
					azimuth: az,
					elevation: ele),
				distance: dist.clip(0.5, 10000))
) }).add;
};

q.makeTwinPanSpatSynthDef = {
	arg that, name, funcA, funcB;
	that.makeSpatialisedSynthDef(name,
		{
			|balance=0.5|
			SelectX.ar(balance, [
				funcA,
				funcB]);
		});
};

q.makeTwinPanSpatSynthDef("rain",{
	Mix(Array.fill(4, { |i| [PinkNoise, PinkNoise, GrayNoise, PinkNoise][i].ar(LFNoise1.kr(0.011))}));
}, {
	tanh(Decay2.ar(Dust.ar(5!10), 0.02, rrand(0.1!10,0.05)) * 1.2
		* SinOsc.ar(Array.exprand(10, 100, 400));)
});

q.makeSpatialisedSynthDef("atom", {
	arg sustain=0.1, freq=440;
	var snd, env;
	snd = SinOsc.ar(freq, phase: 0.5pi);
	env = EnvGen.kr(Env.asr(0.01, 1, sustain), Impulse.kr(Rand(0.3, 0.4)));
	snd * env
});


q.makeSpatialisedSynthDef("grain", {
	arg sustain = 0.1, freq = 440;
	var snd, env;
	snd = SinOsc.ar(freq * [1,1.01]);
	env = EnvGen.ar(Env.perc(0.01,sustain), doneAction:2);
	snd * env;
});


q.makeSpatialisedSynthDef("bfactor2", {
	arg sustain=0.1,freq=440, gate=1;
	var snd, env;
	snd = SinOsc.ar(freq, phase: 0.5pi);
	env = EnvGen.kr(Env.asr(0.01, 1, sustain, 0.1), gate);
	snd * env
});


q.makeSpatialisedSynthDef("bfactor", {
	arg sustain=1.0,freq=440, midinote=40,rhfreq=1,t_trig=1, gate=0;
	var snd, env;
	var outforce;
	snd = SinOsc.ar(Vibrato.kr(midinote.midicps, Rand(1.0,4.0), Rand(0.005,0.0005)) + (0.01 * (midinote > 80)) , phase: 0.5pi, mul:2.8).tanh;
	env = EnvGen.kr(Env.perc(0.1, sustain), Impulse.kr(rhfreq) + t_trig);
	snd = LPF.ar(snd * env * (gate + 1),
		EnvGen.ar(Env.perc(0.001, 4, curve:-2), t_trig,
			levelScale: t_trig
		).linlin(0,1,600, 18000));
});

q.makeSpatialisedSynthDef("bfactor2Grain", {
	arg sustain=1.0,midinote=44, gate=1;
	var snd, env;
	snd = SinOsc.ar(midinote.midicps, phase: 0.5pi, mul:2.8).tanh;
	env = EnvGen.kr(Env.perc(0.001, sustain), gate, doneAction:2);
	snd * env
});


q.makeSpatialisedSynthDef("sample", {
	arg freq=440, sample=0;
	PlayBuf.ar(1, sample, freq/440.0, loop:1);
});


q.makeTwinPanSpatSynthDef("tpsample", {
	arg fakeA, sampleA=0, freqA=440;
	PlayBuf.ar(1, sampleA, freqA/440.0, loop:1);
}, {
	arg fakeB, sampleB=0, freqB=1;
	PlayBuf.ar(1, sampleB, freqB/440.0, loop:1);
});



q.makeSpatialisedSynthDef("hbondGrain", {
	arg sustain=0.2,ampScale=1,freq=340, mfreq=1, t_trig=1, pmindex=4, gate=0;
	var snd, env;
	snd = PMOsc.ar(Vibrato.ar(freq, Rand(1.0,4.0), Rand(0.2,0.005)), mfreq, pmindex);
	snd = HPF.ar(snd, 50);
	LPF.ar(snd * (gate + 1),
		EnvGen.ar(Env.perc(0.08, 2, curve:-2), t_trig, levelScale: t_trig, doneAction:2).linexp(0,1,200, 18000))
});


q.makeSpatialisedSynthDef("hbond1", {
	arg sustain=0.2,ampScale=1,midinote=60, mfreq=1, t_trig=1, pmindex=10, gate=0;
	var snd, env;
	var freq = midinote.midicps;
	snd = SinOsc.ar(Vibrato.ar(freq, Rand(0.1,4.0), Rand(0.01,0.005))) * (SinOsc.ar(mfreq));
	//snd = HPF.ar(snd, 80);
	//snd = MidEQ.ar(snd, freq, 1, -12);
	LPF.ar(snd * 0.25 * ((gate * 4) + 1).lag(0.01),
		EnvGen.ar(Env.perc(0.08, 2, curve:-4), t_trig, levelScale: t_trig).linexp(0,1,400, 18000))
});


q.makeSpatialisedSynthDef("hbond", {
	//Decay.ar(Impulse.ar(1),0.1,mul:3 * SinOsc.ar(30)).tanh
	arg rhfreq = 1, t_trig=1;
	var freq = rhfreq;
	var len = 0.5;
	var closeLen = 0.6;
	var takt = DelayN.kr(Impulse.kr(0) + t_trig, closeLen, closeLen);
	var env = EnvGen.ar(Env.new([0,1,1,0],[0.001,len,0.0001]),takt);
	var snd = (SinOsc.ar(EnvGen.ar(Env.new([0,1],[0.01]), takt).exprange(12300,30), phase:0.5pi) * 10).distort * env;
	var distance = (SinOsc.ar(320) * EnvGen.ar(Env.linen(0.005,0.02,0.015),Impulse.kr(freq)).dup ) * 0.2;
	snd = snd + RHPF.ar(snd, [2000,2001], 0.5);
	snd = Mix(RLPF.ar(BPF.ar(GrayNoise.ar * 0.2, 1660) + distance,
		EnvGen.ar(Env.new([15000,15000, 1000, 300],
			[closeLen/2, closeLen/2, len]), t_trig)) + snd);
	//HPF.ar(snd, 150)
	snd
});


q.makeSpatialisedSynthDef("sine", {
	arg sustain=1.0,midinote=44, gate=1;
	var snd, env;
	env = EnvGen.kr(Env.perc(0.001, sustain), gate, doneAction:2);
	snd = SinOsc.ar(midinote.midicps, phase: 0.5pi, mul:(2.8 * env)).tanh;
	snd * gate
});


q.makeSpatialisedSynthDef("piano", {
	arg sustain=1.0,midinote=44, gate=1;
	var snd, env;
	snd = MdaPiano.ar(midinote.midicps, gate);
	env = EnvGen.kr(Env.asr(0.001, 1,0.1), gate, doneAction:2);
	snd * env * gate
});

);
