TITLE l-calcium channel
: l-type calcium channel


UNITS {
	(mA) = (milliamp)
	(mV) = (millivolt)

	FARADAY = 96520 (coul)
	R = 8.3134 (joule/degC)
	KTOMV = .0853 (mV/degC)
}

PARAMETER {
	v (mV)
	celsius 	(degC)
	gbar=.003 (mho/cm2)
	ki=.0005 (mM)
	cai (mM)
	cao (mM)
	tau_cdi=43 (ms)
        tfa=1
}


NEURON {
	SUFFIX cal12
	USEION ca READ cai, cao WRITE ica
        RANGE gbar,cai
        GLOBAL minf,tau
}

STATE {
          m
	  cdi
}

ASSIGNED {
	ica (mA/cm2)
        gcal (mho/cm2)
        minf
	cdiinf
        tau   (ms)
}

INITIAL {
	rate(v)
	m = minf
        cdi = cdiinf
}

BREAKPOINT {
     SOLVE state METHOD cnexp
	
	gcal = gbar*m*m*cdi
	ica = gcal*ghk(v,cai,cao)

}

FUNCTION h2(cai(mM)) {
	h2 = ki^3/(ki^3+cai^3)
}


FUNCTION ghk(v(mV), ci(mM), co(mM)) (mV) {
        LOCAL nu,f

        f = KTF(celsius)/2
        nu = v/f
        ghk=-f*(1. - (ci/co)*exp(nu))*efun(nu)
}

FUNCTION KTF(celsius (DegC)) (mV) {
        KTF = ((25./293.15)*(celsius + 273.15))
}


FUNCTION efun(z) {
	if (fabs(z) < 1e-4) {
		efun = 1 - z/2
	}else{
		efun = z/(exp(z) - 1)
	}
}

FUNCTION alp(v(mV)) (1/ms) {
	TABLE FROM -150 TO 150 WITH 200
	alp = 15.69*(-1.0*v+81.5)/(exp((-1.0*v+81.5)/10.0)-1.0)
}

FUNCTION bet(v(mV)) (1/ms) {
	TABLE FROM -150 TO 150 WITH 200
	bet = 0.29*exp(-v/10.86)
}

DERIVATIVE state {  
        rate(v)
	cdiinf = h2(cai)
        m' = (minf - m)/tau
	cdi' = (cdiinf - cdi)/tau_cdi
}

PROCEDURE rate(v (mV)) { :callable from hoc
        LOCAL a
        a = alp(v)
        tau = 1/(tfa*(a + bet(v)))
        minf = tfa*a*tau
}
 



















