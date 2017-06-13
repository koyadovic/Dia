# -*- coding: utf-8 -*-

from scipy.interpolate import interp1d
from fractions import Fraction
import numpy as np


"""
Util
"""
class LinearRegression(object):
    def __init__(self, x_list, y_list):
        assert type(x_list) == list, "x_list {} no es una lista".format(x_list)
        assert type(y_list) == list, "y_list {} no es una lista".format(y_list)
        assert len(x_list) == len(y_list), "el numero de elementos de x_list e y_list no coincide"

        x_data = np.array(x_list)
        y_data = np.array(y_list)
        A = np.vstack([x_data, np.ones(len(x_data))]).T
        self.m, self.b = np.linalg.lstsq(A, y_data)[0]
    
    @property
    def f(self):
        return lambda x: (x * self.m) + self.b

    @property
    def latex(self):
        _latex = ''
        fm = Fraction(self.m).limit_denominator()
        fb = Fraction(self.b).limit_denominator()
        if self.m < 0:
            _latex += '-'
        _latex += '\\frac{{{}}}{{{}}}x'.format(abs(fm.numerator), abs(fm.denominator))
        
        
        if self.b >= 0:
            _latex += '+'
        else:
            _latex += '-'
        
        _latex += '\\frac{{{}}}{{{}}}'.format(abs(fb.numerator), abs(fb.denominator))
        return _latex
    
    def data_to_plot(self, min_x, max_x):
        x = np.linspace(min_x, max_x)
        f = np.vectorize(self.f)
        y = f(x)
        return x, y


class PolynomialRegression(object):
    def __init__(self, x_list, y_list, degree):
        assert type(x_list) == list, "x_list {} no es una lista".format(x_list)
        assert type(y_list) == list, "y_list {} no es una lista".format(y_list)
        assert len(x_list) == len(y_list), "el numero de elementos de x_list e y_list no coincide"
        
        self._x = np.array(x_list)
        self._y = np.array(y_list)
        
        self._z = np.polyfit(self._x, self._y, degree)
    
    @property
    def f(self):
        return np.poly1d(self._z)
        

    @property
    def latex(self):
        _latex = u''
        degree = len(self._z)
        degree -= 1
        for c in self._z:
            fc = Fraction(c).limit_denominator()
            if _latex != '':
                if c >= 0:
                    _latex += u'+'
                else:
                    _latex += u'-'
            if degree > 1:
                _latex += u'\\frac{{{}}}{{{}}}x^{}'.format(abs(fc.numerator), abs(fc.denominator), degree) 
            elif degree == 1:
                _latex += u'\\frac{{{}}}{{{}}}x'.format(abs(fc.numerator), abs(fc.denominator))
            else:
                _latex += u'\\frac{{{}}}{{{}}}'.format(abs(fc.numerator), abs(fc.denominator))
            degree -= 1
        
        return _latex

    def data_to_plot(self, min_x, max_x):
        x = np.linspace(min_x, max_x)
        y = self.f(x)
        return x, y

        

class QuadraticInterpolation(object):
    def __init__(self, x_list, y_list):        
        assert type(x_list) == list, "x_list {} no es una lista".format(x_list)
        assert type(y_list) == list, "y_list {} no es una lista".format(y_list)
        assert len(x_list) == len(y_list), "el numero de elementos de x_list e y_list no coincide"

        x_data = np.array(x_list)
        y_data = np.array(y_list)
        
        self._func = interp1d(x_data, y_data, kind='quadratic')
    
    @property
    def f(self):
        return self._func



def mean(l):
    assert type(l) == list, "l {} no es una lista"
    if len(l) > 0:
        return sum(l) / float(len(l))
    else:
        return 0.


def median(l):
    assert type(l) == list, "l {} no es una lista"
    l.sort()
    e = len(l)
    if e > 0.:
        if e % 2:
            return l[e / 2]
        else:
            return (l[e / 2] + l[(e / 2) - 1]) / 2.
    else:
        return 0.



class LinearRegressionAproximator(object):
    _x_list = []
    _y_list = []
    _current_x_point = None

    def __init__(self, current_x_point):
        self._x_list = []
        self._y_list = []
        self._current_x_point = current_x_point
    
    def append_x_y_point(self, x_point, y_point):
        self._x_list.append(x_point)
        self._y_list.append(y_point)

    def current_value(self):
        if len(self._x_list) == 0:
            return None
        elif len(self._x_list) == 1:
            return self._y_list[0]
        else:
            regression = LinearRegression(self._x_list, self._y_list)
            return regression.f(self._current_x_point)
        
    def current_parameters(self):
        if len(self._x_list) < 2:
            return None, None
        else:
            regression = LinearRegression(self._x_list, self._y_list)
            return regression.m, regression.b



def round_not_zero(n, not_zeros=1):
    decs = 1
    not_zeros -= 1
    while True:
        n_rounded = round(n, decs)
        if n_rounded != 0.:
            return round(n, decs + not_zeros)
        decs += 1
        if decs > 50.:
            return 0.0
