from calibrations import main, normal, until

r = main(
    [
        # (a) 5,000 B.P. or older for Bantoid, non-Bantu (58);
        {"glottolog_clade": "bant1294", "languages": {"aghemgrassfields", "njengrassfields", "mbulajarawan", "bamungrassfields", "fefegrassfields", "okugrassfields", "dugurijarawan", "moghamograssfields", "bwazzajarawan", "komgrassfields", "bilejarawan", "kulungjarawan", "mungakagrassfields", "zaambojarawan", "tivtivoid"}, "d": {'tag': 'Uniform', 'name': "distr", 'lower': '5000', 'upper': '20000'}},
        # (b) 4,000–5,000 B.P. for Narrow Bantu (13, 14, 16, 44, 59, 60);
        {"glottolog_clade": "narr1281", "d": until(4000, 5000)},
        # (c) 3,000–3,500 B.P. for the Mbam-Bubi ancestor (61);
        # The Mbam languages [mbam1252] are a61ngoroasom, a61ngorolunda,
        # a62bmmala, a622nugunu, a46nomaande, a601tuki, a44tunen, a45nyokon,
        # a462yambeta, a621nubaca, a62anuasue, a62clibie, a62anukalonge,
        # a61ngorobisoo; Bubi [bubi1250] is b305vove in the dataset.
        {"languages": {"a61ngoroasom", "a61ngorolunda", "a62bmmala", "a622nugunu", "a46nomaande", "a601tuki", "a44tunen", "a45nyokon", "a462yambeta", "a621nubaca", "a62anuasue", "a62clibie", "a62anukalonge", "a61ngorobisoo", "b305vove"}, "d": until(3000, 3500)},
        # (d) 2,500 B.P. for Eastern Bantu (62).
        {"glottolog_clade": "east2731", "d": normal(2500, 50)},
    ]
)
