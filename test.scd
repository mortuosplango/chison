
// test ATK installation
// a piano rotating around your head
// can lead to nausea over headphones
(
Server.local.waitForBoot({
	|server|
	d = FoaDecoderKernel.newSpherical; // synthetic HRTF
	Server.local.sync;
	{ FoaDecode.ar(
		FoaProximity.ar(
			FoaPanB.ar(
				MdaPiano.ar(220, Impulse.kr(0.5), release: 2) * 0.1,
				LFSaw.kr(0.1).range(0,2pi),
				LFSaw.kr(0.11).range(0,2pi),
			),
			LFSaw.kr(0.12).range(1,100)), d)
	}.play;
});
)

// Stop it:
CmdPeriod.run;