.PHONY : deploy

deploy : backend frontend
	rsync -Cavr --exclude '*.pyc' --exclude '*~' . princeton:/n/fs/tmpl


