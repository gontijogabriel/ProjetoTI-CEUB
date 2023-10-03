from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers import verifica_banco
from app import app

if __name__ == '__main__':

    try:   
        scheduler = BackgroundScheduler()
        scheduler.add_job(verifica_banco, 'interval', seconds=10)
        scheduler.start()
    except:
        pass

    app.run(debug=True)


