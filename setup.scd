
(
q = q ? ();
q.kernels = q.kernels ? ();
"synthdefs.scd".loadRelative;

Server.default = Server.local;
s = Server.default;

/*
	Toggle osc debugging on and off
OSCFunc.trace()
OSCFunc.trace(false)
*/

q.makeDecoderSynthDef = { |that,name,kernel|
	SynthDef(name, { |out=0,amp=0.1,gate=1,ambiBus|
		var snd, env;
		env = EnvGen.kr(Env.asr(releaseTime:0.1), gate, doneAction:2);
		snd = FoaDecode.ar(In.ar(ambiBus, 4), kernel);
		Out.ar(out, snd * env * amp);
	}).add;
	name;
};

q.makeDecoderSynth = { |that,decoder,bus,group|
	Synth.new(decoder,
		args: [\ambiBus, bus],
		target: group);
};

q.buildAtkGraph = {
	"Building Atk Graph".postln;
	q.ambiBus = Bus.audio(s, 4);
	q.encGroup = Group.new;
	q.decGroup = Group.after(q.encGroup);
	q.decoders = ();
	q.kernels.keysValuesDo({ |name, kernel|
		("Building decoder synth def for " ++ name ++ " " ++ kernel).postln;
		q.decoders[name] = q.makeDecoderSynthDef(name, kernel);
	});
	q.decoder = q.makeDecoderSynth(
		q.decoders[q.currentKernel],
		q.ambiBus,
		q.decGroup);
	if(Quarks.isInstalled("BatLib"), {
		StageLimiter.activate;
	});
};

// rebuild Atk Graph on Cmd-. and server reboot
ServerTree.removeAll;
ServerTree.add(q[\buildAtkGraph]);

q.loadKernels = {
	q.kernels['KEMAR binaural 1'] = FoaDecoderKernel.newCIPIC(21); 
	q.kernels['KEMAR binaural 2'] = FoaDecoderKernel.newCIPIC(165);
	q.kernels['UHJ stereo'] = FoaDecoderKernel.newUHJ();
	q.kernels['synthetic binaural'] = FoaDecoderKernel.newSpherical;
	q.currentKernel = q.currentKernel ? 'synthetic binaural';
};

q.switchDecoder = { |that, newDecoder|
	if(q.decoders[newDecoder].notNil, {
		q.decoder.set(\gate, 0);
		q.currentKernel = newDecoder;
		q.decoder = q.makeDecoderSynth(
			q.decoders[q.currentKernel],
			q.ambiBus,
			q.decGroup);
		("Set decoder to " ++ newDecoder).postln;
	}, {
		warn("Decoder " ++ newDecoder ++ " not found!");
	});
};

// load kernels on server (re-)boot
ServerBoot.removeAll;
ServerBoot.add({ |server|
	"Server booted. Loading X...".postln;
	q.loadKernels();
}, s);

// boot server
s.boot;

q.objects = q.objects ? ();
q.makeOSCdefs = {
	"Making OSCdefs".postln;

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

	OSCdef(\decoder).free;
	OSCdef(\decoder, {|msg,time, addr, recvPort| 
		var decoder;
		decoder = msg[1];
		q.switchDecoder(decoder.asSymbol);
	}, "/decoder/set");
};
q.makeOSCdefs();
ServerTree.add(q[\makeOSCdefs]);

);
