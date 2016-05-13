.PHONY : deploy

deploy : backend frontend
	rsync -ClgoDvr --exclude '*.pyc' --exclude '*~' --exclude paths.py --exclude playground --exclude uploads . princeton:/n/fs/tmpl


