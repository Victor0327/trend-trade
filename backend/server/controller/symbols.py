from service import symbols


def get_symbols(args):
  return symbols.get_symbols(args)

def get_my_focus_symbols(args):
  return symbols.get_my_focus_symbols(args)

def pin_to_top(args):
  return symbols.pin_to_top(args)

def add_to_focus(args):
  return symbols.add_to_focus(args)

def remove_from_focus(args):
  return symbols.remove_from_focus(args)