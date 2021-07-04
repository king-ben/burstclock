bantu.zip:
	curl https://codeload.github.com/lexibank/grollemundbantu/zip/v1.0rc6 -o bantu.zip

check-zip: bantu.zip
	echo "34ae13e629924553766abc251dd51423765387f8f1a2c2d94a232237  bantu.zip" | sha224sum -c
	touch check-zip

bantu-template.xml: ../template.md
	python ../without_markdown.py bantu-template.xml

raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json: bantu.zip check-zip
	unzip -DD -o -j bantu.zip  "grollemundbantu-1.0rc6/cldf/*" -d raw_cldf/

bantu-undated.xml stats.tex: raw_cldf/cldf-metadata.json add_calibrations.py bantu-template.xml
	cp bantu-template.xml bantu-undated.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata raw_cldf/cldf-metadata.json -b -o bantu-undated.xml

bantu.xml: bantu-undated.xml add_calibrations.py
	cp bantu-undated.xml bantu.xml
	PYTHONPATH=../ python add_calibrations.py -o bantu.xml

bantu-burstclock.xml: bantu.xml ../add_burstclock.py
	python ../add_burstclock.py bantu.xml -o bantu-burstclock.xml

run/vocabulary.log: bantu.xml
	mkdir -p run
	cd run && beast ../bantu.xml
