
(
q = q ? ();
q.kernels = q.kernels ? ();
q.kernelsLoaded = false;
q.volume = q.volume ? 0.5;


Server.default = Server.local;
s = Server.default;

/*
	Toggle osc debugging on and off
OSCFunc.trace()
OSCFunc.trace(false)
*/

q.makeDecoderSynthDef = {
	arg that,name,kernel;
	SynthDef(name, {
		arg out=0,amp=0.5,gate=1,ambiBus;
		var snd, env;
		env = EnvGen.kr(Env.asr(releaseTime:0.1), gate, doneAction:2);
		snd = FoaDecode.ar(In.ar(ambiBus, 4), kernel);
		Out.ar(out, snd * env * amp);
	}).add;
	name;
};

q.makeDecoderSynth = {
	arg that, decoder, bus, group;
	Synth.new(decoder,
		args: [\ambiBus, bus, \amp, q.volume],
		target: group);
};

q.buildAtkGraph = {
	fork {
		while({
			(q.kernels.size == 0)
			or: (q.kernels.select(_.kernelSize.isNil).size > 0)
			or: q.kernelsLoaded.not
		}, {
			"Waiting for kernels to load...".postln;
			0.25.wait;
		});
		"Building Atk Graph".postln;
		"synthdefs.scd".loadRelative;
		q.ambiBus = Bus.audio(s, 4);
		q.encGroup = Group.new;
		q.decGroup = Group.after(q.encGroup);
		q.decoders = ();
		q.kernels.keysValuesDo({
			arg name, kernel;
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
	q.kernelsLoaded = true;
};

q.switchDecoder = {
	arg that, newDecoder;
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
ServerBoot.add({
	arg server;
	"Server booted. Loading X...".postln;
	q.kernels = ();
	q.kernelsLoaded = false;
	q.loadKernels();
}, s);

// boot server
s.boot;

q.objects = q.objects ? ();
q.makeOSCdefs = {
	"Making OSCdefs".postln;

	OSCdef(\new).free;
	OSCdef(\new, {
		arg msg,time, addr, recvPort;
		var id, type;
		id = msg[1];
		type  = msg[2];
		if(q.objects[id].notNil, {
			("Object " ++ id ++ " already exists! Replacing it.").postln;
			q.objects[id].free;
		});
		q.objects[id] = Synth(type,
			args: [\out, q.ambiBus] ++ msg[3..],
			target: q.encGroup);
	}, "/obj/new");


	OSCdef(\modify).free;
	OSCdef(\modify, {
		arg msg,time, addr, recvPort;
		var id, attr, val;
		id = msg[1];
		if(q.objects[id].notNil, {
			msg[2..].pairsDo({
				arg attr, val;
				if(attr.asString == "sample", {
					q.objects[id].set(attr, q.objects[val]);
				}, {
					q.objects[id].set(attr, val);
				});
			});
		});
	}, "/obj/modify");


	OSCdef(\delete).free;
	OSCdef(\delete, {
		arg msg,time, addr, recvPort;
		var id;
		id = msg[1];
		if(q.objects[id].notNil, {
			q.objects[id].free;
			q.objects[id] = nil;
		});
	}, "/obj/delete");

	OSCdef(\reset).free;
	OSCdef(\reset, {
		arg msg,time, addr, recvPort;
		"Resetting objects. Deleting all sound objects.".postln;
		q.objects.do(_.free);
		q.objects = ();
	}, "/obj/reset");

	OSCdef(\decoder).free;
	OSCdef(\decoder, {
		arg msg,time, addr, recvPort;
		var decoder;
		decoder = msg[1];
		q.switchDecoder(decoder.asSymbol);
	}, "/decoder/set");


	OSCdef(\volume).free;
	OSCdef(\volume, {
		arg msg,time, addr, recvPort;
		var volume;
		volume = msg[1];
		q.volume = volume.clip(0.0,1.0);
		q.decoder.set(\amp, q.volume);
	}, "/volume/set");

	OSCdef(\sample).free;
	OSCdef(\sample, {
		arg msg,time, addr, recvPort;
		var id, path;
		id = msg[1];
		path = msg[2];
		if(q.objects[id].notNil, {
			q.objects[id].free;
		});
		("Loading sample " ++ path).postln;
		q.objects[id] = Buffer.read(s, path);
	}, "/sample/new");
};
q.makeOSCdefs();
ServerTree.add(q[\makeOSCdefs]);

);
