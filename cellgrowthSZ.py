# SZ 
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

# parameters
# specific growth rate, \mu
mu_min = 2e-2	# minimum specific growth rate [=] 1/h
mu_max = 6.5e-2	# maximum specific growth rate [=] 1/h
K_glc = 3e-2	# Monod constant for glucose [=] mM
K_gln = 3e-3	# " " " glutamine [=] mM
# specific death rate, \mu_{d}
mu_d_max = 1e-2	# maximum specfic death rate [=] 1/h
K_d_amm = 15	# constant for cell death due to ammonia accumulation [=] mM
d_n = 2.3 		# the exponent in the equation
# GLN glutamine differential equation
K_d_gln = 9e-3	# constant for glutamine degradation [=] 1/h
Y_x_gln = 4e8 	# yield of cells on glutamine [=] cells/mmol
Y_gln_glu = 1 	# yield of glutamine from glutamate [=] mmol/mmol
a1 = 3.4e-13	# alpha_1 of glutamine maintenance coefficient [=] mM/L/cell/h
a2 = 4 			# alpha_2 " " " " [=] mM
# GLC glucose differential equation
Y_x_glc = 1.4e8 # yield of cells on glucose [=] cells/mmol
M_glc = 4.8e-14	# maintenance coefficient for glucose [=] mmol/cell/h
# AMM ammonia differential equation
Y_amm_gln = 9e-1 # yield of ammonia on glutamine [=] mmol/mmol
# X_d dead cells differential equation
K_lysis = 1.3e-2 # Monod constant for lyssis [=] mM

# Additional parameters that involve other amino acids; expected to inhibit cell growth
K_arg = 2.5e-2
K_asp = 1e-1
K_his = 1e-2
K_ile = 5e-2
K_leu = 1.5e-2
K_lys = 2e-2
K_phe = 5e-2
K_ser = 2.5e-2
K_thr = 5e-2
K_val = 2.5e-2
Y_ala_x = 8e-12
Y_arg_asp = 1e-2
Y_arg_glu = 1e-2
Y_arg_pro = 1e-2
Y_asn_asp = 1.8e-1 
Y_asp_arg = 1e-2
Y_asp_x = 1e-15
Y_cys_ser = 1 
Y_glu_arg = 1e-3
Y_glu_gln = 2e-1
Y_glu_his = 1
Y_glu_pro = 1e-2
Y_gly_ser = 4e-1
Y_glu_x = 2e-16
Y_lac_glc = 1.2
Y_lys_x = 2e-14
Y_pro_arg = 1.2
Y_pro_glu = 1
Y_ser_gly = 1e-1
Y_tyr_phe = 1
Y_x_ala = 1.5e10
Y_x_arg = 4.6e9
Y_x_asp = 2.5e9
Y_x_cys = 2e9
Y_x_glu = 6.5e9
Y_x_his = 2.4e10
Y_x_ile = 6.85e9
Y_x_leu = 2.5e9
Y_x_lys = 6.3e9
Y_x_met = 1.9e10
Y_x_phe = 1.4e10
Y_x_pro = 1e11
Y_x_ser = 1.3e9
Y_x_thr = 1e10
Y_x_tyr = 4.3e9
Y_x_val = 6e9

# ODE function
def HEK293(t, w): # inputs: time value, solution vector at current iteration
	# decompose w vector
	Xv = w[0]
	Xd = w[1]
	GLC = w[2]
	GLN = w[3]
	AMM = w[4]
	ALA = w[5]
	ARG = w[6]
	ASN = w[7]
	ASP = w[8]
	CYS = w[9]
	GLU = w[10]
	GLY = w[11]
	HIS = w[12]
	ILE = w[13]
	LEU = w[14]
	LYS = w[15]
	MET = w[16]
	PHE = w[17]
	PRO = w[18]
	SER = w[19]
	THR = w[20]
	TYR = w[21]
	VAL = w[22]
	LAC = w[23]
	# specfic growth and death rates
	mu = mu_min + (mu_max-mu_min)*GLC*GLN/(K_glc+GLC)/(K_gln+GLN) \
		* ASP*ARG*VAL*LYS*THR/(K_asp+ASP)/(K_arg+ARG)/(K_val+VAL)/(K_lys+LYS)/(K_thr+THR) \
		* HIS*SER*ILE*PHE*LEU/(K_his+HIS)/(K_ser+SER)/(K_ile+ILE)/(K_phe+PHE)/(K_leu+LEU)
	mu_d = mu_d_max/(1+(K_d_amm/AMM)**d_n)
	# intermediate variables for ODEs
	# these are independent
	M_gln = a1*GLN/(a2+GLN)
	Q_his = -mu/Y_x_his
	Q_ala = -mu/Y_x_ala + Y_x_ala
	Q_ile = -mu/Y_x_ile
	Q_leu = -mu/Y_x_leu
	Q_lys = -mu/Y_x_lys + Y_lys_x
	Q_met = -mu/Y_x_met
	Q_phe = -mu/Y_x_phe
	Q_thr = -mu/Y_x_thr
	Q_tyr = -mu/Y_x_tyr - Y_tyr_phe*Q_phe
	Q_val = -mu/Y_x_val

	# these are the rates of change of the amino acids and must be solved simultaneously
	#Q_asp = -mu/Y_x_asp - Y_asp_arg*Q_arg + Y_asp_x
	#Q_arg = -mu/Y_x_arg + Y_arg_glu*Q_glu + Y_arg_pro*Q_pro - Y_arg_asp*Q_asp
	#Q_pro = -mu/Y_x_pro + Y_pro_glu*Q_glu - Y_pro_arg*Q_arg
	#Q_glu = -mu/Y_x_glu + Y_glu_pro*Q_pro - Y_gly_his*Q_his
	A1 = np.array([[-1, -Y_asp_arg, 0, 0],
				   [-Y_arg_asp, -1, Y_arg_pro, Y_arg_glu],
				   [0, -Y_pro_arg, -1, Y_pro_glu],
				   [0, 0, Y_glu_pro, -1]   
				  ])
	b1 = np.array([[mu/Y_x_asp - Y_asp_x, mu/Y_x_arg, mu/Y_x_pro, mu/Y_x_glu + Y_glu_his*Q_his]]).T
	x1 = np.linalg.solve(A1, b1)
	Q_asp = x1[0]
	Q_arg = x1[1]
	Q_pro = x1[2]
	Q_glu = x1[3]

	# this is another linear system
	#Q_ser = -mu/Y_x_ser + Y_ser_gly*Q_gly
	#Q_cys = -mu/Y_x_cys - Y_cys_ser*Q_ser
	#Q_gly = -mu/Y_gly_ser*Q_ser
	A2 = np.array([[-1, 0, Y_ser_gly],
				   [-Y_cys_ser, -1, 0],
				   [-mu/Y_gly_ser, 0, -1]
				  ])
	b2 = np.array([[mu/Y_x_ser, mu/Y_x_cys, 0]]).T
	x2 = np.linalg.solve(A2, b2)
	Q_ser = x2[0]
	Q_cys = x2[1]
	Q_gly = x2[2]

	Q_gln = -mu/Y_x_gln - M_gln + Y_gln_glu*Q_glu
	Q_glc = -mu/Y_x_glc - M_glc 
	Q_amm = -Y_amm_gln*Q_gln
	Q_asn = -Y_asn_asp*Q_asp
	Q_lac = -Y_lac_glc*Q_glc

	# ODE
	dXv = (mu-mu_d)*Xv
	#dXd = (mu_d-K_lysis)*Xd
	dXd = (mu_d)*Xd
	dGLN = Q_gln*Xv - K_d_gln*GLN
	dGLC = Q_glc*Xv
	dAMM = Q_amm*Xv + K_d_gln*GLN
	dALA = Q_ala*Xv
	dARG = Q_arg*Xv
	dASN = Q_asn*Xv
	dASP = Q_asp*Xv
	dCYS = Q_cys*Xv
	dGLU = Q_glu*Xv
	dGLY = Q_gly*Xv
	dHIS = Q_his*Xv
	dILE = Q_ile*Xv
	dLEU = Q_leu*Xv
	dLYS = Q_lys*Xv
	dMET = Q_met*Xv
	dPHE = Q_phe*Xv
	dPRO = Q_pro*Xv
	dSER = Q_ser*Xv
	dTHR = Q_thr*Xv
	dTYR = Q_tyr*Xv
	dVAL = Q_val*Xv
	dLAC = Q_lac*Xv 
	return np.array([dXv, dXd, dGLN, dGLC, dAMM,
					 dALA, dARG, dASN, dASP, dCYS, dGLU, dGLY, dHIS, dILE,
					 dLEU, dLYS, dMET, dPHE, dPRO, dSER, dTHR, dTYR, dVAL, dLAC
					])

# cell media initial conditions
GLC_0 = 40		# glucose concentration [=] mM
GLN_0 = 4 		# glutamine concentration [=] mM
AMM_0 = 1e-10	# ammonia concentration [=] mM 

# first cell growth stage is fixed. 
X0 = 1e6			# inoculum, total number of cells
Xv0 = X0*.95		# Assume 95% viability
Xd0 = X0-Xv0 		# assume 5% dead cells or 95% viable cells

IC = np.array([Xv0, Xd0])
# construct a new IC vector by appending a list of the remaining substances in order of:
# glc, gln, amm, ala, arg, asn, asp, cys, glu, gly, his, ile, leu, lys, met, phe, pro, ser, thr, tyr, val, lac
IC_aa = np.array([GLC_0, GLN_0, AMM_0, 1.84, 4.06, 2.33, 1.8, .61, 2.22, 2.25, 0.54, 1.93, 2.32, 6.84, .56, .99, .53, 2.79, 3.23, .62, 1.96, 1e-10])
IC = np.append(IC, IC_aa)
#print(np.size(IC))

v = np.array([.1, 1, 5, 20, 100]) 	# vector of volumes [=] L
v = v/1000 # convert to L
t = np.array([16, 36, 48, 72, 80])			# vector of times [=] hours
viable = [Xv0/v[0]] 						# vector of viable cell density initial conditions
dead = [Xd0/v[0]]							# vector of dead cell density initial conditions
multiply = []								# vector of cell density multipliers from time inoculum to harvest
cell_count = [1e6]							# vector of total cell count
desired_count = 2.16e12

for i in range(len(v)): # iteratre through all passages
	# make initial condition vector for cell concentrations
	cell_density = np.array([viable[i], dead[i]])
	IC = np.append(cell_density, IC_aa) # append cell media concentrations to cell concentrations
	passage = integrate.solve_ivp(HEK293, (0, t[i]), IC, rtol=1e-9, max_step=.5) # solve ODEs
	final_density = passage.y[0][-1]	# final cell density when cells are harvested at passage i
	Xd_t = passage.y[1][-1]				# pass the number of dead cells to the next passage ICs.
	mult = final_density/cell_density[0]	# find the ratio between final density and intial density
	multiply.append(mult)					# record this multiplier in the 'multiply' list
	count = final_density*v[i]				# record the cell count
	cell_count.append(count)				# add cell count to cell count list
	print(i, f'{final_density:.2e}', f'{count:.2e}')	# print data in terminal for debugging
	# dilute the cells to use as the intial cell density for the next passage
	if i < len(v)-1:			# len(v) = 4, add initial conditions until i = 4 or while i <= 3
		viable.append(count/v[i+1]) # divide the cell count by the next volume of the passage
		dead.append(Xd_t*v[i]/v[i+1])	# do the same for dead cells
	else: # for the last passage, find the maximum cell density
		max_density = passage.y[0][-1]
		index = np.where(passage.y[0] == max_density)
		print('max_time', passage.t[index])
	# plotting
	time = passage.t + np.sum(t[0:i])
	label_string = 'passage ' + str(i+1)
	plt.plot(time, passage.y[0], label=label_string)

print('mult', multiply)
print('inoculum density', viable)
print('total cells', [f"{x:.2e}" for x in cell_count])
print('total time', np.sum(t)/24, 'days')
print(desired_count<cell_count[-1]) 

plt.title('Cell density vs time')
plt.xlabel('time / hours')
plt.ylabel('cell density / $cells\\cdot L^{-1}$')
#plt.ylim(1e4,9e6)
plt.legend()
plt.show()


