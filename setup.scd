

(
q = ();
q.kernels = ();
q.models = ();
"synthdefs.scd".load;

q.makeDecoderSynthDef = { |that,name,kernel|
	SynthDef(name, { |out=0,amp=0.1,gate=1,ambiBus|
		var snd, env;
		env = EnvGen.kr(Env.asr(releaseTime:0.1), gate, doneAction:2);
		snd = FoaDecode.ar(In.ar(ambiBus, 4), kernel);
		Out.ar(out, snd * env * amp);
	}).add;
	name;
};

q.buildAtkGraph = {
	q.ambiBus = Bus.audio(s, 4);
	q.encGroup = Group.new;
	q.decGroup = Group.after(q.encGroup);
	q.decoders = ();
	q.kernels.keysValuesDo({ |name, kernel|
		("Building decoder synth def for " ++ name ++ " " ++ kernel).postln;
		q.decoders[name] = q.makeDecoderSynthDef(name, kernel);
	});
	q.decoder = Synth.new(q.decoders[q.defaultKernel],
		args: [\ambiBus, q.ambiBus],
		target: q.decGroup);
};

q.loadKernels = {
	q.kernels['KEMAR binaural 1'] = FoaDecoderKernel.newCIPIC(21); 
	q.kernels['KEMAR binaural 2'] = FoaDecoderKernel.newCIPIC(165);
	q.kernels['UHJ stereo'] = FoaDecoderKernel.newUHJ();
	q.kernels['synthetic binaural'] = FoaDecoderKernel.newSpherical;
	q.defaultKernel = 'synthetic binaural';
};



Server.default = Server.local;
s = Server.default;

s.waitForBoot({
	q.loadKernels();
	s.sync;
	q.buildAtkGraph;
});


q.switchDecoder = { |that, newDecoder|
	if(q.decoders[newDecoder].notNil, {
		q.decoder.set(\gate, 0);
	}, {
		warn("Decoder " ++ newDecoder ++ " not found!");
	});
};

/*
	Toggle osc debugging on and off
OSCFunc.trace()
OSCFunc.trace(false)
*/


(
OSCdef(\atom).free;
OSCdef(\atom, {|msg,time, addr, recvPort| 
	var id, residue;
	id = msg[1];
	residue = msg[2];
	if(q.models[id].notNil, {
		q.models[id][\synths][residue].set(\dist, msg[3], \az, msg[4], \ele, msg[5], \amp, msg[3].linexp(0,500,0.8, 0.01));
		if(residue == 1, {
			("Atom: " + msg).postln;
		});
	});
}, "/atom");

OSCdef(\modelLoaded).free;
OSCdef(\modelLoaded, {|msg,time, addr, recvPort| 
	var id, residues;
	id = msg[1];
	residues = msg[2];
	("Model loaded: " + msg).postln;
	
	q.models[id] = (
		residues: residues,
		synths: residues.collect{ |i|
			Synth(\atom,
				args: [\freq, i.linexp(0,residues, 100,2000),
					\sustain, exprand(0.01, 0.5)
				],
				target: q.encGroup) });
}, "/model/loaded");

OSCdef(\modelChanged).free;
OSCdef(\modelChanged, {|msg,time, addr, recvPort| 
	var eye, obj;
	("Model changed: " + msg).postln;
}, "/model/changed");

OSCdef(\modelClosed).free;
OSCdef(\modelClosed, {|msg,time, addr, recvPort| 
	var id;
	id = msg[1];
	("Model closed: " + msg).postln;
	if(q.models[id].notNil, {
		q.models[id][\synths].do( _.free; );
		q.models[id] = nil;
	});
}, "/model/closed");
);

);

