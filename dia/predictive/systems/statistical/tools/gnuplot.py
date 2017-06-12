# -*- coding: utf-8 -*-
import subprocess


class GnuPlot(object):
    """
    Uso:

    commands = ["set xrange [0:10]", "set yrange [-2:2]"]
    data = ["0 0", "30 5", "60 9"] # x y, x y, x y
    g = GnuPlot(commands, data)
    g.show()
    """

    proc = None
    commands = None
    data = None
    
    def __init__(self, command_list, data):
        self.commands = command_list
        self.data = data

    def show(self):
        self.proc = subprocess.Popen(
            ['gnuplot','-p'], 
            shell=True,
            stdin=subprocess.PIPE,
        )

        if self.commands != None:
            for command in self.commands:
                self.proc.stdin.write(command + "\n") # '; \n'

        if self.data:
            self.proc.stdin.write("plot '-' using 1:2 with linespoints\n")
            for data in self.data:
                self.proc.stdin.write(data + "\n")
            self.proc.stdin.write('e\n')

        self.proc.stdin.write('pause 3000\n')

    def close(self):
        if self.proc != None:
            self.proc.stdin.write('quit\n')
        
