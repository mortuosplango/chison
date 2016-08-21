
(
"Loading SynthDefs".postln;
q.makeSpatialisedSynthDef = {
	arg that, name, func;
	("Making SynthDef " ++ name).postln;
	SynthDef(name, {
		arg out=0, amp=0.5, az=0, ele=0, dist=0;
		Out.ar(out,
			FoaProximity.ar(
				FoaPanB.ar(
					HPF.ar(SynthDef.wrap(func) * dist.linexp(0, 500, 1, 0.01) * amp,
						freq: 20),
					azimuth: az,
					elevation: ele),
				distance: dist.clip(0.5, 10000))
) }).add;
};

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


q.makeSpatialisedSynthDef("bfactor2", {
	arg sustain=0.1,freq=440, gate=1;
	var snd, env;
	snd = SinOsc.ar(freq, phase: 0.5pi);
	env = EnvGen.kr(Env.asr(0.01, 1, sustain, 0.1), gate);
	snd * env
});


q.makeSpatialisedSynthDef("sample", {
	arg sustain=0.5,freq=440, rhfreq=1,sample=0;
	var snd, env;
	snd = PlayBuf.ar(1, sample, freq/440.0, loop:1);
	//env = EnvGen.kr(Env.asr(0.01,1,sustain, 0.1), Impulse.kr(rhfreq));
	snd //* env
});


q.makeSpatialisedSynthDef("hbond", {
	arg sustain=0.2,freq=340, rhfreq=1;
	var snd, env;
	snd = SinOsc.ar(freq);
	env = EnvGen.kr(Env.linen(0.005, sustain, 0.005), Impulse.kr(rhfreq));
	snd * env
});
);
