default:
	python export.py
	scp rod.db shifts.json volunteers.json rod@rod.rasmusbrinck.se:/var/www/static/data/
	scp util.py secrets.py sms.py model.py rod@rod.rasmusbrinck.se:rod-skema/

