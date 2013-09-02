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

from kivy.utils import get_color_from_hex

from config import get_config
from ChessBoard import ChessBoard

config = get_config()

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
    'cream': get_color_from_hex('#FFFFFF'),
    'brown': get_color_from_hex('#bf9e7e'),
}

DARK_SQUARE = COLOR_MAPS['brown']
LIGHT_SQUARE = COLOR_MAPS['cream']

def get_square_abbr(coord):
    return SQUARES[coord]

class ChessCoord(Label):
    show = BooleanProperty(True)

    _text = StringProperty('')

    def on_show(self, *args):
        if not self._text:
            self._text = self.text

        if self.show:
            self.text = self._text

        else:
            self.text = ''

    
class ChessSquare(Button):
    coord = NumericProperty(0)
    piece = ObjectProperty(None, allownone=True)
    show_piece = BooleanProperty(True)
    show_coord = BooleanProperty(False)

    def __init__(self, background_color, **kwargs):
        super(ChessSquare, self).__init__(**kwargs)
        self.background_color = background_color
        self.background_normal = ''
        self.markup = True

    def add_piece(self, piece):
        self.remove_widget(self.piece)
        self.piece = piece
        if self.piece:
            self.piece.hide = not self.show_piece
            self.add_widget(piece)
            piece.set_size(self.size)
            piece.set_pos(self.pos)

    def on_release(self):
        self.state = 'down'
        app.process_move(self)

    def on_show_piece(self, *args):
        if self.piece:
            self.piece.hide = not self.show_piece

    def on_show_coord(self, *args):
        if self.show_coord:
            self.text = '[color=%s]%s[/color]' % ('#000000', SQUARES[self.coord])

        else:
            self.text = ''


    # def on_piece(self, instance, piece):
    #     if piece:
    #         piece.set_size(self.size)
    #         piece.set_pos(self.pos)
    #         self.add_widget(piece)


    def remove_piece(self):
        if self.piece:
            self.remove_widget(self.piece)


    def on_size(self, instance, size):
        # print '%s Size: %s' % (get_square_abbr(self.coord), size)
        if self.piece:
            self.piece.set_size(size)


    def on_pos(self, instance, pos):
        # print '%s Positions: %s' % (get_square_abbr(self.coord), pos)
        if self.piece:
            self.piece.set_pos(pos)

    # def on_touch_down(self, touch):
    #     if super(ChessSquare, self).on_touch_down(touch):
    #         app.process_move(self)


class ChessPiece(Scatter):

    image = ObjectProperty(None)
    moving = BooleanProperty(False)
    allowed_to_move = BooleanProperty(False)

    hide = BooleanProperty(False)


    def __init__(self, image_source, **kwargs):
        super(ChessPiece, self).__init__(**kwargs)

        self.image = Image(source=image_source)
        self.image.allow_stretch = True
        self.add_widget(self.image)
        self.auto_bring_to_front = True

    def on_hide(self, *args):
        self.remove_widget(self.image)

        if not self.hide:
            self.add_widget(self.image)

    def set_size(self, size):
        # Set both sizes otherwise the image
        # won't sit properly, and the scatter becomes larger than
        # the image.
        self.size = size[0], size[1]
        self.image.size = size[0], size[1]

    def set_pos(self, pos):
        self.pos = pos[0], pos[1]

    def on_touch_move(self, touch):
        if not self.allowed_to_move:
            return
        if super(ChessPiece, self).on_touch_move(touch):
            self.moving = True

    def on_touch_up(self, touch):
        if super(ChessPiece, self).on_touch_up(touch):
            if self.parent and self.moving:
                app.check_piece_in_square(self)

            self.moving = False


    def on_touch_down(self, touch):
        if super(ChessPiece, self).on_touch_down(touch):
            pass


class ChessGameApp(App):

    squares = ListProperty([])
    coords = ListProperty([])

    main_text = ObjectProperty(None)
    chess_grid = ObjectProperty(None)

    chessboard = ChessBoard()

    prev_coord = None
    current_coord = None

    SETTINGS_FUNC_MAP = {
        'outside_coordinates': 'toggle_coordinates',
        'show_pieces': 'toggle_pieces',
        'square_coordinates': 'toggle_square_coords',
    }


    def check_piece_in_square(self, piece):
        for square in self.squares:
            if square.collide_point(piece.center_x, piece.center_y):
                return self.process_move(square)


    def process_move(self, square):
        prev_coord = self.prev_coord
        current_coord = self.current_coord

        coord = square.coord
        current_square = self.squares[coord]

        self.prev_coord = current_coord
        self.current_coord = coord

        if self.prev_coord == self.current_coord:
            self.squares[self.prev_coord].state = 'normal'
            self.squares[self.current_coord].state = 'normal'

            self.current_coord = None
            self.prev_coord = None

            return


        valid_move = None
        if self.prev_coord and self.current_coord:

            pc = SQUARES[self.prev_coord]
            cc = SQUARES[self.current_coord]

            valid_move = False
            if self.chessboard.addTextMove('%s-%s' % (pc, cc)):
                valid_move = True

                # Update game notation
                all_moves = self.chessboard.getAllTextMoves()
                notation = ''
                for i, move in enumerate(all_moves):
                    is_even = False
                    if i % 2 == 0:
                        notation += '%d. ' % ((i / 2) + 1, )
                        is_even = True

                    notation += ' %s ' % move

                    if not is_even:
                        notation += '\n'

                self.root.main_text.text = notation
                

            self.refresh_board()

        if not valid_move and self.prev_coord and self.current_coord:
            self.prev_coord = prev_coord
            self.current_coord = current_coord
            current_square.state = 'normal'


        elif valid_move:
            self.squares[self.prev_coord].state = 'normal'
            self.squares[self.current_coord].state = 'normal'

            self.current_coord = None
            self.prev_coord = None

    def toggle_pieces(self, value):
        for square in self.squares:
            square.show_piece = value


    def toggle_coordinates(self, value):
        for coord in self.coords:
            coord.show = value
    

    def toggle_square_coords(self, value):
        for square in self.squares:
            square.show_coord = value


    def handle_settings_updates(self, section, key, value):
        func = getattr(self, self.SETTINGS_FUNC_MAP[key])
        func(self.value(value))
        config.write()

    def value(self, value):
        if value == 'False' or value == '0':
            return False

        elif value == 'True' or value == '1':
            return True

        return bool(value)


    def get_config_value(self, key, section='game', default=None):
        return self.value(config.getdefault(section, key, default))


    def handle_inital_settings(self):

        self.toggle_pieces(self.get_config_value('show_pieces'))
        self.toggle_coordinates(self.get_config_value('outside_coordinates'))
        self.toggle_square_coords(self.get_config_value('square_coordinates'))

        config.add_callback(self.handle_settings_updates)



    def refresh_board(self):

        squares = [item for sublist in self.chessboard.getBoard() for item in sublist]

        # Only deal with the moves played, so we don't do
        # heaps of unnessacery adding and removing of widgets.
        if self.prev_coord and self.current_coord and \
            squares[self.squares[self.prev_coord].coord] == '.':

            prev_piece = self.squares[self.prev_coord].piece
            self.squares[self.prev_coord].remove_piece()
            self.squares[self.current_coord].add_piece(prev_piece)

            return

        # On initialized
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

            light = i % 2 == (i / 8) % 2

            background_color = LIGHT_SQUARE if light else DARK_SQUARE
            bt = ChessSquare(background_color)
            bt.coord = i

            chess_grid.add_widget(bt)
            self.squares.append(bt)


        settings = root.game_settings
        settings.add_json_panel('Chess', config, 'settings.json')

        self.refresh_board()
        self.handle_inital_settings()

        # root.current = 'settings'
       
        return root



if __name__ == '__main__':
    app = ChessGameApp()
    app.run()