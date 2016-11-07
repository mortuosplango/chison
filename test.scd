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