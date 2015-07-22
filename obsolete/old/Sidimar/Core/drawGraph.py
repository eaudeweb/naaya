from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO


YAXIS_X = 20
YAXIS_Y_START = 89
YAXIS_Y_LENGTH = 202

XAXIS_X_START = 20
XAXIS_X_LENGTH = 204
XAXIS_Y = 75

TEXT_Y_XDELAY = 21
TEXT_Y_YDELAY = 15

TEXT_X_XDELAY = 10
TEXT_X_YDELAY = 13

FILL = ["#404040", "#FF00FF", "#0000FF", "#FF0000", "#009900"]
MARK_LEN = 2
POINT_SIZE = 1

class drawGraph:
    """ draw a diagram """

    def __init__(self, img_path, font_path):
        self.img = self._load_image(img_path)
        self.draw = self._load_draw(self.img)
        self.font = self._load_font(font_path)
        self.x_axis = []
        self.y_axis = []

    def del_draw(self):
        del self.draw

    def _load_image(self, path):
        """ load an image """
        return Image.open(path)

    def _load_draw(self, img):
        """ load draw """
        return ImageDraw.Draw(img)

    def _load_font(self, path):
        """ load the font """
        return ImageFont.load(path)

    def _horizontal_marker(self, x, y, color):
        """ draw a horizontal marker """
        begin = x - MARK_LEN
        end = x + MARK_LEN
        self.draw.line([begin, y, end, y], color)

    def _vertical_marker(self, x, y, color):
        """ draw a vertical marker """
        begin = y - MARK_LEN
        end = y + MARK_LEN
        self.draw.line([x, begin, x, end], color)

    def _draw_y_text(self, x, y, content, color):
        """draw text"""
        self.draw.text([x-TEXT_Y_XDELAY, y-TEXT_Y_YDELAY], content, color, self.font)

    def _draw_x_text(self, x, y, content, color):
        """draw text"""
        text_size = self.draw.textsize(content)[0]
        if x-TEXT_X_XDELAY < XAXIS_X_START:
            self.draw.text([x+1, y-TEXT_X_YDELAY], content, color, self.font)
        elif x+text_size > (XAXIS_X_START + XAXIS_X_LENGTH):
            self.draw.text([x-text_size, y-TEXT_X_YDELAY], content, color, self.font)
        else:
            self.draw.text([x-TEXT_X_XDELAY, y-TEXT_X_YDELAY], content, color, self.font)

    def __round_value(self, val):
        """ """
        first, second = str(val).split('.')
        return float("%s.%s" % (first, second[:2]))

    def _draw_y_ax(self, x, y, length, val, color):
        self.draw.line([(x, y), (x, y + length)], color)
        dist = length/float(len(val) - 1)
        dist = self.__round_value(dist)
        cont = 0
        i = 0
        while length>=cont:
            y_temp = y + cont-1
            if (i==0) or (i==(len(val)-1)) or (i==len(val)/2):
                self._horizontal_marker(x, y_temp, color) #scadem unu ca sa apara si end
                value = "%.1f" % (val[i])
                if value.startswith('-'):  value = value[1:]
                self._draw_y_text(x, y_temp, value, color)
            i += 1
            cont += dist
        self.y_axis.append(val)

    def _draw_x_ax(self, x, y, length, val, color):
        self.draw.line([(x, y), (x+length, y)], color)
        dist = length/float(len(val) - 1)
        cont = 0
        i = 0
        while length>=cont:
            x_temp = x + cont
            self._vertical_marker(x_temp, y, color)
            self._draw_x_text(x_temp, y, str(val[i]), color)
            i += 1
            cont += dist
        self.x_axis.append(val)

    def _draw_point(self, x, y, color):
        """ draw a rectangular """
        self.draw.rectangle([(x - POINT_SIZE, y - POINT_SIZE), (x + POINT_SIZE, y + POINT_SIZE)] , fill=color)

    def _draw_line(self, x1, y1, x2, y2, color):
        """ """
        self.draw.line([x1, y1, x2, y2], color)

    def drawYAxis(self, values=[]):
        """ draw the Y-axis """
        cont = i = 0
        for val in values:
            self._draw_y_ax(YAXIS_X-cont, YAXIS_Y_START, YAXIS_Y_LENGTH, val, FILL[i])
            i += 1
            cont += 15

    def drawXAxis(self, values=[]):
        """ draw the Y-axis """
        cont = i = 0
        for val in values:
            self._draw_x_ax(XAXIS_X_START, XAXIS_Y-cont, XAXIS_X_LENGTH, val, FILL[i])
            i += 1
            cont += 15

    def _draw_dia(self, px_len, pt_len, val, nr_ax, color):
        dist = YAXIS_Y_LENGTH/float(len(val) - 1)
        cont = 0
        points = []
        for v in val:
            x = px_len * (v - self.x_axis[nr_ax][0])/pt_len + XAXIS_X_START
            y = YAXIS_Y_START
            y_temp = y + cont-1
            self._draw_point(x, y_temp, color)
            points.append([x, y_temp])
            cont += dist
        x1, y1 = points[0]
        for point in points[1:]:
            self._draw_line(x1, y1, point[0], point[1], color)
            x1, y1 = point

    def drawDiagram(self, values):
        """ draw the diagram """
        i = 0
        for val in values:
            x_scale = self.x_axis[i][-1] - self.x_axis[i][0]
            self._draw_dia(XAXIS_X_LENGTH, x_scale, val, i, FILL[i])
            i += 1

    def getGraph(self):
        """ """
        return self.draw

    def getImage(self):
        """ """
        return self.img

    def saveImage(self, out, format):
        """ """
        self.img.save(out, format)
