from sometime import Sometime
from arkivist import Arkivist as db

memos1 = db("db/cooper.memo.json")
memos2 = db("db/cooper.memo2.json", sort=True)

min = int(Sometime().add(days=-3, years=-1).timestamp())

for key, memo in memos1.items():
    dt = memo.get("ts", 0)
    if min > int(key):
        dt = Sometime(timestamp=int(dt)).add(years=1).timestamp()
    memo.update({"ts": key})
    memos2.set(str(dt), memo)