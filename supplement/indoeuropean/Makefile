indoeuropean.nex:
	curl https://raw.githubusercontent.com/PhyloStar/ie-phylo-exps/a63c0b52f7772adc2341572932a74b23d92570df/medium1.nex -o indoeuropean.nex

check-zip: indoeuropean.zip
	echo "59451dbfcdb949ba8d8a42c74d9f70f629b35027a08323393bf3b415  indoeuropean.nex" | sha224sum -c
	touch check-zip

indoeuropean-template.xml languages.txt: indoeuropean.nex ../template.xml
	python insert_nexus_into_beast.py indoeuropean.nex ../template.xml indoeuropean-template.xml > languages.txt

indoeuropean.xml: indoeuropean-template.xml add_calibrations.py
	cp indoeuropean-template.xml indoeuropean.xml
	PYTHONPATH=../ python add_calibrations.py -o indoeuropean.xml

run/vocabulary.log: indoeuropean.xml
	mkdir -p run
	cd run && beast ../indoeuropean.xml
