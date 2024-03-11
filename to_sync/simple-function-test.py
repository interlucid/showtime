import pprint

pp = pprint.PrettyPrinter(indent=4)


def expand_wah_uh_ooh_uh_half_measure(half_measure, num_wahs):
    starting_wah_half_beat = half_measure * 4
    return list(
        map(lambda offset: offset + starting_wah_half_beat, list(range(num_wahs)))
    )


print(expand_wah_uh_ooh_uh_half_measure(7, 4))
