from datetime import datetime

now = datetime.now().time()
a = "16:00:00.000000"

if str(now.hour) == a[:2]:
    print('SIMMMM')


