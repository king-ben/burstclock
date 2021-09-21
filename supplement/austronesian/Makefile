# Download commit 17a4b30922f9d1010667ae8974f814c624e3e9a4 (2020-07-10): “Regenerate CLDF, minor refactorings”
abvd.zip:
	curl https://codeload.github.com/lexibank/abvd/zip/17a4b30922f9d1010667ae8974f814c624e3e9a4 -o abvd.zip

check-zip: abvd.zip
	echo "1e47e29e1b417ac70dae9086f2e9f7e4500390205d7e4ea7c229e875  abvd.zip" | sha224sum -c
	touch check-zip

austronesian-template.xml: ../template.md
	python ../without_markdown.py austronesian-template.xml

raw_cldf/forms.csv raw_cldf/cognates.csv raw_cldf/cldf-metadata.json: abvd.zip check-zip
	unzip -DD -o -j abvd.zip "abvd-master/cldf/*" -d raw_cldf/

good_languages: raw_cldf/cldf-metadata.json raw_cldf/forms.csv
	python -m lexedata.report.coverage -l --min-concepts 189 --metadata raw_cldf/cldf-metadata.json > high_coverage_languages
	echo "Explicitly exclude Favorlang [831]."
	python -c 'print(*(set(open("high_coverage_languages")) - set(open("bad_languages"))), sep="")' > good_languages


austronesian-undated.xml stats.tex: raw_cldf/cldf-metadata.json good_languages austronesian-template.xml
	cp austronesian-template.xml austronesian-undated.xml
	python -m lexedata.exporter.phylogenetics --stats stats.tex --metadata raw_cldf/cldf-metadata.json -b -o austronesian-undated.xml

austronesian.xml: austronesian-undated.xml add_calibrations.py
	python ../no_nested_sampling.py austronesian-undated.xml -o austronesian.xml
	PYTHONPATH=../ python add_calibrations.py -s --subset good_languages -f aust1307 -o austronesian.xml
  # Old Javanese is a sampled ancestor
	python ../config_sampled_ancestors.py austronesian.xml -s 290 -o austronesian.xml
	python ../set_rho.py austronesian.xml aust1307 -o austronesian.xml

austronesian-burstclock.xml: austronesian.xml ../add_burstclock.py
	python ../add_burstclock.py austronesian.xml -o austronesian-burstclock.xml

austronesian-relaxed.xml: austronesian.xml ../relax_clock.py
	python ../relax_clock.py austronesian.xml -o austronesian-relaxed.xml

austronesian-relaxed-burstclock.xml: austronesian-burstclock.xml ../relax_clock.py
	python ../relax_clock.py austronesian-burstclock.xml -o austronesian-relaxed-burstclock.xml

run/vocabulary.log: austronesian.xml
	mkdir -p run
	cd run && beast ../austronesian.xml

