.PHONY : deploy

deploy : backend frontend
	rsync -ClgoDvr --exclude '*.pyc' --exclude '*~' --exclude paths.py --exclude uploads . princeton:/n/fs/tmpl


