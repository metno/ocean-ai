#import packages 
import numpy as np 

#Global variables 
Theta0 = 40.0 #Celsius
T0 = 273.15 # Kelvin
SSO = 35.16504
C_p = 3991.86795711963 # J/kg/K
Alpha = -9.309495003228781 # J/kg/K

#Gibbs polynomials 
p_8 = {
    (0,0) : - 3.7102436569e-01,
    (1,0) :  3.0834502223e-04  , 
    (2,0) : - 3.2916987818e+00, 
    (3,0) :  7.2818259040e+00 , 
    (4,0) : - 5.6657256773e+00, 
    (5,0) :  2.8402903938e+00 , 
    (6,0) : - 8.9615123138e-01, 
    (7,0) : 1.0035964794e-01  ,
    (8,0) : 1.8140964105e-03  ,
    (0,1) : 3.0779211774e-02  ,
    (1,1) : 1.5006196848e-03  ,
    (2,1) : 1.2029316021e-01  ,
    (3,1) : 3.7464975805e-01  ,
    (4,1) : - 6.0590428227e-01,
    (5,1) : 6.4365865093e-02  ,
    (6,1) : 2.4626795446e-02  ,
    (7,1) : - 1.0335853091e-02 ,
    (0,2) : 2.3045093877e+00 ,
    (1,2) : - 5.4154968624e-03 ,
    (2,2) : - 2.5098282844e+00,
    (3,2) : 1.9163697628e-02,
    (4,2) : 9.6230320461e-02,
    (5,2) : 3.7953034101e-02,
    (6,2) : - 5.1206778774e-04,
    (0,3) : - 8.4974032876e-01 ,
    (1,3) : - 1.3727475447e-02,
    (2,3) : 8.6969911602e-01,
    (3,3) : 1.1127539375e-01,
    (4,3) : - 8.7616123860e-02,
    (5,3) : - 1.6250024449e-02,
    (0,4) : 4.1807750439e-01,
    (1,4) : 5.1388181100e-02,
    (2,4) : - 3.1917000611e-01,
    (3,4) : - 4.4999965986e-02,
    (4,4) : 3.3822211876e-02,
    (0,5) : - 1.9191736060e-01,
    (1,5) : - 5.3890029514e-02,
    (2,5) : 9.3472917957e-02,
    (3,5) : - 4.9779616704e-04,
    (0,6) : 6.6066546976e-02,
    (1,6) : 2.4144978278e-02,
    (2,6) : -1.2850921670e-02,
    (0,7) : -1.3678360946e-02,
    (1,7) : -4.1337102429e-03,
    (0,8) : 1.1180283076e-03}

#############################################################################

#Gibbs empirical polynomial function
def P_8(s,tau):
    """
    Definition: 
    Calculating the Gibbs polynomials and it's derivatives - based on the Gibbs function
    from TEOS10. All empirical values are given in Appendix B of the following article: 
    https://doi.org/10.5194/os-19-1719-2023

    The derived function is differentiated with respect to the dimensionless variable T,
    and is thus denoted g_T later in the code. 

    Arguments: 
    arg[1] : float - s ~ [Absolute Salinity / SSO]** - (1/2) 
    arg[2] : float - Tau ~ (Theta / 40.0) 

    Returns: 
    The Gibbs sum of the gibbs polynomial function as well as the derived polynomial function. 
    """
    gibbs = 0.0
    gibbs_dT = 0.0
    for (i,j), coeff in p_8.items():
        gibbs += coeff * (s**i) * (tau**j) 
        if j > 0:
            gibbs_dT += j * coeff * s **i * tau**(j-1)
    return gibbs, gibbs_dT

#############################################################################

#Entropy calculation 
def entropy(SA, Theta):
    """
    Definition: 
    Function for calculating the entropy - also based on appendix B in article: 
    https://doi.org/10.5194/os-19-1719-2023 - TEOS10. 
    The function takes in both the differentiated and the regular gibbs polynomal in it's calculations. 

    Arguments:
    arg[1] : float - SA ~ Currently salinity (must be changed to Absolute Salinity when more layers are included) 
    arg[2] : float - Theta ~ The Conservative Temperature 
    
    Output: 
    Returns the specific entropy for both the differentiated Gibbs with respect 
    to T, as well as the original entropy that's not differentiated. 
    """

    s = np.sqrt(SA / SSO)
    tau = Theta / Theta0

    log_term1 = C_p * np.log(1 + (Theta / T0))
    log_term2 = Alpha * (SA / SSO) * np.log(SA/SSO)  
    log_term1_differentiated = C_p / (T0 + Theta)    

    g, g_T = P_8(s, tau)

    entropy_analytical = log_term1 + log_term2 + g 
    entropy_analytical_differentiated = log_term1_differentiated + g_T * (1/Theta0) #to convert to degrees

    return entropy_analytical, entropy_analytical_differentiated

#############################################################################

#Finding the approximated conserved temperature 
def initial_theta(SA, entropy_target):
    """
    Definition:
    Function dedicated to finding the Conserved Temperature Theta from the entropy. 
    The conserved temperature is needed to calculate the density field of the ocean surface. 
    
    Theta is found with the use of an Newton Raphson iterativ technique, where we seek
    convergence by using differentiated steps in our function. To do so, we will follow some key aspect
    from the given TEOS manual: https://www.teos-10.org/pubs/gsw/pdf/t_from_entropy.pdf (eq1-eq7). 
    Based on the McDougall Article - we will also make an inital guess of the differentiated 
    specific entropy with regards to the absolute salinity - to improve convergence

    To avvoid complex equations, we will use an implemented polynomial solution based on the empirical values
    where T0 is used as a reference, becuase the potential temperature is likely close to this values. 
    We also account for the changes in s - which is the salinity divided by the standard seawater salinity. 

    Arguments:
    arg[1] :  float - SA ~ Currently salinity (must be changed to Absolute Salinity when more layers are included) 
    arg[2] : float - Entropy results from the entropy function
    
    Outputs:
    The approximated value of conserved temperature, when convergence is reached beyond a given treshold. 
    """ 

    part1 = 1.0 - SA/SSO
    part2 = 1.0 - 0.05 * part1 
    ent = (C_p / T0) * part1 * (1.0 - 1.01 * part1)
    c = (entropy_target - ent) * (part2 / C_p)
    conv = T0 * (np.exp(c) - 1.0)
    return conv 

def theta_from_entropy(SA, entropy_target, tolerance = 1e-14, max_iters = 100):
    Theta = initial_theta(SA, entropy_target)
    for i in range(max_iters):
        ent, ent_d = entropy(SA, Theta)
        f = ent - entropy_target
        step = f / ent_d  
        Theta -= step 
        if abs(step) < tolerance:
            break 
    return Theta 


def potential_enthalpy(Theta):
    """
    Definition:
    Calculating the potential enthalpy which is necessary to calculate the conservative temperature. 
    The equation for this process is found in the TEOS10 manual. 

    Arguments: 
    arg[1] : Theta (float) - 

    Output: 
    The potential enthalpy
    """

    h0 = C_p * Theta 
    return h0 


        






 







