"""
http://www.cumsejoaca.ro/reguli-de-joc-regulament/scrabble-regulament-de-joc/
https://scrabble.hasbro.com/en-us/rules
# https://repl.it/@Bookie0/ZooooomCar#main.py pentru culori
TEMA:
  - primul cuvant introdus in joc sa includa punctul din mijloc (H8)
  - cuvintele ulterioare sa se intersecteze/lege cu cuvinte existente pe tabla (hint: vezi in place_word) 
    - de exemplu, pe tabla poate sa existe "BALAUR", jucatorul adauga "I" la sfarsit, rezulta "BALAURI", care e OK
"""
import random

table = []
tile_values = {} # 'A': 1, 'E': 1, 'Z': 9, ...
bag = {} # 'A': 8, 'E': 12, 'Z': 1, ...
player_tiles = [] # array of arrays, contains tiles for each player
player_points = []
player_names = []
available_words = []
player_count = 0
current_player = 0
trans = "₀₁₂₃₄₅₆₇₈₉"
is_first_word = True

def load_tiles():
  f = open('scrabble_tiles.txt') # we don't have the '_: 0x2' record at the top, for jokers
  content = f.read()
  f.close()
  lines = content.split('\n')
  for line in lines:
    tile = line[0] # 'A', 'B', ...
    value = int(line[3]) # 1, 3, ...
    count = int(line[5:]) # 9, 3, ...
    tile_values[tile] = value
    for tiles in player_tiles:
      tiles[tile] = 0
    bag[tile] = count

def init_table():
  for i in range(15):
    small_list = []
    for j in range(15):
      small_list.append('.') #☐')
    table.append(small_list)
    
def load_dictionary():
  global available_words
  # f = open('listofwords_en.txt')
  f = open('words_alpha.txt') # from https://github.com/dwyl/english-words/
  content = f.read()
  f.close()
  available_words = content.upper().split('\n')

def show_table():
  "responsible for displaying the game board; to be called after every player's turn"
  global player_names, player_tiles, player_count, player_points, current_player
  print('    ', end='')
  print(' 1', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', ' 8', ' 9', '10', '11', '12', '13', '14', '15', sep = ' |  ', end = '\n\n') # number coords
  for i in range(15):
    line = chr(i + 65) + '    '
    for j in range(15):
      tile_to_show = table[i][j]
      line += tile_to_show
      if tile_to_show != '.':
        line += trans[(tile_values[tile_to_show])]
      else:
        line += ' ' 
      #old: 
      line += '    '
      # new: line += ' |  '
    # old: 
    print(line, end = '\n\n')
    # new:     print(line, '\n', '-' * 90)
  for i in range(player_count):
    tiles = get_player_tiles(player_tiles[i])
    # string interpolation:
    print(f'{player_names[i]}{" *" if current_player == i else "  "}: {tiles}; {player_points[i]} points')

def get_player_tiles(player_tiles):
  "gets player's available tiles"
  tiles = []
  for tile in player_tiles:
    for i in range(player_tiles[tile]):
      tiles.append(tile)
  tiles = ' '. join(tiles)
  return tiles

def decode_coord(coord): # ex: H11
  "takes a coord such as H11 or 7G and decodes it into a list of: [row, column, orientation]"
  coord = coord.upper()
  if ord('A') <= ord(coord[0]) <= ord('Z'):
   row = ord(coord[0]) - ord('A')
   col = int(coord[1:]) - 1
   ort = 'h'
  else:
   row = ord(coord[-1]) - ord('A')
   col = int(coord[:-1]) - 1
   ort = 'v'
  return [row, col, ort]

def get_letter(coord):
  [row, col, ort] = decode_coord(coord)
  return table[row][col]

def set_letter(coord, value):
  [row, col, ort] = decode_coord(coord)
  table[row][col] = value

def word_value(word):
  "computes the value of the word by summing up the values of its components/characters"
  result = 0
  for char in word.upper():
    char_value = tile_values[char]
    result = result + char_value
  return result

def place_word(coord, word, player_tiles):
  """place word on table, starting with given coordinates
  <digit letter> means vertical, <letter digit> means horizontal
  player_tiles contains the tiles the player has in hand
  Returns: negative number if word cannot be placed, otherwise points attained"""
  global is_first_word
  [row, col, ort] = decode_coord(coord)
  # does word fall outside the table? no => OK, yes => not OK
  if (ort == 'h' and len(word) + col > 14) or (ort == 'v' and len(word) + row > 14):
      print('Word falls outside table')
      return -1
  player_tiles_copy = player_tiles.copy()
  positions = compute_word_coords(coord, word.upper())
  score = 0
  intersects_any_word = False
  print('aaaaaa')
  for [coordinate, in_hand, on_table] in positions:
    if on_table == '.': 
      # is_player_tiles_missing_tile(player_tiles, letter)
      if player_tiles.get(in_hand, 0) == 0: 
        print('Player does not hold', in_hand, 'in hand')
        return -2
      else:
        intersected_word = get_intersected_word(on_table, in_hand, coordinate)      
        print('Found intersected_word', intersected_word)
        if intersected_word != None:
          if intersected_word not in available_words:
            return -3
          intersects_any_word = True
          print('Adding', word_value(intersected_word), 'for', intersected_word)
          # points made by changing existing words on table
          score += word_value(intersected_word)
    else:
      if on_table != in_hand:
        return -4
    player_tiles_copy[in_hand] -= 1
  print('bbbbbbbbb, is_first_word =', is_first_word)
  # for first word, check that it touches mid position
  if is_first_word:
    found_mid_position = False
    for [coordinate, in_hand, on_table] in positions:
      print(coordinate, in_hand, on_table)
      if coordinate == 'H8' or coordinate[0] == '8H':
        found_mid_position = True
    if found_mid_position == False:
      print('First word must contain coord H8')
      return -20
  else:
    # otherwise, it must intersect at least one other word on the table
    print('ccccc')
    if not intersects_any_word :
      print('Your word does not intersect any other word on the table')
      return -30
  # actually write word, skipping letters already on table
  print('dddddd')
  for [coordinate, in_hand, on_table] in positions:
    if on_table == '.':
      set_letter(coordinate, in_hand)
      player_tiles[in_hand] -= 1
  # add to score points made by word itself
  score += word_value(word)
  is_first_word = False
  return score

def get_intersected_word(letter_on_table, letter_in_hand, coord):
  """takes letter_on_table, its desired position on board and orientation of word
  return any word it would intersect, perpendicular on orientation, or None"""
  # print(letter_on_table, letter_in_hand, coord)
  [row, col, ort] = decode_coord(coord)
  if letter_on_table != '.':
    return None
  intersected_word = [ letter_in_hand ]
  if ort == 'h':
    row1 = row
    while row1 > 0 and table[row1][col] != '.':
      intersected_word.insert(0, table[row1][col])
      row1 -= 1
    row2 = row + 1
    while row2 < 15 and table[row2][col] != '.':
      intersected_word.append(table[row2][col])
      row2 += 1
    # print('horiz:', row, row1, row2, intersected_word)
  else:
    col1 = col - 1
    while col1 > 0 and table[row][col1] != '.':
      intersected_word.insert(0, table[row][col1])
      col1 -= 1
    col2 = col + 1
    while col2 < 15 and table[row][col2] != '.':
      intersected_word.append(table[row][col2])
      col2 += 1
    # print('vert:', col, col1, col2, intersected_word)
  intersected_word = ''.join(intersected_word)
  if intersected_word == letter_in_hand:
    return None
  else:
    return intersected_word

def is_table_position_free(on_table):
  return on_table == '.'

def is_player_tiles_missing_tile(player_tiles, letter):
  return player_tiles.get(letter, 0) == 0

def compute_word_coords(coord, word):
  """compute all the positions that the word should take on the table. 
  returns list of positions, as strings"""
  positions = []
  [row, col, ort] = decode_coord(coord)
  for letter in word:
    if ort == 'h':
      coord = chr(row + ord('A')) + str(col + 1)
      col = col + 1
    else:
      coord = str(col + 1) + chr(row + ord('A'))
      row = row + 1    
    positions.append([coord, letter, get_letter(coord)])
  return positions

def count_tiles(tiles):
  "takes a dictionary of tiles and returns the current count of tiles"
  result = 0
  for tile in tiles:
    result += tiles[tile]
  return result

def refill_rack(player_tiles): # e.g. player_tiles = {'_': 0, 'A': 2, 'B': 1, ..., 'R': 1, ...}
  "takes a player's tiles and makes sure they end up with 7 tiles (or max allowed by available in bag)"
  # how many tiles are needed from the bag? 7 - current player_tiles count
  target_count = 7 - count_tiles(player_tiles)  
  # for each of those do:
  while target_count > 0:
    # randomly pick a tile from the bag:
    # collect existent tiles into an "available" dictionary
    available = get_available_tiles(bag)
    # randomly pick a tile index, because random works with numbers, not dictionaries or arbitrary objects
    tile_count = len(available) # count of available types of tiles
    if tile_count > 0:
      target_count -= 1
      random_index = random.randrange(tile_count) # picked the x-th type of tile
      counter = 0
      for letter in available: # e.g. if we have A B R Z
        if counter == random_index: # e.g. if random_index = 2
          # found tile in bag, so take out of bag
          bag[letter] = bag[letter] - 1
          # and add to player's collection
          player_tiles[letter] = player_tiles[letter] + 1
          break
        else:
          counter += 1
  # return target_count

def get_available_tiles(tiles):
  "returns tiles that are actually in the collection"
  available = {} # dictionar care va contine perechi
  for letter in tiles:
    if tiles[letter] > 0: # daca in saculet mai exista litera letter
      available[letter] = tiles[letter]
  return available

def pick_starting_player(player_count):
  "randomly chooses which player will start, based on number of players"
  starting_player = random.randrange(player_count)
  return starting_player

def game_continues():
  "returns true if all players have tiles on their supports"
  for i in player_tiles:
    if count_tiles(i) == 0:
      return False
  return True

commands = 'HELP, TILES, PASS, TABLE, CHECK <word>, XCHG/EXCHANGE <t i l e s>, MOVE <coords> <word>'

def cmd_help(choice):
  if choice == 'HELP' or choice == '?' or choice == 'H':
    print('Commands are: ' + commands)
    return (True, -700)
  return (False, -700)

def cmd_tiles(choice):
  if choice == 'TILES':
    print('YOUR tiles:', get_player_tiles(player_tiles[current_player]))
    return (True, -200)
  return (False, -200)

def cmd_table(choice):
  if choice == 'TABLE':
    show_table()
    return (True, -500)
  return (False, -500)

def cmd_pass(choice):
  if choice == 'PASS':
    return (True, 0)
  return (False, -300)

def cmd_check(choice):
  global available_words
  if choice.find('CHECK ') == 0:
    word = choice[6:]
    print(f'{word} is {"" if word in available_words else "NOT "}available')
    return (True, -400)
  return (False, -400)

def cmd_exchange(choice):
  "allows you to exchange tiles from your hand with some from the bag. you ask for 1 to all of your tiles to be exchanged, it checks you actually have them, if no - bad luck, nothing happens, if yes it then takes them from you, puts them in the bag, then refills your rack as usual"
  global player_tiles, bag, current_player
  tiles = None
  if choice.find('EXCHANGE ') == 0:
    tiles = choice[9:].split()
  if choice.find('XCHG ') == 0:
    tiles = choice[5:].split()
  if tiles != None:
    # attempt to take required tiles from player's hand
    player_tiles_copy = player_tiles[current_player].copy()
    temp_bag = []
    for tile in tiles:
      if player_tiles_copy[tile] > 0:
        player_tiles_copy[tile] -= 1
        temp_bag.append(tile)
      else:
        return (True, -600) # command correct, but player tried to replace tile they didn't have
    # that was just a copy, so actually take them out
    old_tiles = get_player_tiles(player_tiles[current_player])
    for tile in tiles:
      player_tiles[current_player][tile] -= 1
    # and put them back in the bag
    for tile in temp_bag:
      bag[tile] += 1
    # now refill player's hand
    refill_rack(player_tiles[current_player])
    print(f'You had {old_tiles}, you now have {get_player_tiles(player_tiles[current_player])}')    
    return (True, 0) # pass turn
  return (False, -600)

def cmd_move(choice):
  if choice.find('MOVE ') == 0:
    choice = choice[5:]          
    score = word_is_ok(choice, player_tiles[current_player])
    print('choice:', choice)
    print('score:', score)
    return (True, score)
  return (False, None)

cmds = [ cmd_help, cmd_tiles, cmd_pass, cmd_check, cmd_exchange, cmd_move ]

def run_turn():  
  message = player_names[current_player] + ' command: ' + commands + '\n'
  choice = input(message).upper()
  for cmd in cmds:
    (handled, score) = cmd(choice)
    #print(cmd.__name__[4:], handled, score)
    if handled:
      return score
  return -1000

def do_player_turn():
  "does turn for player, returning attained score; player can enter multiple commands"
  score = run_turn()
  while score < 0:
    # print('score is', str(score), 'continuing')
    score = run_turn()
  print('moving on')
  return score

def word_is_ok(choice, tiles):
  "takes player's choice, which is of the form '<coord> <word>'. returns true if word is in dictionary, fits on the table, can be added by said player"
  splits = choice.split(' ')
  coord = splits[0]
  word = splits[1]
  if word not in available_words:
    return -100
  score = place_word(coord, word, tiles)
  return score
  
def show_winner():
  """1. find out max player points
  2. loop through player points and for each index whose points are the same as max, print the value at the corresponding index in the player names"""
  max_points = max(player_points)
  for i in range(len(player_points)):
    if player_points[i] == max_points:
      print(player_names[i], 'has won')

def initialise():
  global player_count
  player_count = 2 # int(input('How many players?\n'))
  for i in range(player_count):
    player_tiles.append({}) # fiecare jucator are un dictionar gol de piese
    player_points.append(0) # fiecare jucator are 0 puncte la inceput
    player_names.append('Player_' + str(i + 1)) # Player_1, Player_2    
  init_table()
  load_tiles()
  load_dictionary()
  for tiles in player_tiles:
    refill_rack(tiles)
  current_player = pick_starting_player(player_count)

def play_game():
  global current_player, player_points
  initialise()
  show_table()
  while game_continues():
    score = do_player_turn()
    player_points[current_player] += score
    print(player_names[current_player], 'you have', player_points[current_player], 'points')
    refill_rack(player_tiles[current_player])
    current_player += 1
    if current_player == player_count:
      current_player = 0    
    show_table()
  show_winner()

play_game()

# for i in range(player_count):
#   print(get_available_tiles(player_tiles[i]), player_points[i], player_names[i])

# GO
# initialise()
# place_word('7d', 'WONDER', {'D': 1, 'R': 2, 'W': 1, 'E': 1, 'O': 1, 'N': 1})
# place_word('d7', 'WATER', {'R': 2, 'W': 1, 'E': 1, 'T': 1, 'A': 1})
# place_word('h4', 'HOPE', {'H': 2, 'P': 1, 'E': 1, 'O': 1})
# place_word('5g', 'POLICE', {'P': 1, 'O': 1, 'E': 1, 'L': 1, 'I': 1, 'C': 1})
# show_table()

# SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")




  
"""


Pentru fiecare litera din 'PELIN': 
e liber pe tabla?
  da - am piesa in mana?      
    da - se intersecteaza cu vreun cuvant existent?
      da - se potriveste cu cuvantul respectiv? (aici putem sa retinem cuvantul, ca sa-l socotim la puncte)
        da - returneaza True
        nu - returneaza False
      nu - returneaza True
    nu - returneaza False
  nu - e aceeasi piesa?     
    da - returneaza True    
    nu - returneaza False

1.
if is_position_free_on_table(position):
  if has_player_tile(tile):
    if is_intersected_with_word_on_table(?):
      if ....:
        return True
      else:
        return False
    else:
      return True
  else:
    return False
else:
  if is_same_tile(tile?):
    return True
  else:
    return False

2.
if is_position_free_on_table(position):
  if has_player_tile(tile):
    intersected_word = get_intersected_word(tile, coordinates)
    if intersected_word != None:                            # if is_intersected_with_word_on_table(...)
      if is_word_in_dictionary(intersected_word):                # if is_intersected_word_in_dictionary
        return True
      else:
        return False
    else:
      return True
  else:
    return False
else:
  if is_same_tile(tile?):
    return True
  else:
    return False










Pentru ca in caz de eroare (piesa lipsa, patratica ocupata cu altceva etc) iesim din functie cu False, ne intereseaza mai ales partile alea; in caz ca algoritmul nu are nevoie sa se opreasca, merge mai departe
e liber pe tabla?
  da - am piesa in mana?      
    da - se intersecteaza cu vreun cuvant existent?
      da - se potriveste cu cuvantul respectiv? (aici putem sa retinem cuvantul, ca sa-l socotim la puncte)
        nu - returneaza False
    nu - returneaza False
  nu - e aceeasi piesa?   
    nu - returneaza False



H5 rau
L4 pelin: L4 P; L5 E; L6 L; L7 I; L8 N
4L pelin: 4L P; 4M E; 4N L; 4O I; 

"""