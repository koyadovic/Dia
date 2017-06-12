# -*- coding: utf-8 -*-
"""
Para visualización o modificación de los shapes
mejor usar Spyder y el fichero digestion_shapes

Actualizados aquí a fecha 30/01/2017 21:10
"""
from ...analysis.tools.graphs import Graph
from ...tools.dates import Datetime
from ...tools.shapes import Shape

from dia.models import Feeding


"""
Para dibujar gráficas
"""
import numpy as np
from matplotlib.patches import Rectangle

class ReshapeFeedingGraph(Graph):
    def __init__(self, parent):
        assert isinstance(parent, ShapeFeeding)

        self.parent = parent
        options = {
            "name": 'reshape_feeding',
            "figsize": (8, 9),
            "dpi": 70,
            "cols": 1,
        }
        super(ReshapeFeedingGraph, self).__init__(**options)
        
        self.add_drawing_routine(self.drawing_routine('carb'))
        self.add_drawing_routine(self.drawing_routine('protein'))
        self.add_drawing_routine(self.drawing_routine('fat'))
        
    def drawing_routine(self, what=""): # carb, protein, fat
        assert what in ["carb", "protein", "fat"]
        
        def draw_routine(ax):
            """
            Original:
            self.x_minutes_carb_orig, self.y_effect_carb_orig
            self.x_minutes_protein_orig, self.y_effect_protein_orig
            self.x_minutes_fat_orig, self.y_effect_fat_orig

            Modificado el shape
            self.x_minutes_carb_new, self.y_effect_carb_new
            self.x_minutes_protein_new, self.y_effect_protein_new
            self.x_minutes_fat_new, self.y_effect_fat_new
            """    
            """
            Dibujamos el gráfico
            """
            if what == "carb":
                ax.set_title('Carbohidratos {}g en {}'.format(self.parent._feeding.carb_gr, self.parent._feeding.datetime))
            elif what == "protein":
                ax.set_title('Proteinas {}g en {}'.format(self.parent._feeding.protein_gr, self.parent._feeding.datetime))
            elif what == "fat":
                ax.set_title('Grasas {}g en {}'.format(self.parent._feeding.fat_gr, self.parent._feeding.datetime))
                
            ax.set_xlabel(u"Minutos desde ingesta")
            ax.set_ylabel(u"% velocidad digestión")
    
            ax.set_xlim(0, self.parent.x_minutes_fat_new[-1])
            ax.set_ylim(0, 100)
            
            ax.set_xticks(np.arange(0, self.parent.x_minutes_fat_new[-1], 30.))
            ax.set_yticks(np.arange(0, 100., 20.))
    
            if what == "carb":
                ax.fill_between(self.parent.x_minutes_carb_orig, self.parent.y_effect_carb_orig, color='green', alpha=0.1)
                ax.fill_between(self.parent.x_minutes_carb_new, self.parent.y_effect_carb_new, color='red', alpha=0.2)
                ax.plot(self.parent.x_minutes_carb_new, self.parent.y_effect_carb_new, color='black')
            elif what == "protein":
                ax.fill_between(self.parent.x_minutes_protein_orig, self.parent.y_effect_protein_orig, color='green', alpha=0.1)
                ax.fill_between(self.parent.x_minutes_protein_new, self.parent.y_effect_protein_new, color='red', alpha=0.2)
                ax.plot(self.parent.x_minutes_protein_new, self.parent.y_effect_protein_new, color='black')
            elif what == "fat":
                ax.fill_between(self.parent.x_minutes_fat_orig, self.parent.y_effect_fat_orig, color='green', alpha=0.1)
                ax.fill_between(self.parent.x_minutes_fat_new, self.parent.y_effect_fat_new, color='red', alpha=0.2)
                ax.plot(self.parent.x_minutes_fat_new, self.parent.y_effect_fat_new, color='black')

            legend_handles = []
            if '_factor_retard_shown' not in self.__dict__ or not self._factor_retard_shown: 
                legend_retard = Rectangle(
                    (0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0,
                    label=u'+{}m, pending proteins {}, fats {}'.\
                    format(
                        int(round(self.parent.minutes_retard)),
                        round(self.parent.pending_protein_gr),
                        round(self.parent.pending_fat_gr)
                    )
                )
                legend_digestion_factor = Rectangle(
                    (0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0,
                    label=u'dig. factor {}, copious {}, protein {}, fat {}'.\
                    format(
                        round(self.parent.digestion_factor, 3),
                        round(self.parent.copious_factor, 3),
                        round(self.parent.protein_factor, 3),
                        round(self.parent.fat_factor, 3)
                    )
                )
                legend_handles += [legend_retard,
                    legend_digestion_factor]
                self._factor_retard_shown = True
            
            if len(legend_handles) > 0:
                ax.legend(loc='upper right', handles=legend_handles)
    
            ax.grid()
        
        return lambda ax: draw_routine(ax)



class ShapeFeeding(object):
    def __init__(self, feeding):
        assert isinstance(feeding, Feeding), "feeding ha de ser instancia de Feeding"
        self._feeding = feeding

        """
        Es líquido o sólido?
        """    
        digestion_factor = 1.0 # solid
        if self._feeding.is_liquid:
            digestion_factor = 0.4 # liquid
            
        self._carbohydrate = Carbohydrate(self._feeding.carb_gr)
        self._protein = Protein(self._feeding.protein_gr)
        self._fat = Fat(self._feeding.fat_gr)

        self.carbohydrate.reset_pointers()
        self.protein.reset_pointers()
        self.fat.reset_pointers()
        
        self.carbohydrate.scale_shape(digestion_factor)
        self.protein.scale_shape(digestion_factor)
        self.fat.scale_shape(digestion_factor)
        
        self.graph = ReshapeFeedingGraph(self)
    
    def set_start_dt_end_dt_(self, start_dt, end_dt):
        assert isinstance(start_dt, Datetime) and isinstance(end_dt, Datetime), "start_dt y end_dt tienen que ser instancias de Datetime"
        assert (end_dt - start_dt).total_secs >= 0, "end_dt {} tiene que ser más grande o igual que start_dt {}".format(end_dt, start_dt)
        
        """
        Establecemos el rango de datetimes donde queremos
        extraer del current alimento, lo que aporta allá
        
        Todo esto habrá que probarlo.
        """
        start = int(round((start_dt - self._feeding.datetime).total_seconds() / 60.))
        end = start + int(round((end_dt - start_dt).total_seconds() / 60.))
        
        self.carbohydrate.pointers(start, end)
        self.protein.pointers(start, end)
        self.fat.pointers(start, end)
        return self

    def reset_start_dt_end_dt(self):
        self.carbohydrate.reset_pointers()
        self.protein.reset_pointers()
        self.fat.reset_pointers()
        return self
    
    def digested_between_start_dt_end_dt(self):
        ch = self.carbohydrate.digested
        pr = self.protein.digested
        fa = self.fat.digested
        
        factor = (ch + pr + fa) / (self.carbohydrate.gr + self.protein.gr + self.fat.gr)

        gr = self.total_gr * factor
        fiber = self.fiber_gr * factor
        alcohol = self.alcohol_gr * factor
        
        return gr, ch, pr, fa, fiber, alcohol
    
    @property
    def total_gr(self):
        return self._feeding.total_gr

    @property
    def total_ml(self):
        return self._feeding.total_ml

    @property
    def fiber_gr(self):
        return self._feeding.fiber_gr

    @property
    def alcohol_gr(self):
        return self._feeding.alcohol_gr
    
    @property
    def carbohydrate(self):
        return self._carbohydrate

    @property
    def protein(self):
        return self._protein

    @property
    def fat(self):
        return self._fat
    
    
    def scale_digestion_time(self, pending_total_gr=0., pending_carb_gr=0., pending_protein_gr=0., pending_fat_gr=0.):
        assert pending_total_gr >= 0
        assert pending_carb_gr >= 0
        assert pending_protein_gr >= 0
        assert pending_fat_gr >= 0
        
        """
        Lo pending en proteinas y grasas, atrasa la digestión del feeding actual
        máximo 45 minutos
        
        La composición del feeding actual, alarga o acorta su digestión
        """
        self.pending_protein_gr=pending_protein_gr
        self.pending_fat_gr=pending_fat_gr

        
        """
        Para dibujar la gráfica
        """
        self.x_minutes_carb_orig = np.hsplit(np.array(self.carbohydrate.shape), 2)[0].T[0]
        self.y_effect_carb_orig = np.hsplit(np.array(self.carbohydrate.shape), 2)[1].T[0]
        self.x_minutes_protein_orig = np.hsplit(np.array(self.protein.shape), 2)[0].T[0]
        self.y_effect_protein_orig = np.hsplit(np.array(self.protein.shape), 2)[1].T[0]
        self.x_minutes_fat_orig = np.hsplit(np.array(self.fat.shape), 2)[0].T[0]
        self.y_effect_fat_orig = np.hsplit(np.array(self.fat.shape), 2)[1].T[0]

        """
        Retardos por lo que pueda quedar pendiente por digerir en el estómago
        """
        self.retard_protein = self.pending_protein_gr * 0.3333333333333333333
        self.retard_fats = 0.
        if self.pending_fat_gr > 0.:
            self.retard_fats = (self.pending_fat_gr * 0.3) + 6.
        self.minutes_retard = self.retard_fats + self.retard_protein
        
        if self._feeding.is_liquid:
            self.minutes_retard *= 0.4

        self.carbohydrate.retard_shape(self.minutes_retard)
        self.protein.retard_shape(self.minutes_retard)
        self.fat.retard_shape(self.minutes_retard)
        
        """
        Estiramientos por la composición del alimento actual
        """
        self.copious_factor = (self._feeding.total_gr * 0.00055) + 0.83 # 300 = 1.0, 700 = 1.22
        self.protein_factor = (self._feeding.protein_gr * 0.003142857142857143) + 0.8742857142857143 # 40 = 1.0, 110 = 1.22
        self.fat_factor = (self._feeding.fat_gr *0.0036666666666666666) + 0.89 # 30 = 1.0, 90 = 1.22
        
        """
        Por no pasarnos ...
        """
        if self.copious_factor < 1.0: self.copious_factor = 1.0
        if self.protein_factor < 1.0: self.protein_factor = 1.0
        if self.fat_factor < 1.0: self.fat_factor = 1.0
        if self.copious_factor > 1.22: self.copious_factor = 1.22
        if self.protein_factor > 1.22: self.protein_factor = 1.22
        if self.fat_factor > 1.22: self.fat_factor = 1.22
        
        """
        Calculamos la digestion estimada
        """
        self.normal_digestion = 3 # in hours
        self.total_digestion_estimated_hours = self.normal_digestion * self.copious_factor * self.protein_factor * self.fat_factor

        self.digestion_factor = self.total_digestion_estimated_hours / self.normal_digestion
        
        self.carbohydrate.scale_shape(self.digestion_factor)
        self.protein.scale_shape(self.digestion_factor)
        self.fat.scale_shape(self.digestion_factor)
        
        """
        Para dibujar la gráfica
        """
        self.x_minutes_carb_new = np.hsplit(np.array(self.carbohydrate.shape), 2)[0].T[0]
        self.y_effect_carb_new = np.hsplit(np.array(self.carbohydrate.shape), 2)[1].T[0]
        self.x_minutes_protein_new = np.hsplit(np.array(self.protein.shape), 2)[0].T[0]
        self.y_effect_protein_new = np.hsplit(np.array(self.protein.shape), 2)[1].T[0]
        self.x_minutes_fat_new = np.hsplit(np.array(self.fat.shape), 2)[0].T[0]
        self.y_effect_fat_new = np.hsplit(np.array(self.fat.shape), 2)[1].T[0]
    
    @property
    def datetime(self):
        return self._feeding.datetime
    
    @property
    def is_solid(self):
        return self._feeding.is_solid

    @property
    def is_liquid(self):
        return self._feeding.is_liquid

    def relative_positioned_shapes(self, datetime_minute_0):
        assert isinstance(datetime_minute_0, Datetime)
        """
        Offset con respecto al datetime_minute_0 especificado. Anteriores Feedings comenzarán
        en x's negativos
        """
        minutes_offset = int(round((self._feeding.datetime - datetime_minute_0).total_seconds() / 60))

        """
        Extraemos el total y's y total gr de los tres shapes
        """
        total_carbs_gr = self._feeding.carb_gr
        total_carbs_y = sum([float(pair[1]) for pair in self.carbohydrate])
        total_protein_gr = self._feeding.protein_gr
        total_protein_y = sum([float(pair[1]) for pair in self.protein])
        total_fat_gr = self._feeding.fat_gr
        total_fat_y = sum([float(pair[1]) for pair in self.fat])
        
        """
        Creamos tres shapes adicionales, modificando el offset de las x's
        y también traduciendo en cada pair, las y's con los gr de macronutriente
        que será digerido.
        """
        carbohydrate_shape = [[pair[0] + minutes_offset, (pair[1] / float(total_carbs_y)) * total_carbs_gr] for pair in self.carbohydrate]
        protein_shape = [[pair[0] + minutes_offset, (pair[1] / float(total_protein_y)) * total_protein_gr] for pair in self.protein]
        fat_shape = [[pair[0] + minutes_offset, (pair[1] / float(total_fat_y)) * total_fat_gr] for pair in self.fat]
        
        return carbohydrate_shape, protein_shape, fat_shape


class Carbohydrate(Shape):
    """
    Es necesario el cálculo de k, la constante de la relación de
    proporcionalidad inversa que mantienen la pendiente m del ratio
    carbohidrato y dosis y el factor de corrección.

    k = m * cf
    
    Cuando la sensibilidad a la insulina aumente, cf aumentará, m disminuirá, k debería mantenerse constante
    Cuando la sensibilidad a la insulina disminuya, cf disminuirá, m aumentará, k debería mantenerse constante
    """
    SHAPE = [
        [   0,   0], [  10,  28], [  20,  51], [  30,  70], [  40,  84],
        [  50,  94], [  60,  99], [  70, 100], [  80,  98], [  90,  92],
        [ 100,  84], [ 110,  74], [ 120,  60], [ 130,  46], [ 140,  32],
        [ 150,  20], [ 160,  10], [ 170,   3], [ 180,   0],
    ]
    
    def __init__(self, gr):
        assert gr >= 0, "gr debe ser mayor o igual que 0"

        self.gr = gr
        super(Carbohydrate, self).__init__(Carbohydrate.SHAPE)

    """
    Deviation
    """
    def deviation(self, k=None):
        assert k, "k tiene que estar calculado para ofrecer desvío por hidratos"
        return self.digested * k

    def deviation_pending(self, k=None):
        assert k, "k tiene que estar calculado para ofrecer desvío por hidratos"
        return self.digestion_pending * k
    
    """
    Pendiente de digestion
    """
    @property
    def digested(self):
        return self.value_inside_pointers(self.gr)

    @property
    def digestion_pending(self):
        return self.gr - self.digested
    

class Protein(Shape):
    """
    Nos basamos en un estudio que se encontró en el que acabaron determinando
    que por cada 40 gr de proteina ingerida, a los 180 minutos se produce
    un desvío ascendente en los niveles de glucosa de +43mg/dL
    """
    SHAPE = [
        [   0,   0], [  10,  15], [  20,  29], [  30,  42], [  40,  54],
        [  50,  64], [  60,  74], [  70,  82], [  80,  88], [  90,  93],
        [ 100,  97], [ 110,  99], [ 120, 100], [ 130,  99], [ 140,  98],
        [ 150,  94], [ 160,  90], [ 170,  84], [ 180,  78], [ 190,  69],
        [ 200,  60], [ 210,  50], [ 220,  38], [ 230,  26], [ 240,  14],
        [ 250,   0],
    ]
    
    def __init__(self, gr, shape=None):
        assert gr >= 0, "gr debe ser mayor o igual que 0"

        self.gr = gr
        super(Protein, self).__init__(Protein.SHAPE)


    @property
    def deviation(self):
        base_proteins = Shape(Protein.SHAPE).\
            pointers(0, 180).\
            value_inside_pointers(40)

        deviation_per_gram = 43. / base_proteins
        deviation = self.digested * deviation_per_gram
        return deviation
    
    @property
    def deviation_pending(self):
        base_proteins = Shape(Protein.SHAPE).\
            pointers(0, 180).\
            value_inside_pointers(40)
            
        deviation_per_gram = 43. / base_proteins
        deviation = self.digestion_pending * deviation_per_gram
        return deviation

    @property
    def digested(self):
        return self.value_inside_pointers(self.gr)

    @property
    def digestion_pending(self):
        return self.gr - self.digested

    
class Fat(Shape):
    """
    Nos basamos en un estudio que se encontró en el que acabaron determinando
    que por cada 35 gr de grasa ingerida, a los 210 minutos se produce
    un desvío ascendente en los niveles de glucosa de +32mg/dL
    """
    SHAPE = [
        [   0,   0], [  10,   9], [  20,  18], [  30,  27], [  40,  35],
        [  50,  43], [  60,  50], [  70,  57], [  80,  63], [  90,  69],
        [ 100,  74], [ 110,  79], [ 120,  84], [ 130,  87], [ 140,  91],
        [ 150,  94], [ 160,  96], [ 170,  98], [ 180,  99], [ 190, 100],
        [ 200, 100], [ 210, 100], [ 220,  99], [ 230,  98], [ 240,  96],
        [ 250,  93], [ 260,  90], [ 270,  86], [ 280,  81], [ 290,  76],
        [ 300,  70], [ 310,  63], [ 320,  56], [ 330,  49], [ 340,  40],
        [ 350,  31], [ 360,  21], [ 370,  11], [ 380,   0],
    ]
    
    def __init__(self, gr, shape=None):
        assert gr >= 0, "gr debe ser mayor o igual que 0"

        self.gr = gr
        super(Fat, self).__init__(Fat.SHAPE)

        
    @property
    def deviation(self):
        base_fats = Shape(Fat.SHAPE).\
            pointers(0, 210).\
            value_inside_pointers(35)
            
        deviation_per_gram = 32. / base_fats
        deviation = self.digested * deviation_per_gram
        return deviation

    @property
    def deviation_pending(self):
        base_fats = Shape(Fat.SHAPE).\
            pointers(0, 210).\
            value_inside_pointers(35)

        deviation_per_gram = 32. / base_fats
        deviation = self.digestion_pending * deviation_per_gram
        return deviation

    @property
    def digested(self):
        return self.value_inside_pointers(self.gr)

    @property
    def digestion_pending(self):
        return self.gr - self.digested
    
    






