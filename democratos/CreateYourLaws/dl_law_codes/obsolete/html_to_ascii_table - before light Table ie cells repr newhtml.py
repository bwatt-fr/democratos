# -*- coding: utf-8 -*-

""" contains classes to transform Html Table to ascii table
Printable with python print() """
try:
    from functions import get_something, remove_piece_of_text
except:
    from CreateYourLaws.dl_law_codes.functions import get_something
    from CreateYourLaws.dl_law_codes.functions import remove_piece_of_text

LIST_OF_CHANGE = [('<thead>\n', ''),
                  ('</thead>\n', ''),
                  ('<sup>', ''),
                  ('</sup>', ''),
                  ('<br clear="none"/>', ''),
                  (' align="left"', ''),
                  (' align="right"', ''),
                  (' align="center"', ''),
                  (' align="justify"', ''),
                  (' vAlign="top"', ''),
                  (' vAlign="middle"', ''),
                  (' vAlign="bottom"', ''),
                  ('<p>', ''),
                  ('<b>', ''),
                  ('</b>', ''),
                  ('<br/>', ''),
                  ('</p>', ''),
                  ('<p/>', ''),
                  (' colspan="1"', ''),
                  (' rowspan="1"', ''),
                  (' colspan=1', ''),
                  (' rowspan=1', ''),
                  ('&gt;', '>'),
                  ('&lt;', '<'),
                  ('colSpan="', 'colspan='),
                  ('rowSpan="', 'rowspan='),
                  ('colspan="', 'colspan='),
                  ('rowspan="', 'rowspan='),
                  ('colSpan=', 'colspan='),
                  ('rowSpan=', 'rowspan='),
                  ('<tbody>\n', ''),
                  ('</tbody>\n', ''),
                  ]

LIST_OF_DEL = [(' width=', '>', '/')
               ]


class Cell():
    """ cell of a table """

    def __init__(self, text, isth):
        self.isth = isth
        if text is None:
            self.text = ''
            self.colspan, self.rowspan = 1, 1
            self.contents = ''
            self.width, self.height = 1, 1
        else:
            self.text = text
            self.colspan, self.rowspan = self._get_span()
            self.contents = self._get_contents()
            self.width, self.height = self._get_width_and_height()
            self.contents = self.contents.replace('\n', '')
        self.itr = 0

    def __repr__(self):
        return self.contents

    def _get_span(self):
        """ check the colspan and rowspan"""
        col = 1
        row = 1
        buf = self.text[0:7]
        i = 7
        while i < len(self.text) and self.text[i] != '>':
            buf += self.text[i]
            if buf == 'colspan=':
                try:
                    col = int(self.text[i + 1:i + 3])
                    i += 2
                except:
                    col = int(self.text[i + 1])
                    i += 1
            elif buf == 'rowspan=':
                try:
                    row = int(self.text[i + 1:i + 3])
                    i += 2
                except:
                    row = int(self.text[i + 1])
                    i += 1
            buf = buf[1:8]
            i += 1
        return col, row

    def _get_contents(self):
        """ Get the content of the table's cell"""
        if self.isth:
            contents, i = get_something(self.text, '>', '</th>', 0)
        else:
            contents, i = get_something(self.text, '>', '</td>', 0)
        return contents

    def _get_width_and_height(self):
        """ return the height and width of cell from the html table"""
        buf = ""
        counter = 0
        width = 0
        height = 1
        for i in range(len(self.contents)):
            counter += 1
            buf = self.contents[i:i + 2]
            if buf == "\n":
                if counter > width:
                    width = counter
                height += 1
                counter = 0
                i += 1
        if counter > width:
            width = counter
        return width, height


class Table():
    # table in ascii
    def __init__(self, html):
        self.clean_html = self._prepare_html(html)
        self.cellslist = [Cell(None, False)]
        self.tab = self.get_dat_tab()
        self.widths, self.heights = self.get_the_sizes()
        self.representation = self.get_repr()
        self.html = self.make_dat_html()

    def __repr__(self):
        return self.representation

    def _prepare_html(self, text):
        """ remove all the text parts which bother dashtable.py
        See LIST_OF_CHANGE
        """
        buf = ""
        buf2 = ""
        i = 0
        while i < len(text):
            buf += text[i]
            if len(buf) == 9:
                if buf == 'colSpan="' or buf == 'rowSpan="':
                    while buf2 != '"':
                        i += 1
                        buf2 = text[i]
                    text = text[0:i] + text[i + 1:len(text)]
                    buf2 = ""
                buf = buf[1:9]
            i += 1
        for i in range(len(LIST_OF_DEL)):
            try:
                text = remove_piece_of_text(text,
                                            LIST_OF_DEL[i][0],
                                            LIST_OF_DEL[i][1],
                                            LIST_OF_DEL[i][2])
            except:
                text = remove_piece_of_text(text,
                                            LIST_OF_DEL[i][0],
                                            LIST_OF_DEL[i][1])
        for i in range(len(LIST_OF_CHANGE)):
            text = text.replace(LIST_OF_CHANGE[i][0], LIST_OF_CHANGE[i][1])
        return text

    def get_dat_tab(self):
        """ recover the each cells + the tab squeleton """
        tab = []
        text = ""
        flag = False
        isth = False
        max_col = 0
        col = -1  # to agree with my PC friend and start counting at 0
        row = -1  # to agree with my PC friend and start counting at 0
        for t in range(len(self.clean_html)):
            buf = self.clean_html[t:t + 4]
            if buf == '<tr>' or buf == '<tr ':
                try:
                    test = tab[row + 1]
                except:
                    tab.append([])
                    for x in range(len(tab[row])):
                            tab[row + 1].append('X')
                col = -1
                row += 1
            elif (buf == '<td ' or buf == '<td>' or
                    buf == '<th ' or buf == '<th>'):
                if buf == '<th ' or buf == '<th>':
                    isth = True
                flag = True
            elif (buf == '/td>' or
                    buf == '/th>' or
                    buf[2:4] == '/>'):
                col += 1
                flag = False
                if buf == '/td>' or buf == '/th>':
                    text += buf
                    self.cellslist.append(Cell(text, isth))
                else:
                    self.cellslist.append(Cell(None, isth))
                isth = False
                text = ''
                for i in range(self.cellslist[-1].rowspan):
                    try:
                        test = tab[row + i]
                    except:
                        tab.append([])
                        for x in range(len(tab[row + i - 1])):
                            tab[row + i].append('X')
                    if i == 0:
                        try:
                            A = tab[row + i][col]
                            if A == 'X':
                                tab[row + i][col] = len(self.cellslist) - 1
                                cspan = col
                            else:
                                flag2 = True
                                x = col
                                while x < len(tab[row + i]) and flag2:
                                    if tab[row + i][x] == 'X':
                                        tab[row + i][x] = len(self.cellslist) - 1
                                        cspan = x
                                        flag2 = False
                                    else:
                                        x += 1
                                if flag2:
                                    tab[row + i].append(len(self.cellslist) - 1)
                                    cspan = len(tab[row + i]) - 1
                        except:
                            tab[row + i].append(len(self.cellslist) - 1)
                            cspan = len(tab[row + i]) - 1
                    for j in range(cspan, cspan + self.cellslist[-1].colspan):
                        while cspan + self.cellslist[-1].colspan > len(tab[row + i]):
                            tab[row + i].append('X')
                        tab[row + i][j] = len(self.cellslist) - 1
            elif buf == '/tr>':
                if len(tab[row]) > max_col and row != -1:
                    max_col = len(tab[row])
            if flag:
                text += self.clean_html[t]
        for i in range(len(tab)):
            if len(tab[i]) < max_col:
                last_cell = tab[i][-1]
                while len(tab[i]) < max_col:
                    tab[i].append(last_cell)
        for i in range(len(tab)):
            for j in range(max_col):
                if tab[i][j] == 'X':
                    if j > 0:
                        tab[i][j] = tab[i][j - 1]
                    else:
                        tab[i][j] = 0
        return tab

    def get_the_sizes(self):
        """ define the final columns and rows size depending the cells:
        widht column <--  size of the largest cell of the column
        height line <--  size of the highest cell of the line
        cells size/colspan or rowspan if >1 """
        height_max = []
        width_max = []
        for i in range(len(self.tab)):
            for j in range(len(self.tab[i])):
                wdth = (self.cellslist[self.tab[i][j]].width //
                        self.cellslist[self.tab[i][j]].colspan)
                if ((self.cellslist[self.tab[i][j]].width %
                        self.cellslist[self.tab[i][j]].colspan) != 0):
                    wdth += 1
                try:
                    if wdth > width_max[j]:
                        width_max[j] = wdth
                except:
                    width_max.append(wdth)
                hght = (self.cellslist[self.tab[i][j]].height //
                        self.cellslist[self.tab[i][j]].rowspan)
                if ((self.cellslist[self.tab[i][j]].height %
                        self.cellslist[self.tab[i][j]].rowspan) != 0):
                        hght += 1
                try:
                    if hght > height_max[i]:
                        height_max[i] = hght
                except:
                    height_max.append(hght)
        while sum(width_max) > 150:
            for x, val in enumerate(width_max):
                width_max[x] = val // 2
                if val % 2 != 0:
                    width_max[x] += 1
        return width_max, height_max

    def get_repr(self):
        """ pre-define the representation of the Table when it is created
        in order to avoid re-calculated it for each print"""
        rep = ''
        line = '+'
        for j in range(len(self.widths)):
            line += '-' + '-' * self.widths[j] + '-+'
        line += '\n'
        rep += line
        line = ''
        flag = []
        for iter_variable_de_merde in range(len(self.widths)):
            flag.append(False)
        for i in range(len(self.heights)):
            h = 0
            while h <= self.heights[i]:
                for j in range(len(self.widths)):
                    if h == 0 and flag[j] is False:
                        flag[j] = True
                    w = 0
                    x = self.cellslist[self.tab[i][j]].itr
                    X = self.tab[i][j]
                    # Creation of the left line of the cell if j=0
                    # And deals with colspan
                    if j == 0:
                        if h == self.heights[i]:
                            line += '+'
                        else:
                            line += '|'
                    # contents of the cell
                    if flag[j]:
                        if (j > 0 and
                                self.tab[i][j] == self.tab[i][j - 1] and
                                flag[j - 1] and
                                x < len(self.cellslist[X].contents)):
                            line += self.cellslist[X].contents[x]
                            x += 1
                        else:
                            line += ' '
                        while w < self.widths[j]:
                            if (x >= len(self.cellslist[X].contents) and
                                    flag[j]):
                                flag[j] = False
                            if flag[j]:
                                line += self.cellslist[X].contents[x]
                                x += 1
                            else:
                                line += ' '
                            if (h == self.heights[i] - 1 and
                                    (i == len(self.heights) - 1 or
                                     self.tab[i][j] != self.tab[i + 1][j]) and
                                    x < len(self.cellslist[X].contents)):
                                self.heights[i] += 1
                            w += 1
                    elif (h == self.heights[i] and
                            ((flag[j] is False and
                                i < (len(self.heights) - 1) and
                                self.tab[i][j] != self.tab[i + 1][j]) or
                                i == (len(self.heights) - 1))):
                        line += '-' + '-' * self.widths[j]
                    else:
                        line += ' ' + ' ' * self.widths[j]
                    # right line of the cell
                    if (j < len(self.widths) - 1 and
                            self.tab[i][j] == self.tab[i][j + 1]):
                        if x < len(self.cellslist[X].contents):
                            line += self.cellslist[X].contents[x:x + 2]
                            x += 2
                        elif (h == self.heights[i] and
                                ((flag[j] is False and
                                    i < (len(self.heights) - 1) and
                                    self.tab[i][j] != self.tab[i + 1][j]) or
                                    i == (len(self.heights) - 1))):
                            line += '--'
                        else:
                            line += '  '
                    elif h == self.heights[i]:
                        if ((flag[j] is False and
                                i < (len(self.heights) - 1) and
                                self.tab[i][j] != self.tab[i + 1][j]) or
                                i == (len(self.heights) - 1)):
                            line += '-+'
                        else:
                            line += ' +'
                    else:
                        line += ' |'
                    # end of the line?
                    if j == len(self.widths) - 1:
                        line += '\n'
                        rep += line
                        line = ''
                    self.cellslist[self.tab[i][j]].itr = x
                h += 1
        return rep

    def make_dat_html(self):
        """ create a clean simple html from our object(cellslist + tab)"""
        new_html = '<table class="modtab"><tbody>'
        for i in range(len(self.tab)):
            new_html += '<tr>'
            for j in range(len(self.tab[i])):
                if i > 0 and self.tab[i - 1][j] == self.tab[i][j]:
                    continue
                if j > 0 and self.tab[i][j - 1] == self.tab[i][j]:
                    continue
                if self.cellslist[self.tab[i][j]].isth:
                    new_html += '<th '
                else:
                    new_html += '<td '
                new_html += ('colspan="' +
                             str(self.cellslist[self.tab[i][j]].colspan) +
                             '"')
                new_html += ('rowspan="' +
                             str(self.cellslist[self.tab[i][j]].rowspan) +
                             '">')
                new_html += self.cellslist[self.tab[i][j]].contents
                if self.cellslist[self.tab[i][j]].isth:
                    new_html += '</th>'
                else:
                    new_html += '</td>'
            new_html += '</tr>'
        new_html += '</tbody></table>'
        return new_html

"""
TEST = """
"""

A = Table(TEST)
print(A)

# Revoir si manque de ligne, ajouter une ligne
# Revoir si mot coupé
"""
