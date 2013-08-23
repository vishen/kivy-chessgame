import kivy
kivy.require('1.8.0')


from kivy.app import App

from kivy.properties import BooleanProperty, \
    ListProperty, ObjectProperty, NumericProperty, \
    StringProperty

from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter

from ChessBoard import ChessBoard

SQUARES = [
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", 
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", 
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", 
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", 
    "a4", "b4","c4", "d4", "e4", "f4", "g4", "h4", 
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", 
    "a2", "b2", "c2","d2", "e2", "f2", "g2", "h2", 
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"
]

IMAGE_PIECE_MAP = {
    "B": "wb", 
    "R": "wr", 
    "N": "wn", 
    "Q": "wq", 
    "K": "wk", 
    "P": "wp",
    "b": "bb", 
    "r": "br", 
    "n": "bn", 
    "q": "bq", 
    "k": "bk", 
    "p": "bp"
}

ROW_COORDS = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
)

COLS_COORS = (
    '8','7', '6', '5', '4', '3', '2', '1',
)

COLOR_MAPS = {
    'black': (1, 1, 1, 1),
    'white': (0, 0, 0, 1),
    'grey': (0.7, 0.7, 0.6, 1),
    'dark_blue': (0.2, 0.3, 0.8, 0.5),
}

DARK_SQUARE = COLOR_MAPS['dark_blue']
LIGHT_SQUARE = COLOR_MAPS['grey']

def get_square_abbr(coord):
    return SQUARES[coord]

class ChessCoord(Label):
    on = BooleanProperty(False)

    
class ChessSquare(ToggleButton):
    coord = NumericProperty(0)
    piece = ObjectProperty(None)

    def add_piece(self, piece):
        self.piece = piece

    def on_piece(self, instance, piece):
        self.add_widget(piece)


    def on_size(self, instance, size):
        print '%s Size: %s' % (get_square_abbr(self.coord), size)
        if self.piece:
            self.piece.set_size(size)


    def on_pos(self, instance, pos):
        print '%s Positions: %s' % (get_square_abbr(self.coord), pos)

        if self.piece:
            self.piece.set_pos(pos)


class ChessPiece(Scatter):

    image = ObjectProperty(None)
    
    def __init__(self, image_source, **kwargs):
        super(ChessPiece, self).__init__(**kwargs)

        self.image = Image(source=image_source)
        self.image.allow_stretch = True
        self.add_widget(self.image)
        self.auto_bring_to_front = True

    def set_size(self, size):
        self.image.size = size[0], size[1]

    def set_pos(self, pos):
        self.pos = pos[0], pos[1]


    def on_touch_up(self, touch):
        if super(ChessPiece, self).on_touch_up(touch):
            self.pos = self.parent.pos
            # self.parent.state = 'normal'


    def on_touch_down(self, touch):
        if super(ChessPiece, self).on_touch_down(touch):
            # self.parent._do_press()
            pass


class ChessGameApp(App):

    squares = ListProperty([])
    coords = ListProperty([])

    main_text = ObjectProperty(None)
    chess_grid = ObjectProperty(None)

    chessboard = ChessBoard()

    def refresh_board(self):

        squares = [item for sublist in self.chessboard.getBoard() for item in sublist]

        for i, square in enumerate(squares):
            piece = None
            if square != '.':
                piece = ChessPiece('resources/images/%s.png' % IMAGE_PIECE_MAP[square])

            self.squares[i].add_piece(piece)

    def build(self):
        # Had to manually load due to not being able to 
        # dynamically add buttons
        self.load_kv('chessgame.kv')

        root = self.root
        chess_grid = root.chess_grid

        # Add empty label
        chess_grid.add_widget(ChessCoord())

        # Add row coords
        for rc in ROW_COORDS:
            l = ChessCoord(text=rc)
            chess_grid.add_widget(l)
            self.coords.append(l)

        for i, square in enumerate(SQUARES):

            if i % 8 == 0:
                rc = COLS_COORS[i/8]
                l = ChessCoord(text=rc)
                chess_grid.add_widget(l)
                self.coords.append(l)

            bt = ChessSquare()
            bt.coord = i

            chess_grid.add_widget(bt)
            self.squares.append(bt)


        self.refresh_board()
       
        return root



if __name__ == '__main__':
    app = ChessGameApp()
    app.run()