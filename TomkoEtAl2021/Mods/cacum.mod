COMMENT
	calcium accumulation into a volume of area*depth next to the
	membrane with a decay (time constant tau) to resting level
	given by the global calcium variable cai0_ca_ion
	Modified to include a resting current (irest) and peak value
	(cmax)
	i is a dummy current needed to force a BREAKPOINT
ENDCOMMENT

NEURON {
	SUFFIX cacum
	USEION ca READ ica WRITE cai
	NONSPECIFIC_CURRENT i
	RANGE depth, tau, cai0, cmax, B
	RANGE flux, flux_per_um
}

UNITS {
	(mM) = (milli/liter)
	(mA) = (milliamp)
        F = (faraday) (coulombs)
       (um) = (micron)
       (umms) = (micron ms)
	PI = (pi) (1)
}

PARAMETER {
	depth = 0.1 (um)	: assume volume = area*depth
	irest = 0  (mA/cm2)		: to be initialized in hoc	
					     tau = 30 (ms)
        B = 1                           : ca buffer capacity
	cai0 = 70e-6 (mM)	: Requires explicit use in INITIAL
			: block for it to take precedence over cai0_ca_ion
			: Do not forget to initialize in hoc if different
			: from this default.
       
}


ASSIGNED {
	ica (mA/cm2)
	cmax
	i  	 (mA/cm2)
	flux (1/ms)
	flux_per_um (1/umms)
	area (um2)
        diam (um)
}

STATE {
	cai (mM)
}

INITIAL {
	cai = cai0
	:irest = ica
	cmax=cai
}

BREAKPOINT {
	SOLVE integrate METHOD derivimplicit
	if (cai>cmax) {cmax=cai}
	i=0
}

DERIVATIVE integrate {
	cai' = (irest-ica)/depth/F/2/B * (1e4) + (cai0 - cai)/tau
	flux = (irest-ica)/F/2*area*(1e11)
        flux_per_um = flux/PI/diam
}
