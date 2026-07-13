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

#############################################################################
#THE NEWTON RAPHSON ITERATIVE PROCESS#

def theta_from_entropy(SA, entropy_target, tolerance = 1e-14, max_iters = 100):
    Theta = initial_theta(SA, entropy_target)
    for i in range(max_iters):
        ent, ent_d = entropy(SA, Theta)
        f = ent - entropy_target
        step = f / ent_d  
        Theta -= step 
        if np.all(abs(step) < tolerance):
            break 
    return Theta 

#############################################################################


def potential_enthalpy(theta):
    """
    Definition:
    Calculating the potential enthalpy which is necessary to calculate the conservative temperature. 
    The equation for this process is found in the TEOS10 manual. 

    Arguments: 
    arg[1] : Theta (float) - 

    Output: 
    The potential enthalpy
    """

    h0 = C_p * theta 
    return h0 

#############################################################################


def conservative_T(h0):
    """
    Definition:
    Calculating the conservative temperature from the potential entalpy

    Arguments: 
    arg[1] : h0 (float) - the potential entalphy calculated in the function above  
    """

    Theta = h0 / C_p
    return Theta

#############################################################################


def CT(SA, entropy_tar):
    """
    Runs all above functions at the same time 
    """
    theta = theta_from_entropy(SA, entropy_tar)
    h0 = potential_enthalpy(theta)
    Theta = conservative_T(h0)
    print(f'theta = {theta}, h0 = {h0}, Theta = {Theta}' )
    return Theta

#############################################################################


def coeff_75term_polynomial(SA, entropy_tar, P=None):

    """
    Definition: 
    Implementing the 75-term expression for specific volume of seawater - with the use of Conservative Temperature Theta. 
    The specific volume is expressed as an efficient polymomial in the TEOS10 manual for thermodynamic equations -
    Thus we are adapting the same procedure and defining the coefficients as a Python dictionary.

    The expression is defined by Roquet et al. (2015) and described in Appendix K of the TEOS10 manual: 
    
    ##Roquet, F., G. Madec, T. J. McDougall and P. M. Barker, 2015: Accurate polynomial
    expressions for the density and specific volume of seawater using the TEOS-10 standard.
    Ocean Modelling, 90, 29-43, http://dx.doi.org/10.1016/j.ocemod.2015.04.002 ##

    Returns:
    The specific volume 
    """

    coeff_75term = {
        (0,0,0) : 1.0769995862e-3,
        (1,0,0) : -3.1038981976e-4, 
        (2,0,0) : 6.6928067038e-4,
        (3,0,0) : -8.5047933937e-4,
        (4,0,0) : 5.8086069943e-4,
        (5,0,0) : -2.1092370507e-4,
        (6,0,0) : 3.1932457305e-5,


        (0,1,0) : -1.5649734675e-5,
        (1,1,0) : 3.5009599764e-5,
        (2,1,0) : -4.3592678561e-5,
        (3,1,0) : 3.4532461828e-5,
        (4,1,0) : -1.1959409788e-5,
        (5,1,0) : 1.3864594581e-6,

        (0,2,0) : 2.7762106484e-5,
        (1,2,0) : -3.7435842344e-5,
        (2,2,0) : 3.5907822760e-5,
        (3,2,0) : -1.8698584187e-5,
        (4,2,0) : 3.8595339244e-6,

        (0,3,0) : -1.6521159259e-5,
        (1,3,0) : 2.4141479483e-5,
        (2,3,0) : -1.4353633048e-5,
        (3,3,0) : 2.2863324556e-6,

        (0,4,0) : 6.9111322702e-6,
        (1,4,0) : -8.7595873154e-6,
        (2,4,0) : 4.3703680598e-6,
        
        (0,5,0) : -8.0539615540e-7,
        (1,5,0) : -3.3052758900e-7, 
        (0,6,0) : 2.0543094268e-7,

        (0,0,1) : -6.0799143809e-5,
        (1,0,1) : 2.4262468747e-5,
        (2,0,1) : -3.4792460974e-5,
        (3,0,1) : 3.7470777305e-5,
        (4,0,1) : -1.7322218612e-5,
        (5,0,1) : 3.0927427253e-6,

        (0,1,1) : 1.8505765429e-5,
        (1,1,1) : -9.5677088156e-6,
        (2,1,1) : 1.1100834765e-5,
        (3,1,1) : -9.8447117844e-6,
        (4,1,1) : 2.5909225260e-6,
        
        (0,2,1) : -1.1716606853e-5,
        (1,2,1) : -2.3678308361e-7,
        (2,2,1) : 2.9283346295e-6,
        (3,2,1) : -4.8826139200e-7,

        (0,3,1) : 7.9279656173e-6,
        (1,3,1) : -3.4558773655e-6, 
        (2,3,1) : 3.1655306078e-7,

        (0,4,1) : -3.4102187482e-6,
        (1,4,1) : 1.2956717783e-6,
        (0,5,1) : 5.0736766814e-7,

        (0,0,2) : 9.9856169219e-6,
        (1,0,2) : -5.8484432984e-7, 
        (2,0,2) : -4.8122251597e-6,
        (3,0,2) : 4.9263106998e-6, 
        (4,0,2) : -1.7811974727e-6, 
        
        (0,1,2) : -1.1736386731e-6, 
        (1,1,2) : -5.5699154557e-6, 
        (2,1,2) : 5.4620748834e-6,
        (3,1,2) : -1.3544185627e-6, 

        (0,2,2) : 2.1305028740e-6,
        (1,2,2) : 3.9137387080e-7,
        (2,2,2) : -6.5731104067e-7,

        (0,3,2) : -4.6132540037e-7,
        (1,3,2) : 7.7618888092e-9,

        (0,4,2) : -6.3352916514e-8,

        (0,0,3) : -1.1309361437e-6,
        (1,0,3) : 3.6310188515e-7,
        (2,0,3) : 1.6746303780e-8,
        (0,1,3) : -3.6527006553e-7,
        (1,1,3) : -2.7295696237e-7,
        (0,2,3) : 2.8695905159e-7,
        (0,0,4) : 1.0531153080e-7,
        (1,0,4) : -1.1147125423e-7,
        (0,1,4) : 3.1454099902e-7,
        (0,0,5) : -1.2647261286e-8,
        (0,0,6) : 1.9613503930e-9,}
    
    v_u = 1 #m³ kg⁻1
    S_au = (SSO / 35)
    sfac = 1 / 40 * S_au
    s = np.sqrt(sfac * (SA + 24))
    #s = np.sqrt(SA + 24 / S_au)

    Theta = CT(SA, entropy_tar)
    print(Theta) 
    tau = Theta / Theta0
    print(f's = {s}, tau = {tau}')
    v_hat = 0
    for (i,j,k), coeff in coeff_75term.items():
        if P is not None: 
            raise ValueError(f'The function is not adapted for varying pressure yet. Please ensure sea surface input where the pressure is equal to zero and given as None')
        else: 
            z = 0 
            v_hat += coeff * (s ** i) * (tau **j) * (z**k) 
    v_hat *=  v_u 
    return v_hat 

#############################################################################


def density_field(SA, entropy_tar):
    """
    Definition:
    Calculating the density field based on the conservative temperature and specific volume

    Arguments: 
    arg [1] : SA (float) 
    arg [2] : entropy target (float)
    """

    v_hat = coeff_75term_polynomial(SA, entropy_tar) 
    #inverse of v_hat is the density 
    sigma_0 = 1 / v_hat 
    sigma_0_anomaly = sigma_0 - 1000 #kg m⁻3
    return sigma_0, sigma_0_anomaly


#############################################################################

#to create a entropy target - we run: 
"""
e_target, _ = entropy(SA, Theta)
"""