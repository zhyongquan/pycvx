import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


class function:
    name = ""
    description = ""
    line_start = 0
    line_end = 0

    def __init__(self, name):
        self.name = name

    def tojason(self):
        return ""

    def show(self):
        return

    def __str__(self):
        str = "name={0}, description={1}".format(self.name, self.description) \
              + "\nline_start={0}, line_end={1}".format(self.line_start, self.line_end)
        return str


class cvxobject(function):
    type = ""
    unit = ""
    value = []

    def getlabel(self, axis, name, unit):
        if len(name) > 0 and len(unit) > 0:
            return "{0}({1})".format(name, unit)
        elif len(name) > 0:
            return name
        elif len(unit) > 0:
            return "{0}({1})".format(axis, unit)
        else:
            return axis

    def __str__(self):
        str = super().__str__() \
              + "\ntype={0}, unit={1}".format(self.type, self.unit) \
              + "\nvalue\n" + self.value.__str__()
        return str


class axis(cvxobject):

    def show(self):
        x = range(0, len(self.value) - 1, 1)
        plt.plot(x, self.value, marker='o')
        plt.title(name)
        plt.xlabel(self.getlabel("x", "", ""))
        plt.ylabel(self.getlabel("y", self.name, self.unit))
        # for i in range(0, len(self.value) - 1):
        #     plt.text(i, self.value[i], "{0},{1}".format(i, self.value[i]))
        plt.show()


class calibration(cvxobject):
    x = axis("")
    y = axis("")

    def show(self):
        if self.type == "CURVE" or self.type == "MAP" or self.type == "VAL_BLK":
            if self.type == "CURVE":
                plt.plot(self.x.value, self.value, marker='o')
                plt.title(self.name)
                plt.xlabel(self.getlabel("x", self.x.name, self.x.unit))
                plt.ylabel(self.getlabel("y", self.name, self.unit))
                # for i in range(0, len(self.value) - 1):
                #     plt.text(self.x.value[i], self.value[i], "{0},{1}".format(self.x.value[i], self.value[i]))
                plt.show()
            elif self.type == "MAP":
                X, Y = np.meshgrid(self.x.value, self.y.value)
                nx = len(self.x.value)
                ny = len(self.y.value)
                Z = np.zeros((ny, nx))
                for i in range(0, ny - 1):
                    for j in range(0, nx - 1):
                        Z[i, j] = self.value[i][j]
                fig1 = plt.figure()
                ax = Axes3D(fig1)
                ax.plot_surface(X, Y, Z)
                ax.set_title(self.name)
                ax.set_xlabel(self.getlabel("x", self.x.name, self.x.unit))
                ax.set_ylabel(self.getlabel("y", self.y.name, self.y.unit))
                ax.set_zlabel(self.getlabel("z", self.name, self.unit))
                plt.show()
            elif self.type == "VAL_BLK":
                x = range(0, len(self.value) - 1, 1)
                plt.title(self.name)
                plt.plot(x, self.value, marker='o')
                plt.xlabel(self.getlabel("x", "", ""))
                plt.ylabel(self.getlabel("y", self.name, self.unit))
                # for i in range(0, len(self.value) - 1):
                #     plt.text(i, self.value[i], "{0},{1}".format(i, self.value[i]))
                plt.show()

    def __str__(self):
        str = super().__str__()
        if len(self.x.value) > 0:
            str = str + "\nx\n" + self.x.__str__()
        if len(self.y.value) > 0:
            str = str + "\ny\n" + self.y.__str__()
        return str


class cvxinfo:
    file_content = "CALIBRATION VALUES V2.1"
    field_separator = ','
    decimal_point = '.'
    comment_indicator = '*'
    string_delimiter = '"'
    functions = {}
    calibrations = {}
    axises = {}
    line_count = 0

    def __init__(self):
        return

    def addfunction(self, fun):
        if not fun.name in self.functions.keys():
            self.functions[fun.name] = fun

    def addcalibration(self, cal):
        if not cal.name in self.calibrations.keys():
            self.calibrations[cal.name] = cal

    def addaxis(self, ax):
        if not ax.name in self.axises.keys():
            self.axises[ax.name] = ax
            # for cal in self.calibrations:
            #     if cal.x.name == ax.name:
            #         cal.x = ax
            #     if cal.y.name == ax.name:
            #         cal.y = ax

    def read(self, cvxfile):
        line_count = 0
        with open(cvxfile, 'r') as file:
            # first line: Description Header
            line = file.readline()
            line_count = 1
            cal = calibration("")
            fun = function("")
            while True:
                line = file.readline()
                line_count = line_count + 1
                if not line:
                    break
                line = line.strip()
                if len(line) == 0:
                    if len(cal.value) > 0:
                        cal.line_end = line_count - 1
                        self.addcalibration(cal)
                        cal = calibration("")
                elif not line.startswith(self.comment_indicator):
                    txt = line.split(self.field_separator)
                    if txt[0] == "FUNCTION_HDR":
                        # jump FUNCTION_HDR
                        file.readline()
                        line_count = line_count + 1
                    elif txt[0] == "FUNCTION":
                        # function
                        fun = function(txt[2].strip(self.string_delimiter))
                        fun.description = txt[3].strip(self.string_delimiter)
                        fun.line_start = line_count
                        fun.line_end = line_count
                        self.addfunction(fun)
                    elif len(txt) == 2 and len(txt[0]) == 0 and len(txt[1]) > 0:
                        # calibration block
                        cal = calibration(txt[1])
                        cal.value = []
                        cal.line_start = line_count
                    elif txt[0] == "VALUE" or txt[0] == "CURVE" or txt[0] == "MAP" or txt[0] == "VAL_BLK":
                        cal.type = txt[0]
                        if txt[0] == "VALUE":
                            cal.unit = getunit(txt[1])
                            if isDigit(txt[2]):
                                cal.value = [float(txt[2])]
                            else:
                                cal.value = [txt[2]]
                        elif txt[0] == "CURVE":
                            if len(txt) > 1 and len(txt[1]) > 0:
                                ax = getaxis(txt[1], "AXIS_PTS", txt, line_count)
                                cal.x = ax
                        elif txt[0] == "MAP":
                            if len(txt) > 1 and len(txt[1]) > 0:
                                ax = axis(txt[1])
                                ax.type = "AXIS_PTS"
                                cal.x = ax
                        elif txt[0] == "VAL_BLK":
                            cal.unit = getunit(txt[1])
                            cal.value = getvalue(txt)
                    elif txt[0] == "X_AXIS_PTS":
                        self.calibrations[cal.name].x = getaxis("", "X_AXIS_PTS", txt, line_count)
                    elif txt[0] == "Y_AXIS_PTS":
                        self.calibrations[cal.name].y = getaxis("", "Y_AXIS_PTS", txt, line_count)
                    elif txt[0] == "AXIS_PTS":
                        ax = getaxis(cal.name, "AXIS_PTS", txt, line_count)
                        self.addaxis(ax)
                    else:
                        if cal.type == "CURVE":
                            cal.unit = getunit(txt[0])
                            cal.value = getvalue(txt)
                        if cal.type == "MAP":
                            if len(cal.value) == 0 and len(cal.x.value) == 0:
                                cal.unit = getunit(txt[0])
                            if len(cal.x.name) > 0 and len(cal.x.value) == 0:
                                cal.x.value = getvalue(txt)
                                if len(txt[1]) > 0:
                                    ax = axis(txt[1])
                                    ax.type = "AXIS_PTS"
                                    cal.y = ax
                            else:
                                if len(cal.y.name) > 0:
                                    cal.y.value.append(float(txt[1]))
                                cal.value.append(getvalue(txt))

            print("find functions:{0}, calibrations:{1}, axises:{2}".format(len(self.functions), len(self.calibrations),
                                                                            len(self.axises)))
            self.line_count = line_count


def isDigit(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def getvalue(txt):
    if isDigit(txt[2]):
        # number
        value = [0] * (len(txt) - 2)
        for i in range(2, len(txt), 1):
            value[i - 2] = float(txt[i])
        return value
    else:
        # ascii
        return txt[2:len(txt) - 1]


def getunit(str):
    unit = ""
    if len(str) > 0:
        unit = str[2:len(str) - 2]
    return unit


def getaxis(name, type, txt, line_count):
    ax = axis(name)
    ax.type = type
    if len(txt[1]) > 0:
        ax.unit = getunit(txt[1])
    ax.value = getvalue(txt)
    ax.line_start = line_count - 1
    ax.line_end = line_count
    return ax
