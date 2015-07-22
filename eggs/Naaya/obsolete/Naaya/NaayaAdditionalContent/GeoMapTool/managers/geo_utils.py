#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "EWGeoMap"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania and Eau de Web 
#are Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)
#        Bogdan Grama (Finsiel Romania)
#        Iulian Iuga (Finsiel Romania)
#  Porting to Naaya: 
#        Cornel Nitu (Eau de Web)


#Python imports
import math

#Zope imports

#Product imports

PI = 3.14159265358979323
a = 6378137.0
f = 1/298.257223563
Ra = 6371007.1810824
Azeq_False_Easting = 4321000.0
Azeq_False_Northing = 3210000.0

PI_OVER_2 = (PI/2.0)
TWO_PI = (2.0*PI)
ONE = (1.0*PI/180)

# in radians
Azeq_Origin_Lat = (52.0*PI/180.0)
Azeq_Origin_Long = (10.0*PI/180.0)
abs_Azeq_Origin_Lat = (52.0*PI/180.0)
# in radians
Sin_Azeq_Origin_Lat = math.sin(Azeq_Origin_Lat)
Cos_Azeq_Origin_Lat = math.cos(Azeq_Origin_Lat)

class geo_utils:
    """
    Utils for working/converting Latitude/Longitude coordinates.

    D = Degrees
    M = Minutes
    S = Seconds
    C = cardinal (N, S, E or W)
    .m = Decimal Minutes
    .s = Decimal Seconds

    DM.m = Degrees, Minutes, Decimal Minutes (eg. 45o22.6333)
    D.d = Degrees, Decimal Degrees (eg. 45.3772o)
    DMS = Degrees, Minutes, Seconds (eg. 45o22'38")

    """

    def geoDMSToDd(self, D, M, S, C):
        try:
            D, M, S, sign = float(D), float(M), float(S), 1
            if C in ['W', 'S']: sign = -1
            return sign*((S/60 + M)/60 + D)
        except ValueError:
            return 0


    # Curent parameters
    # PROJCS["ETRS-LAEA5210",
    # GEOGCS["ETRS89",
    # DATUM["<custom>",
    # SPHEROID["GRS_1980",	6378137.0,298.257222101]],
    # PRIMEM["Greenwich",0.0],
    # UNIT["Degree",0.0174532925199433]],
    # PROJECTION["Lambert_Azimuthal_Equal_Area"],
    # PARAMETER["False_Easting",4321000.0],
    # PARAMETER["False_Northing",3210000.0],
    # PARAMETER["Central_Meridian",10.0],
    # PARAMETER["Latitude_Of_Origin",52.0],UNIT["Meter",1.0]]


    #Begin Convert_Geodetic_To_Azimuthal_Equidistant
    #The function Convert_Geodetic_To_Azimuthal_Equidistant converts geodetic (latitude and
    #longitude) coordinates to Azimuthal Equidistant projection (easting and northing)
    #coordinates, according to the current ellipsoid and Azimuthal Equidistant projection
    #parameters.  If any errors occur, the error code(s) are returned by the
    #function, otherwise AZEQ_NO_ERROR is returned.
    #Latitude          : Latitude (phi)           (input)
    #Longitude         : Longitude (lambda)       (input)
    #Easting           : Easting (X) in meters               (output)
    #Northing          : Northing (Y) in meters              (output)

    def geoDdToAzimuthalEquidistant(self, Latitude, Longitude):
        Latitude = Latitude*PI/180
        Longitude = Longitude*PI/180

        dlam = 0.0        #Longitude - Central Meridan
        k_prime = 0.0     #scale factor
        c = 0.0           #angular distance from center
        slat = math.sin(Latitude)
        clat = math.cos(Latitude)
        cos_c = 0.0
        sin_dlam = 0.0
        cos_dlam = 0.0
        Ra_kprime = 0.0
        Ra_PI_OVER_2_Lat = 0.0

        dlam = Longitude - Azeq_Origin_Long
        if (dlam > PI):
            dlam -= TWO_PI
        if (dlam < -PI):
            dlam += TWO_PI
        sin_dlam = math.sin(dlam)
        cos_dlam = math.cos(dlam)
        if (math.fabs(abs_Azeq_Origin_Lat - PI_OVER_2) < 1.0e-10):
            if (Azeq_Origin_Lat >= 0.0):
                Ra_PI_OVER_2_Lat = Ra * (PI_OVER_2 - Latitude)
                tmp_Easting = Ra_PI_OVER_2_Lat * sin_dlam + Azeq_False_Easting
                tmp_Northing = -1.0 * (Ra_PI_OVER_2_Lat * cos_dlam) + Azeq_False_Northing
            else:
                Ra_PI_OVER_2_Lat = Ra * (PI_OVER_2 + Latitude)
                tmp_Easting = Ra_PI_OVER_2_Lat * sin_dlam + Azeq_False_Easting
                tmp_Northing = Ra_PI_OVER_2_Lat * cos_dlam + Azeq_False_Northing
        elif (abs_Azeq_Origin_Lat <= 1.0e-10):
            cos_c = clat * cos_dlam
            if (math.fabs(fabs(cos_c) - 1.0) < 1.0e-14):
                if (cos_c >= 0.0):
                    tmp_Easting = Azeq_False_Easting
                    tmp_Northing = Azeq_False_Northing
            else:
                c = acos(cos_c)
                k_prime = c / sin(c)
                Ra_kprime = Ra * k_prime
                tmp_Easting = Ra_kprime * clat * sin_dlam + Azeq_False_Easting
                tmp_Northing = Ra_kprime * slat + Azeq_False_Northing
        else:
            cos_c = (Sin_Azeq_Origin_Lat * slat) + (Cos_Azeq_Origin_Lat * clat * cos_dlam)
            if (math.fabs(math.fabs(cos_c) - 1.0) < 1.0e-14):
                if (cos_c >= 0.0):
                    tmp_Easting = Azeq_False_Easting
                    tmp_Northing = Azeq_False_Northing
            else:
                c = math.acos(cos_c)
                k_prime = c / math.sin(c)
                Ra_kprime = Ra * k_prime
                tmp_Easting = Ra_kprime * clat * sin_dlam + Azeq_False_Easting
                tmp_Northing = Ra_kprime * (Cos_Azeq_Origin_Lat * slat - Sin_Azeq_Origin_Lat * clat * cos_dlam) + Azeq_False_Northing

        return tmp_Easting, tmp_Northing

# The coordinates transcalculation form Lambert Asimuthal Equal Area are quite similar wilth Azimuthal Equidistant
# The function Convert_Azimuthal_Equidistant_To_Geodetic converts Azimuthal_Equidistant projection
# (easting and northing) coordinates to geodetic (latitude and longitude)
# coordinates, according to the current ellipsoid and Azimuthal_Equidistant projection
# coordinates.  If any errors occur, the error code(s) are returned by the
# function, otherwise AZEQ_NO_ERROR is returned.


# Easting           : Easting (X) in meters                  (input)
# Northing          : Northing (Y) in meters                 (input)
# Latitude          : Latitude (phi) in radians              (output)
# Longitude         : Longitude (lambda) in radians          (output)
# decimals          :Number of decimals for DD               (input)
# format:           :MATH using minus for negative, GEOG using E/W;N/S
# type              :DD 15.4848; DMS 05*18'48''


# Curent parameters
# PROJCS["ETRS-LAEA5210",
# GEOGCS["ETRS89",
# DATUM["<custom>",
# SPHEROID["GRS_1980",	6378137.0,298.257222101]],
# PRIMEM["Greenwich",0.0],
# UNIT["Degree",0.0174532925199433]],
# PROJECTION["Lambert_Azimuthal_Equal_Area"],
# PARAMETER["False_Easting",4321000.0],
# PARAMETER["False_Northing",3210000.0],
# PARAMETER["Central_Meridian",10.0],
# PARAMETER["Latitude_Of_Origin",52.0],UNIT["Meter",1.0]]

def transcalc(inEasting, inNorthing, inNrDecimals):
    dx = 0
    dy = 0
    rho = 0
    #  height above ellipsoid
    c = 0
    #  angular distance from center
    sin_c = 0
    cos_c = 0
    dy_sinc = 0
    a = 6378137.0
    f = 1/298.257223563
    Ra = 6371007.1810824
    Azeq_False_Easting = 4321000.0
    Azeq_False_Northing = 3210000.0
    PI = 3.14159265358979323
    PI_OVER_2 = (PI/2.0)
    TWO_PI = (2.0*PI)
    ONE = (1.0*PI/180)
    # in radians
    Azeq_Origin_Lat = (52.0*PI/180.0)
    Azeq_Origin_Long = (10.0*PI/180.0)
    abs_Azeq_Origin_Lat = (52.0*PI/180.0)
    # in radians
    Sin_Azeq_Origin_Lat = math.sin(Azeq_Origin_Lat)
    Cos_Azeq_Origin_Lat = math.cos(Azeq_Origin_Lat)
    Error_Code = "AZEQ_NO_ERROR"
    if (Error_Code == "AZEQ_NO_ERROR"):
        dy = inNorthing-Azeq_False_Northing
        dx = inEasting-Azeq_False_Easting
        rho = math.sqrt(dx*dx+dy*dy)
        if (abs(rho)<=0.0000000001):
            Latitude = Azeq_Origin_Lat
            Longitude = Azeq_Origin_Long
        else:
            c = rho/Ra
            sin_c = math.sin(c)
            cos_c = math.cos(c)
            dy_sinc = dy*sin_c
            dy_sinc = dy*sin_c
            Latitude = math.asin((cos_c*Sin_Azeq_Origin_Lat)+((dy_sinc*Cos_Azeq_Origin_Lat)/rho))
            if (abs(abs_Azeq_Origin_Lat-PI_OVER_2)<0.0000000001):
                if (Azeq_Origin_Lat>=0.0):
                    Longitude = Azeq_Origin_Long+math.atan2(dx, -dy)
                else:
                    Longitude = Azeq_Origin_Long+math.atan2(dx, dy)
            else:
                Longitude = Azeq_Origin_Long+math.atan2((dx*sin_c), ((rho*Cos_Azeq_Origin_Lat*cos_c)-(dy_sinc*Sin_Azeq_Origin_Lat)))
        if (Latitude>PI_OVER_2):
            Latitude = PI_OVER_2
        elif (Latitude<-PI_OVER_2):
            Latitude = -PI_OVER_2
        if (Longitude>PI):
            Longitude = PI
        elif (Longitude<-PI):
            Longitude = -PI
    Latitude = (Latitude*180.0/PI)
    Longitude = (Longitude*180.0/PI)
    # starting diplay work
    # number of decimals
    Latitude_display = 0
    Longitude_display = 0
    decim = 0
    decim = pow(10, inNrDecimals)
    Latitude_display = (math.ceil(Latitude*decim))/decim
    Longitude_display = (math.ceil(Longitude*decim))/decim

    return Longitude_display, Latitude_display