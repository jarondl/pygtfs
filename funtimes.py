from gtfsparser.schedule import Schedule

sched = Schedule( "/home/brandon/Desktop/davepeck_20100806_2257.db" )

counts = {}

def cons(ary):
  for i in range(len(ary)-1):
    yield ary[i],ary[i+1]

for route in sched.routes:
  print route.route_short_name
  for trip in route.trips:
    print trip
    for st1,st2 in cons(trip.stop_times):
      counts[(st1.stop_id,st2.stop_id)] = counts.get( (st1.stop_id,st2.stop_id), 0 ) + 1

print counts
