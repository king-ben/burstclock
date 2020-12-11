from calibrations import main, normal, until

r = main(
    [
        # (a) 5,000 B.P. or older for Bantoid, non-Bantu (58);
        {
            "glottolog_clade": "bant1294",
            "languages": {
                "aghemgrassfields",
                "njengrassfields",
                "mbulajarawan",
                "bamungrassfields",
                "fefegrassfields",
                "okugrassfields",
                "dugurijarawan",
                "moghamograssfields",
                "bwazzajarawan",
                "komgrassfields",
                "bilejarawan",
                "kulungjarawan",
                "mungakagrassfields",
                "zaambojarawan",
                "tivtivoid",
            },
            "d": {"tag": "Uniform", "name": "distr", "lower": "5000", "upper": "20000"},
        },

        # (b) 4,000–5,000 B.P. for Narrow Bantu (13, 14, 16, 44, 59, 60);
        {"glottolog_clade": "narr1281", "d": until(4000, 5000)},

        # (c) 3,000–3,500 B.P. for the Mbam-Bubi ancestor (61); The Mbam
        # languages [mbam1252] are a61ngoroasom, a61ngorolunda, a62bmmala,
        # a622nugunu, a46nomaande, a601tuki, a44tunen, a45nyokon, a462yambeta,
        # a621nubaca, a62anuasue, a62clibie, a62anukalonge, a61ngorobisoo; Bubi
        # [bubi1242] of Bioko is a31bubi in the dataset. I will keep this in,
        # although I don't see how Lavachery P (2003): “A la lisière de la
        # forêt” [Peuplements Anciens et Actuels des Forêts Tropicales, eds
        # Froment A, Guffroy J (IRD Editions, Paris), pp 89–102] is a reference
        # for a split date between 3000 and 3500. As far as I can see,
        # Lavachery only states that stone bifaces similar to those dated to
        # 3000 to 6000 BP have been in use by the Bubi on Bioko turn of the
        # (20th) century. I only checked the reference to see which Bubi this
        # refers to, and I don't consider myself competent in judging
        # calibrations as valid or invalid.
        {
            "languages": {
                "a61ngoroasom",
                "a61ngorolunda",
                "a62bmmala",
                "a622nugunu",
                "a46nomaande",
                "a601tuki",
                "a44tunen",
                "a45nyokon",
                "a462yambeta",
                "a621nubaca",
                "a62anuasue",
                "a62clibie",
                "a62anukalonge",
                "a61ngorobisoo",
                "a31bubi",
            },
            "d": until(3000, 3500),
        },

        # (d) 2,500 B.P. for Eastern Bantu (62).
        {"glottolog_clade": "east2731", "d": normal(2500, 50)},
    ]
)
