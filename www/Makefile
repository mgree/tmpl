.PHONY : deploy

deploy : backend frontend
	rsync -Cavr --exclude '*.pyc' --exclude '*~' . weaselhat:tmpl


