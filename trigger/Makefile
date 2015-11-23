SHELL := /bin/sh

all: 

www:
	rsync -avz --progress --exclude '*.pdf' --include '*/*/*' --include '*/*/*/*' --include '*.png' plots/* ~/www/vbfHbb/trigger/
	find ~/www/vbfHbb/trigger/ -type f -not -name *noleg.png -exec rm {} \;
	find ~/www/vbfHbb/trigger/ -type d -exec cp ~/www/vbfHbb/index.php {} \;

