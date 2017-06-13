# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from PIL import Image
import io
import inspect


class Graph(object):
    _index = 0
    
    def __init__(self, **kvargs):
        Graph._index += 1
        options = {
            "name": '',
            "figsize": (8, 6),
            "dpi": 70,
            "cols": 1,
        }
        options.update(kvargs)

        self.index = Graph._index
        self.name = options['name']
        self.figsize = options['figsize']
        self.dpi = options['dpi']
        self._drawing_routines = []
        self.cols = options['cols']
       
    def _draw_figure(self):
        self.rows = len(self._drawing_routines) / self.cols
        if len(self._drawing_routines) % self.cols != 0:
            self.rows += 1

        fig = plt.figure(self.index,
                figsize=self.figsize,
                dpi=self.dpi)
        
        for n, routine in enumerate(self._drawing_routines):
            ax = fig.add_subplot(self.rows, self.cols, n + 1)
            routine(ax)

        fig.tight_layout()
        return fig

    def add_drawing_routine(self, routine):
        assert len(inspect.getargspec(routine)[0]) == 1, u"las rutinas deben aceptar un parametro con el axes donde dibujar"
        self._drawing_routines.append(routine)

    def bufferedpng(self):
        """
        Lo dibujamos
        """
        figure = self._draw_figure()
        buf = io.BytesIO()
        figure.savefig(buf, format='png', dpi=figure.dpi)
        buf.seek(0)
        return buf
    
    def pil_image(self):
        buf = self.bufferedpng()
        return Image.open(buf)
        
    def show(self):
        self.pil_image().show()
    
    def plt_show(self):
        plt.close('all')
        self._draw_figure()
        plt.show()
        
