LANGUAGE_SAMPLES = all half 3quarter biggest

indoeuropean.nex:
	curl https://raw.githubusercontent.com/PhyloStar/ie-phylo-exps/a63c0b52f7772adc2341572932a74b23d92570df/medium1.nex -o indoeuropean.nex

indoeuropean.zip:
	curl https://muse.jhu.edu/article/576999/file/supp02.zip -o indoeuropean.zip

check-zip: indoeuropean.zip indoeuropean.nex
	echo "2c04d51bc1b800715fbd8342771faae8e08b7c7d07cc554819989e74  indoeuropean.zip" | sha224sum -c
	echo "59451dbfcdb949ba8d8a42c74d9f70f629b35027a08323393bf3b415  indoeuropean.nex" | sha224sum -c
	touch check-zip

raw_cldf/ielex-130421-ag-cc.txt: indoeuropean.zip check-zip
	unzip -DD -o -j indoeuropean.zip "sup/ielex-130421-ag-cc.txt" -d raw_cldf/

raw_cldf/ielex-130421-ag-cc-with-concept.tsv: raw_cldf/ielex-130421-ag-cc.txt
	 python add_singleton_cognate_sets.py raw_cldf/ielex-130421-ag-cc.txt | grep -v 22842 > raw_cldf/ielex-130421-ag-cc-with-concept.tsv

indoeuropean-template.xml: ../template.md
	python ../without_markdown.py indoeuropean-template.xml

all: indoeuropean.nex
	echo "Mapping according to Chang et al. (2015), Table 8"
	echo "Language" > all
	grep 01 indoeuropean.nex | cut -d ' ' -f 1 \
	  | sed -e 's/^Adapazar$$/Armenian_List/' \
	  | sed -e 's/^Arvanitika$$/Albanian_K/' \
	  | sed -e 's/^Belarusian$$/Byelorussian/' \
	  | sed -e 's/^Breton$$/Breton_ST/' \
	  | sed -e 's/^Cagliari$$/Sardinian_C/' \
	  | sed -e 's/^Dutch$$/Dutch_List/' \
	  | sed -e 's/^Eastern_Armenian$$/Armenian_Mod/' \
	  | sed -e 's/^Icelandic$$/Icelandic_ST/' \
	  | sed -e 's/^Irish$$/Irish_B/' \
	  | sed -e 's/^Lithuanian$$/Lithuanian_ST/' \
	  | sed -e 's/^Modern_Greek$$/Greek_Mod/' \
	  | sed -e 's/^Nuorese$$/Sardinian_N/' \
	  | sed -e 's/^Old_Church_Slavic$$/Old_Church_Slavonic/' \
	  | sed -e 's/^Old_Irish_B$$/Old_Irish/' \
	  | sed -e 's/^Old_West_Norse$$/Old_Norse/' \
	  | sed -e 's/^Panjabi$$/Panjabi_ST/' \
	  | sed -e 's/^Portuguese$$/Portuguese_ST/' \
	  | sed -e 's/^Romani$$/Gypsy_Gk/' \
	  | sed -e 's/^Romanian$$/Rumanian_List/' \
	  | sed -e 's/^Swiss_German$$/Schwyzerdutsch/' \
	  | sed -e 's/^Tajik$$/Tadzik/' \
	  | sed -e 's/^Tosk$$/Albanian_Top/' \
	  | sed -e 's/^Welsh$$/Welsh_N/' \
	| sort >> all

indoeuropean-%-undated.xml: % indoeuropean-template.xml raw_cldf/ielex-130421-ag-cc-with-concept.tsv raw_cldf/cldf-metadata.json
	cp indoeuropean-template.xml $@
	python -m lexedata.exporter.phylogenetics --stats stats-$<.tex --metadata raw_cldf/cldf-metadata.json -b -o $@ --languages $<

indoeuropean-%.xml: % indoeuropean-%-undated.xml add_%_calibrations.py
	python ../no_nested_sampling.py indoeuropean-$<-undated.xml -o $@
	echo "Language" > actually_included_$<_languages
	PYTHONPATH=../ python add_$<_calibrations.py -w 4000. -s -o $@ --subset $< | sort >> actually_included_$<_languages
	python ../config_sampled_ancestors.py $@ Latin Vedic_Sanskrit Avestan Ancient_Greek Old_Church_Slavonic -s Old_Irish -s Old_Norse -s Old_English -s Old_High_German -s Classical_Armenian -o $@
	python ../set_rho.py $@ indo1319 -o $@
	diff $< actually_included_$<_languages

indoeuropean-%-burstclock.xml: indoeuropean-%.xml ../add_burstclock.py
	python ../add_burstclock.py $< -o $@

indoeuropean-%-relaxed.xml: indoeuropean-%.xml ../relax_clock.py
	python ../relax_clock.py $< -o $@

indoeuropean-%-relaxed-burstclock.xml: indoeuropean-%-burstclock.xml ../relax_clock.py
	python ../relax_clock.py $< -o $@

run/vocabulary.log: indoeuropean-all.xml
	mkdir -p run
	cd run && beast ../indoeuropean-all.xml

half: all
	echo "Language" > half
	tail -n +1 $< | shuf --random-source=$< | tail -n 41 | sort >> half

3quarter: all
	echo "Language" > 3quarter
	tail -n +1 $< | shuf --random-source=$< | tail -n 61 | sort >> 3quarter
