from models import User, Post, Likes, Muscle, Equipment, PostEquipment, PostMuscle
from app import db, do_logout

db.drop_all()
db.create_all()


# define initial muscle options

biceps = Muscle(name='biceps', body_part='arms')
triceps = Muscle(name='triceps', body_part='arms')
deltoids = Muscle(name='deltoids', body_part='shoulders')
traps = Muscle(name='traps(trapezius)', body_part='shoulders')
lats = Muscle(name='lats(latissmus)', body_part='back')
pecs = Muscle(name='pecs(pectoralis)', body_part='chest')
forearms = Muscle(name='forearms', body_part='arms')
ab = Muscle(name='abs(abdominals)', body_part='abs')
hips = Muscle(name='hips(hip flexors)', body_part='legs')
groin = Muscle(name='groin', body_part='legs')
glutes = Muscle(name='glutes(gluteus)', body_part='legs')
quads = Muscle(name='quads(quadriceps)', body_part='legs')
hams = Muscle(name='hamstrings', body_part='legs')
calves = Muscle(name='calves', body_part='legs')

db.session.add_all([biceps, triceps, deltoids, traps, lats,
                    pecs, forearms, ab, hips, groin, glutes, quads, hams, calves])
db.session.commit()


# define initial equipment options
barbell = Equipment(name='barbell')
kettlebell = Equipment(name='kettlebell')
dumbbells = Equipment(name='dumbbells')
half = Equipment(name='half-rack')
bench = Equipment(name='bench')
pullup = Equipment(name='pullup bar')
body = Equipment(name='bodyweight')
physioball = Equipment(name='physioball')
medicine_ball = Equipment(name='medicine ball')
curl = Equipment(name='curl bar')
pulley = Equipment(name='pulley machine')
squat = Equipment(name='squat rack')
smith = Equipment(name='smith machine')
tred = Equipment(name='treadmill')
elliptical = Equipment(name='elliptical')
stairmaster = Equipment(name='stairmaster')
row = Equipment(name='row machine')
trx = Equipment(name='trx')
resistance = Equipment(name='resistance bands')
battle = Equipment(name='battle ropes')
dip = Equipment(name='dip station')
assist = Equipment(name='weight-assist')
adduct = Equipment(name='hip adductor')
abduct = Equipment(name='hip abductor')

db.session.add_all([barbell, kettlebell, dumbbells, half, bench, pullup, body, physioball, medicine_ball, curl,
                    pulley, squat, smith, tred, elliptical, stairmaster, row, trx, resistance, battle, dip, assist, adduct, abduct])
db.session.commit()
