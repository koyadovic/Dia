# -*- coding: utf-8 -*-

class Shape(object):
    """
    Objeto que facilita el trabajo con Shapes
    """
    def __init__(self, shape):
        self._check_shape(shape)
        self._shape = shape
        self._start_pointer = 0
        self._end_pointer = self.end_x

    def __getitem__(self, index):
        result = self._shape[index]
        return result

    @staticmethod
    def _check_shape(shape):
        assert type(shape) is list, "shape ha de ser una lista"
        assert len(shape) > 0, "shape está vacío"
        assert type(shape[0]) is list and len(shape[0]) == 2, "shape tiene que estar formado por pares [x, y]"
        #assert shape[0] == [0, 0] and shape[-1][1] == 0, "shape está mal formado, ha de comenzar en [0, 0] y terminar en [x, 0]"
    
    """
    Para establecer los puntos desde donde extraer datos.
    """
    def pointers(self, start, end):
        assert start <= end, "start {} tiene que ser anterior o igual a end {}".format(start, end)

        if end > self.end_x:
            self._end_pointer = end
        if start < 0: start = 0
        if end < 0: end = 0

        self._start_pointer = start
        self._end_pointer = end
        return self

    def reset_pointers(self):        
        self._start_pointer = 0
        self._end_pointer = self.end_x
        return self


    """
    Atributos y métodos públicos
    """
    @property
    def end_x(self):
        return self._shape[-1][0]

    """
    Retorna el area de un polígono
    """
    @property
    def area(self):
        shape = Shape._trim_shape(self._shape, self._start_pointer, self._end_pointer)
        n = len(shape) # n of corners
        area = 0.
        for i in range(n):
            j = (i + 1) % n
            area += shape[i][0] * shape[j][1]
            area -= shape[j][0] * shape[i][1]
        area = abs(area) / 2.
        return area

    """
    Devuelve el porcentaje del shape que se encuentra entre el comienzo y final especificados
    con respecto al shape original
    """
    @property
    def area_percentage(self):
        percent = (self.area * 100.) / self.total_area
        if percent > 100.:
            percent = 100.
        return (self.area * 100.) / self.total_area

    @property
    def total_area(self):
        start_saved = self._start_pointer
        end_saved = self._end_pointer
        self._start_pointer = self._shape[0][0]
        self._end_pointer = self._shape[-1][0]

        total = self.area
        
        self._start_pointer = start_saved
        self._end_pointer = end_saved

        return total

    def value_inside_pointers(self, value):
        return value * (self.area_percentage / 100.)
    
    def value_total(self, proportional_value):
        return proportional_value / (self.area_percentage / 100.)

    def value_outside_pointers(self, value):
        rest_percent = 100. - self.area_percentage
        return value * (rest_percent / 100.)

    def value_above_end_pointer(self, value):
        total = self.area
        portion = Shape._get_area(Shape._trim_shape(self._shape, self._end_pointer, self.end_x))
        percent = (portion * 100.) / total
        return value * (percent / 100.)

#     def shape_end_minute_for_percentage_effect(self, percentage):
#         shape = Shape._detail_shape(self._shape, 5)
#         end_x = 0
#         for n in range(0, shape[-1][0], 5):
#             if Shape.get_area_percentage(shape, 0, n) >= percentage:
#                 end_x = n
#                 break
#         return end_x


    def scale_shape(self, scale):
        self._shape = [[pair[0] * scale, pair[1]] for pair in self._shape]
    
    def retard_shape(self, x_offset):
        if x_offset != 0:
            self._shape = [[pair[0] + x_offset, pair[1]] for pair in self._shape]
    
    @property
    def shape(self):
        return self._shape
    
    @staticmethod
    def sum_shapes_y(shape1, shape2, detail = 10):
        max_x = shape2[-1][0]
        if shape1[-1][0] > max_x:
            max_x = shape1[-1][0]
        max_x = int(round(max_x))
        
        min_x = shape2[0][0]
        if shape1[0][0] < min_x:
            min_x = shape1[0][0]
        min_x = int(round(min_x))
         
        def get_y_point(shape, x):
            for pair in shape:
                if pair[0] == x:
                    return pair[1]
            return 0.
        shape1 = [pair for pair in Shape._detail_shape(shape1, detail) if pair[0] % detail == 0]
        shape2 = [pair for pair in Shape._detail_shape(shape2, detail) if pair[0] % detail == 0]
        
        if shape1[-1][1] > 0.:
            shape1.append([shape1[-1][0] + 10, 0.])
        if shape2[-1][1] > 0.:
            shape2.append([shape2[-1][0] + 10, 0.])

        shape_result = []
        for mins in range(min_x, max_x, detail):
            shape_result.append([mins, get_y_point(shape1, mins) + get_y_point(shape2, mins)])
        
        if shape_result[-1][1] > 0.:
            shape_result.append([shape_result[-1][0] + 10, 0.])

        return shape_result


    """
    detalla el shape original añadiendo puntos cada minutos especificados
    """
    @staticmethod
    def _detail_shape(shape, detail_minutes):
        Shape._check_shape(shape)
        
        result = []
        def add_point(p):
            if p not in result:
                result.append(p)

        last_x, last_y = shape[0][0], shape[0][1]
        add_point([shape[0][0], shape[0][1]])
        for x, y in shape:
            if x == last_x and y == last_y: continue
            
            slope = None
            if x - last_x == 0:
                slope = 0.0
            else:
                slope = (y - last_y) / float((x - last_x))
            d = int(detail_minutes)
            s = ((int(last_x) / d) * d) + d
            r = range(s, int(x), d)
            for hour in r:
                new_y = ((hour - last_x) * slope) + last_y
                if new_y < 0:
                    new_y = 0
                elif new_y > 100:
                    new_y = 100
                add_point([hour, new_y])
            add_point([x, y])
            last_x = x
            last_y = y
        result = [[round(float(pair[0]) / detail_minutes) * detail_minutes, pair[1]] for pair in result]
        return result

    """
    De todo el shape, la función devuelve sólo la parte que se quiere,
    especificando el start_x y end_x
    """
    @staticmethod
    def _trim_shape(shape, start_x, end_x):
        Shape._check_shape(shape)
        last_x, last_y, result = None, None, []
        global last_point_added
        last_point_added = None
        def add_point(p):
            if p not in result:
                global last_point_added
                last_point_added = p
                result.append(p)
        add_point([shape[-1][0], shape[-1][1]])
        for x, y in shape:
            if last_y == None and last_x == None or\
                x < start_x:
                last_x = x
                last_y = y
                continue
            incr_x = float((x - last_x))
            slope = 0.
            if incr_x != 0:
                slope = (y - last_y) / incr_x
            if start_x >= last_x and start_x <= x:
                diff_x = abs(x - start_x)
                y_point = y - (slope * (diff_x))
                add_point([start_x, 0])
                add_point([start_x, y_point])
            if end_x >= last_x and end_x <= x:
                diff_x = abs(end_x - last_x)
                y_point = last_y + (slope * (diff_x))
                if last_x >= last_point_added[0]:
                    add_point([last_x, last_y])
                add_point([end_x, y_point])
                if y_point != 0:
                    add_point([end_x, 0])
                break
            add_point([x, y])
            last_x = x
            last_y = y
        return result



import sys

def main():
    """
    Shape de insulina lenta, 24h de acción
    """
    I = [
        [    0,   0], [   10,   7], [   20,  13], [   30,  20],
        [   40,  27], [   50,  33], [   60,  40], [   70,  47],
        [   80,  53], [   90,  60], [  100,  67], [  110,  73],
        [  120,  80], [  130,  82], [  140,  83], [  150,  85],
        [  160,  87], [  170,  88], [  180,  90], [  190,  91],
        [  200,  92], [  210,  93], [  230,  94], [  240,  95],
        [  250,  96], [  260,  97], [  270,  98], [  290,  99],
        [  300, 100], [ 1390,  83], [ 1400,  67], [ 1410,  50],
        [ 1420,  33], [ 1430,  17], [ 1440,   0],
    ]
    """
    Pinchazo 7:00 y 19:00 de 31 unidades.
    Cuanto llega durante el día y cuánto durante la noche
    """
    shape = Shape(I)
    dia = 0
    noche = 0

    dia += shape.pointers(720, 1440).value_inside_pointers(31) # del dia anterior
    dia += shape.pointers(0, 720).value_inside_pointers(31) # del día actual
    
    noche += shape.pointers(720, 1440).value_inside_pointers(31) # de la mañana
    noche += shape.pointers(0, 720).value_inside_pointers(31) # de la noche
    
    print "Pinchando 31 unidades a las 7:00 y a las 19:00, el valor de insulina que llega es dia {} y noche {}".format(dia, noche)
    
    
    """
    Pinchazo 7:00 y 19:00 de 20 y 42
    Cuanto llega durante el día y cuánto durante la noche
    """
    dia = 0
    noche = 0

    dia += shape.pointers(720, 1440).value_inside_pointers(42) # del dia anterior
    dia += shape.pointers(0, 720).value_inside_pointers(20) # del día actual
    
    noche += shape.pointers(720, 1440).value_inside_pointers(20) # de la mañana
    noche += shape.pointers(0, 720).value_inside_pointers(42) # de la noche
    
    
    print "Pinchando 20 unidades a las 7:00 y 42 a las 19:00, el valor de insulina que llega es dia {} y noche {}".format(dia, noche)
    
    """
    Salida:
    
    Pinchando 31 unidades a las 7:00 y a las 19:00, el valor de insulina que llega es dia 31.0 y noche 31.0
    Pinchando 20 unidades a las 7:00 y 42 a las 19:00, el valor de insulina que llega es dia 30.9331096254 y noche 31.0668903746
    
    ¿Es igual pincharse 31 y 31 que 20 y 42?
    """
    
    sys.exit()

if __name__ == '__main__':
    main()

