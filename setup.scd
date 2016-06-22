
(
q = ();
q.kernels = ();
"synthdefs.scd".loadRelative;

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
	if(Quarks.isInstalled("BatLib"), {
		StageLimiter.activate;
	});
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
q.objects = q.objects ? ();
OSCdef(\new).free;
OSCdef(\new, {|msg,time, addr, recvPort| 
	var id, type;
	id = msg[1];
	type  = msg[2];
	if(q.objects[id].notNil, {
		("Object " ++ id ++ " already exists! Replacing it.").postln;
		q.objects[id].free;
	});
	q.objects[id] = Synth(type, [\out, q.ambiBus], target: q.encGroup);
}, "/obj/new");


OSCdef(\modify).free;
OSCdef(\modify, {|msg,time, addr, recvPort| 
	var id, attr, val;
	id = msg[1];
	attr = msg[2];
	val = msg[3];
	if(q.objects[id].notNil, {
		q.objects[id].set(attr, val);
	});
}, "/obj/modify");


OSCdef(\delete).free;
OSCdef(\delete, {|msg,time, addr, recvPort| 
	var id;
	id = msg[1];
	if(q.objects[id].notNil, {
		q.objects[id].free;
		q.objects[id] = nil;
	});
}, "/obj/delete");

);
);

q.objects.do(_.free)