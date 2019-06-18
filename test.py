from time import sleep
from pyrpl import pyrpl

#reload everything
p = pyrpl.Pyrpl(hostname="131.246.145.91")
r = p.rp
#p = pyrpl.Pyrpl(config='test_19_05_03')


# pass asg signal through pid0 with a simple integrator - just for fun (detailed explanations for pid will follow)
#r.pid0.input = 'asg1'
#r.pid0.ival = 0 # reset the integrator to zero
#r.pid0.i = 1000 # unity gain frequency of 1000 hz
#r.pid0.p = 1.0 # proportional gain of 1.0
#print r.pid0.help()