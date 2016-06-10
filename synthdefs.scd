


(

SynthDef(\atom, { |out=0,amp=0.1,sustain=0.1,freq=440,az=0,ele=0,dist=0|
	var snd, env;
	snd = SinOsc.ar(freq, phase:0.5pi);
	env = EnvGen.kr(Env.asr(0.01,1,sustain), Impulse.kr(Rand(0.3,0.4)));
	Out.ar(out, FoaProximity.ar(FoaPanB.ar(snd * env * amp, az, ele),
		dist));
}).add;

);