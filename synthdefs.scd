
(
"Loading SynthDefs".postln;
q.makeSpatialisedSynthDef = {
	arg that, name, func;
	("Making SynthDef " ++ name).postln;
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

q.makeSpatialisedSynthDef("bfactor", {
	arg sustain=0.1,freq=440, rhfreq=1;
	var snd, env;
	snd = SinOsc.ar(freq, phase: 0.5pi);
	env = EnvGen.kr(Env.asr(0.01, 1, sustain, 0.1), Impulse.kr(rhfreq));
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


q.makeSpatialisedSynthDef("hbond1", {
	arg sustain=0.2,freq=340, mfreq=1;
	var snd, env;
	snd = SinOsc.ar(freq) * SinOsc.ar(mfreq * 0.1).clip;
	snd + (snd * PinkNoise.ar(0.1))
});

q.makeSpatialisedSynthDef("hbond", {
	//Decay.ar(Impulse.ar(1),0.1,mul:3 * SinOsc.ar(30)).tanh
	arg rhfreq = 1;
	var freq = rhfreq;
	var len = 0.2;
	var closeLen = 0.5;
	var takt = DelayN.kr(Impulse.kr(0), closeLen, closeLen);
	var env = EnvGen.ar(Env.new([0,1,1,0],[0.001,len,0.0001]),takt);
	var snd = (SinOsc.ar(EnvGen.ar(Env.new([0,1],[0.01]), takt).exprange(12300,30), phase:0.5pi) * 10).distort * env;
	var distance = (SinOsc.ar(320) * EnvGen.ar(Env.linen(0.005,0.02,0.015),Impulse.kr(freq)).dup ) * 0.2;
	snd = snd + RHPF.ar(snd, [2000,2001], 0.5);
	Mix(RLPF.ar(BPF.ar(GrayNoise.ar, 660) + distance,
		EnvGen.ar(Env.new([15000,15000, 1000, 200],
			[closeLen/2, closeLen/2, len]))) + snd)
});
);
