from kivy.config import ConfigParser

__all__ = ('get_config', )

def get_config():

    config = ConfigParser()
    config.read('config.ini')
    
    config.adddefaultsection('game')
    config.setdefault('game', 'outside_coordinates', True)
    config.setdefault('game', 'show_pieces', True)
    config.setdefault('game', 'square_coordinates', False)

    

    return config


