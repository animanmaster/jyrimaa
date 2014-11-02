from game_examiner import *

print 'Loading move_data'
move_data = pickle.load(file('move_data%d.pickle' % GAME_LIMIT))
# encountered = pickle.load(file('encounteredhash.pickle'))
print 'Loading pd_per_turn'
pd_per_turn = pickle.load(file('pd_per_turn%d.pickle' % GAME_LIMIT))

print 'Analyzing data...'

stathash = {}
turnstathash = {}

total_number_of_moves = 0
moves_with_same_before_and_after = dict(map(lambda r: [r, 0], range(14)))
for game_id, turn_id in move_data:
  # print 'Examining', (game_id, turn_id)
  turn_data = move_data[game_id, turn_id]
  for move_number in turn_data.moves:
    before_and_after_pd = turn_data.moves[move_number]
    total_number_of_moves += 1
    for radius in range(14):
      # print '\t Looking at move number', move_number, 'with radius', radius
      pdhashes = tuple(map((lambda pd: pd and pd.get_filtered_state(radius) or None), before_and_after_pd))
      value = (game_id, turn_id, move_number)
      if pdhashes in stathash:
        stathash[pdhashes].add(value)
        moves_with_same_before_and_after[radius] += 1
      else:
        stathash[pdhashes] = set([value])

# print 'Value counts:', map(lambda v: len(v), stathash.values())
counts = {}
for tup in stathash:
  associated = stathash[tup]
  if len(associated) in counts:
    counts[len(associated)] += 1
  else:
    counts[len(associated)] = 1

  if len(stathash[tup]) >= 2:
    print tup, ':'
    print '\t', stathash[tup]
# print 'Number of cases with the given length of associated values:'
# print sorted(counts.iteritems(), key=lambda a: -a[1])

total_unique_pairs = len(stathash.keys())
print "Total number of moves examined (per radius):", total_number_of_moves
print "Total number of unique (before,after) tuples:", total_unique_pairs
print "Total number of moves with same before and after hash per radius:"
for radius in moves_with_same_before_and_after:
  value = moves_with_same_before_and_after[radius]
  print "\t Radius", radius + 1, ":", value, "[", (float(value)/float(total_number_of_moves) * 100), '% ]'

