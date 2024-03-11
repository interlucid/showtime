import importlib
import math
import random
import time

import config


def get_now_millis():
    return round(time.time() * 1000)


def get_measure_ms(bpm):
    return 60 * 1000 / (bpm / 4)


def get_sequence_module(song_name):
    sequence_module = importlib.import_module(f"sequences.{song_name}")
    return sequence_module


def get_song_timing_constants(song_measure_ms):
    song_timing_constants = {}
    song_timing_constants["song_measure_ms"] = song_measure_ms
    song_timing_constants["song_double_measure_ms"] = song_measure_ms * 2
    song_timing_constants["song_half_measure_ms"] = song_measure_ms / 2
    # 4 beats per measure
    song_timing_constants["song_beat_ms"] = song_measure_ms / 4
    song_timing_constants["song_half_beat_ms"] = song_measure_ms / 8
    song_timing_constants["song_quarter_beat_ms"] = song_measure_ms / 16
    return song_timing_constants


# do some general calculations that will be reused every time the loop is run
def get_current_song_playback_timing(playback_start_time: int, song_measure_ms=None):
    current_song_playback_timing = {}
    # get the milliseconds since the song was started vs. now
    ms_since_song_start = get_now_millis() - playback_start_time
    current_song_playback_timing["ms_since_song_start"] = ms_since_song_start
    if not song_measure_ms:
        return current_song_playback_timing

    song_timing_constants = get_song_timing_constants(song_measure_ms)
    # at the moment animations are done by measure so get the milliseconds since the start of the measure
    # this is equal to the milliseconds elapsed modulo the milliseconds in one measure
    current_song_playback_timing["ms_since_double_measure_start"] = (
        ms_since_song_start % song_timing_constants["song_double_measure_ms"]
    )
    current_song_playback_timing["ms_since_measure_start"] = (
        ms_since_song_start % song_measure_ms
    )
    current_song_playback_timing["ms_since_half_measure_start"] = (
        ms_since_song_start % song_timing_constants["song_half_measure_ms"]
    )
    current_song_playback_timing["ms_since_beat_start"] = (
        ms_since_song_start % song_timing_constants["song_beat_ms"]
    )
    current_song_playback_timing["ms_since_half_beat_start"] = (
        ms_since_song_start % song_timing_constants["song_half_beat_ms"]
    )
    current_song_playback_timing["ms_since_quarter_beat_start"] = (
        ms_since_song_start % song_timing_constants["song_quarter_beat_ms"]
    )

    # figure out which measure we're in
    current_song_playback_timing["current_measure"] = math.trunc(
        ms_since_song_start / song_measure_ms
    )
    current_song_playback_timing["current_double_measure"] = math.trunc(
        ms_since_song_start / song_timing_constants["song_double_measure_ms"]
    )
    current_song_playback_timing["current_half_measure"] = math.trunc(
        ms_since_song_start / song_timing_constants["song_half_measure_ms"]
    )
    current_song_playback_timing["current_beat"] = math.trunc(
        ms_since_song_start / song_timing_constants["song_beat_ms"]
    )
    current_song_playback_timing["current_half_beat"] = math.trunc(
        ms_since_song_start / song_timing_constants["song_half_beat_ms"]
    )
    current_song_playback_timing["current_quarter_beat"] = math.trunc(
        ms_since_song_start / song_timing_constants["song_quarter_beat_ms"]
    )
    return current_song_playback_timing


# we're gonna have a bunch of properties to pass around so wrap them in an object
def get_sequence_config(song, pixels, song_timing=None):
    sequence_config = {}
    sequence_config["song"] = song
    sequence_config["song_timing"] = song_timing
    sequence_config["pixels"] = pixels
    return sequence_config


def get_pattern_config(
    pattern_segment_ms,
    num_fade_segments,
    num_pattern_segments,
    num_sectors,
    pattern_offset,
):
    pattern_config = {}
    # how long one segment of the pattern will last in milliseconds
    pattern_config["pattern_segment_ms"] = pattern_segment_ms
    # how many segments a particular animation will last for that segment (2 for a fade means the whole fade animation takes up 2 segments of time)
    pattern_config["num_fade_segments"] = num_fade_segments
    # the number of available time slots for the pattern to last
    pattern_config["num_pattern_segments"] = num_pattern_segments
    # this is kind of tricky, it's basically how far apart each pattern instance is from the next in integers
    # it's usually 1 but can be other numbers like in Dream Killa which needs to use smaller patterns
    # and the final pattern is offset by half its length
    pattern_config["pattern_offset"] = pattern_offset
    # the number of sectors of the light strip that can be lit up
    pattern_config["num_sectors"] = num_sectors
    # the amount of milliseconds a whole pattern will take
    pattern_config["pattern_ms"] = pattern_segment_ms * num_pattern_segments
    return pattern_config


def get_pattern_timing(sequence_config, pattern_config):
    pattern_timing = {}
    # basic amount of time since the pattern start; doesn't account for offsets smaller than the pattern length
    pattern_timing["basic_ms_since_pattern_duration_start"] = (
        sequence_config["song"]["ms_since_song_start"] % pattern_config["pattern_ms"]
    )
    pattern_timing["current_pattern_instance"] = math.trunc(
        sequence_config["song"]["ms_since_song_start"] / pattern_config["pattern_ms"]
    )
    return pattern_timing


def flatten(list):
    return [item for sublist in list for item in sublist]


def get_rainbow_loop_color(position):
    # input a value 0 to 255 to get a color value.
    # the colours are a transition r - g - b - back to r.
    if position < 0 or position > 255:
        r = g = b = 0
    elif position < 85:
        r = int(position * 3)
        g = int(255 - position * 3)
        b = 0
    elif position < 170:
        position -= 85
        r = int(255 - position * 3)
        g = 0
        b = int(position * 3)
    else:
        position -= 170
        r = 0
        g = int(position * 3)
        b = int(255 - position * 3)
    return (r, g, b)


def fill_average(pixels, color):
    for pindex, pixel in enumerate(pixels):
        pixels[pindex] = tuple([round((x + y) / 2) for x, y in zip(*[pixel, color])])


# size is the number of additional pixels (radius)
def fill_pixels_in_range(
    pixels, starting_pixel, ending_pixel, color, size=1, hardness=1, add=False
):
    num_pixels = len(pixels)
    # if starting_ignore_pixel == math.inf:
    #     starting_ignore_pixel = num_pixels
    original_size = ending_pixel - starting_pixel
    # this has out of bounds protection
    sized_starting_pixel = max(starting_pixel - round(original_size * abs(1 - size)), 0)
    sized_ending_pixel = min(
        ending_pixel + round(original_size * abs(1 - size)), num_pixels - 1
    )
    middle_pixel = (starting_pixel + ending_pixel) / 2
    radius = max(middle_pixel - sized_starting_pixel, 1)
    for pixel_index in range(sized_starting_pixel, sized_ending_pixel):
        # get this pixel's color strength
        color_strength = (1 - (abs(middle_pixel - pixel_index) / radius)) ** (
            # this multiplier may make some pixels be off instead of a value at lower light levels
            # but at higher levels it should be fine
            1.5
            * (1 - hardness)
        )
        new_pixel = tuple(map(lambda x: round(color_strength * x), color))
        # print(new_pixel)
        if add:
            new_pixel = tuple(
                [int(min(sum(x), 255)) for x in zip(*[new_pixel, pixels[pixel_index]])]
            )
        pixels[pixel_index] = new_pixel


# given coordinates as if lighting up the whole strip:
#   - reduce the size of the animation to half its size
#   - reflect the animation across the center
def fill_pixels_in_center_split_mirror_range(
    pixels,
    starting_pixel,
    ending_pixel,
    color,
    size=1,
    hardness=1,
    add=False,
):
    num_pixels = len(pixels)
    strip_middle_pixel = math.trunc(num_pixels / 2)
    half_starting_pixel = max(math.trunc(starting_pixel / 2), 0)
    half_ending_pixel = min(math.trunc(ending_pixel / 2), strip_middle_pixel)
    fill_pixels_in_range(
        pixels,
        half_starting_pixel,
        half_ending_pixel,
        color,
        size,
        hardness,
        add,
    )
    fill_pixels_in_range(
        pixels,
        num_pixels - half_ending_pixel,
        num_pixels - half_starting_pixel,
        color,
        size,
        hardness,
        add,
    )


# for stuff like the dyoo in Dream Killa and all of Unlimited
def get_exponential_dropoff(x):
    return round((config.num_pixels - 1) * (-(x ** (2 / 5)) + 1))


# ease in and out (for the woo in Your Dream)
def get_parametric_blend(x):
    return x**2 / (2 * (x**2 - x) + 1)


# amount should be 1 or greater
# modified from https://stackoverflow.com/a/61746605/4561047
# needed to multiply x by 2 to fit within 1 x 1 transformation
# def get_ease_in_out(x, amount):
#     return (2 * x) ** amount / ((2 * x) ** amount + (1 / (2 * x) ** amount))


def get_sector_starting_pixel(sector, num_sectors):
    return math.trunc(sector * config.num_pixels / num_sectors)


def get_sector_ending_pixel(sector, num_sectors):
    return math.trunc((sector + 1) * config.num_pixels / num_sectors)


def get_fade_in_color(ms_since_fade_start, increment_ms, base_color):
    return [
        round(color_part * (ms_since_fade_start / increment_ms))
        for color_part in base_color
    ]


def get_fade_out_color(ms_since_fade_start, increment_ms, base_color):
    return [
        round(color_part * (1 - ms_since_fade_start / increment_ms))
        for color_part in base_color
    ]


def get_fade_in_out_color(ms_since_fade_start, increment_ms, base_color):
    if ms_since_fade_start < 0 or ms_since_fade_start > increment_ms:
        print(
            "get_fade_in_out_color returning black since increment is out of range",
            flush=True,
        )
        return (0, 0, 0)
    return tuple(
        map(
            lambda color_part: math.trunc(
                color_part * (-abs(2 * ms_since_fade_start / increment_ms - 1) + 1)
            ),
            base_color,
        )
    )


# we need a new key for every time the animation repeats
def get_pixel_key(song, pattern_timing):
    return pattern_timing["current_pattern_instance"]


def basic_populate_pixel_key(
    sequence_config,
    pattern_config,
    pattern_interval_pixel_locations,
    pattern_intervals,
    get_pattern_timing=get_pattern_timing,
):
    pattern_timing = get_pattern_timing(sequence_config, pattern_config)
    pixel_key = pattern_timing["current_pattern_instance"]
    pattern_offset = pattern_config["pattern_offset"]
    # only generate a new location for the light if the current interval has changed
    if pixel_key not in pattern_interval_pixel_locations:
        pattern_interval_pixel_locations[pixel_key] = generate_random_pattern(
            pattern_config
        )
    if (
        pixel_key - pattern_offset not in pattern_interval_pixel_locations
        # only generate the previous notes if they are also part of the loop
        and pattern_timing["current_pattern_instance"] - pattern_offset
        in pattern_intervals
    ):
        pattern_interval_pixel_locations[pixel_key - pattern_offset] = (
            generate_random_pattern(pattern_config)
        )


def generate_random_pattern(pattern_config, repeat_count=1):
    num_sectors = pattern_config["num_sectors"]
    return flatten(
        [
            # this one-liner returns a list that is num_sectors long with unique values
            random.sample(list(range(num_sectors)), num_sectors)
            # why is this 5? magic number 👀 but it was only used in Dream Killa when I discovered this
            for repeat in list(range(repeat_count))
        ]
    )


# there are three main times to consider:
# - duration of the fade
# - duration of the pattern repeat interval (how long before the pattern repeats)
# - pattern spacing duration (the time by which the pattern offsets are measured)
def fill_staggered_fade_in_out(
    sequence_config,
    pattern_config,
    pixel_locations,
    # this is the milliseconds since the start of the duration
    # normalized because the fade might be offset in different parts of the song (see pattern_start_segment as well)
    normalized_ms_since_pattern_duration_start,
    base_color,
    pattern_start_segment,
    # use the default pixel key getter unless there's a weird thing like the pattern is offset in a weird way
    get_pixel_key=get_pixel_key,
    # this is an optional offset if the repeat pattern starts at a time that's offset by a fraction of its duration
    # for example if a measure long pattern starts half a measure late, this will be non-zero
    # this is how far away the previous pattern is in the pixel locations
    pixel_key_offset=1,
    get_color=get_fade_in_out_color,
):
    song = sequence_config["song"]
    pattern_timing = get_pattern_timing(sequence_config, pattern_config)
    pixel_key = get_pixel_key(song, pattern_timing)
    pattern_segment_ms = pattern_config["pattern_segment_ms"]
    num_fade_segments = pattern_config["num_fade_segments"]
    num_pattern_segments = pattern_config["num_pattern_segments"]
    fade_duration = pattern_segment_ms * num_fade_segments

    # figure out what section of the repeated pattern we're in right now
    current_pattern_segment = math.trunc(
        normalized_ms_since_pattern_duration_start / pattern_segment_ms
    )
    # if the animation start interval of this fade duration is more than the offset, use this fade duration's position
    # otherwise, use the position of the previous fade duration
    repeat_offset = (
        0 if current_pattern_segment >= pattern_start_segment else pixel_key_offset
    )

    # print(
    #     f"cm: {song['current_measure']}, pl: {pixel_key - repeat_offset}, pss: {pattern_start_segment}",
    #     flush=True,
    # )
    # we may need to access the previous interval's data if there is an offset
    # just don't run this if there is nothing in the previous interval
    # the previous interval may intentionally be left empty if this is the first instance of a repeated pattern
    if pixel_key - repeat_offset not in pixel_locations:
        if normalized_ms_since_pattern_duration_start % 10 == 0:
            print(
                f"no data available in previous location ({pixel_key - repeat_offset}) relative to {pixel_key}",
                flush=True,
            )
        return

    # get the pixels
    # use the pixel key which is for the current pattern repeat duration
    # unless there is a pattern repeat duration offset, which will get it from two pattern repeat durations ago
    # there are multiple pixel locations on each entry, so get the one that corresponds to this offset
    # print(
    #     f"cm: {song['current_measure']}, pl at {pixel_key - repeat_offset}: {pixel_locations[pixel_key - repeat_offset]}, pss: {pattern_start_segment}",
    #     flush=True,
    # )
    cur_fade_sector = pixel_locations[pixel_key - repeat_offset][pattern_start_segment]
    starting_fade_pixel = get_sector_starting_pixel(
        cur_fade_sector, pattern_config["num_sectors"]
    )
    ending_fade_pixel = get_sector_ending_pixel(
        cur_fade_sector, pattern_config["num_sectors"]
    )
    # print(f"start: {starting_fade_pixel}, end: {ending_fade_pixel}", flush=True)
    # cur_beat_ending_fade_pixel = (
    #     pixel_locations[pixel_key - repeat_offset][pattern_start_segment] + 1
    # )

    # if math.trunc(normalized_ms_since_pattern_duration_start) % 10 == 0:
    #     print(
    #         f"cps: {current_pattern_segment}, cond 1: { current_pattern_segment < pattern_start_segment and num_pattern_segments - pattern_start_segment > num_fade_segments}, cond 2: {pattern_start_segment + num_fade_segments > num_pattern_segments and current_pattern_segment >= (pattern_start_segment + num_fade_segments) - num_pattern_segments and current_pattern_segment < pattern_start_segment}, cond 3: {current_pattern_segment >= pattern_start_segment + num_fade_segments}",
    #         flush=True,
    #     )

    # print(f"play for measure {song['current_measure']}?", flush=True)
    if (
        # don't play if the current segment hasn't reached where the pattern starts
        current_pattern_segment < pattern_start_segment
        # this only matters if the pattern can't wrap that far
        and num_pattern_segments - pattern_start_segment > num_fade_segments
        # don't play if the pattern is so long it wraps around to the current segment
        # check if the offset and the animation is longer than the entire segment we have (which means it will wrap)
        or pattern_start_segment + num_fade_segments > num_pattern_segments
        # if the pattern wraps, don't play if the current segment is bigger than the farthest the pattern can wrap
        and current_pattern_segment
        >= (pattern_start_segment + num_fade_segments) - num_pattern_segments
        # but it's ok if we run into the original pattern again
        and current_pattern_segment < pattern_start_segment
        or
        # don't play if the current segment has passed the point where the pattern ends
        current_pattern_segment >= pattern_start_segment + num_fade_segments
        # don't play if this particular segment ended its cycle in the previous instance of the pattern
        or current_pattern_segment + pattern_start_segment + num_fade_segments
        < num_pattern_segments
        and repeat_offset != 0
    ):
        return

    # print(
    #     f"cps: {current_pattern_segment}, pss: {pattern_start_segment}, nfm: {num_fade_segments}, nps: {num_pattern_segments}, ro: {repeat_offset}",
    #     flush=True,
    # )
    ms_since_fade_start = (
        normalized_ms_since_pattern_duration_start
        - (pattern_start_segment * pattern_segment_ms)
    ) % fade_duration

    # if math.trunc(normalized_ms_since_pattern_duration_start) % 10 == 0:
    #     print(
    #         f"cps: {current_pattern_segment}, nmspds: {math.trunc(normalized_ms_since_pattern_duration_start)}, cbsdp: {math.trunc(cur_beat_starting_fade_pixel)}, msis: {math.trunc(ms_since_fade_start)}, pl: {pixel_locations[pixel_key][pattern_start_segment]}, ppl: {pixel_locations[pixel_key - pixel_key_offset][pattern_start_segment]}",
    #         flush=True,
    #     )
    #     print(pixel_locations[pixel_key][pattern_start_segment], flush=True)
    #     print(
    #         pixel_locations[pixel_key - pixel_key_offset][pattern_start_segment],
    #         flush=True,
    #     )
    # print(
    #     f"normalized_ms_since_pattern_duration_start: {normalized_ms_since_pattern_duration_start}",
    #     flush=True,
    # )
    # print(f"ms_since_fade_start: {ms_since_fade_start}", flush=True)

    # fade in and out the selected color
    cur_color = get_fade_in_out_color(
        # calculate the stage of the animation - should be an increment of a half measure starting from
        # the beat that this animation started
        ms_since_fade_start,
        fade_duration,
        base_color,
    )

    # print(
    #     f"pl at {pixel_key - repeat_offset}, pss: {pattern_start_segment}, pl[pk-ro][pss]: {pixel_locations[pixel_key - repeat_offset][pattern_start_segment]}, cc: {cur_color}",
    #     flush=True,
    # )
    # print(cur_color, flush=True)
    # # print(f"cur_color: {cur_color}", flush=True)
    # cur_color = (250, 20, 255)

    fill_pixels_in_range(
        sequence_config["pixels"],
        starting_fade_pixel,
        ending_fade_pixel,
        cur_color,
    )


# a generalized function to expand types of animations
# arbitrary_start_time_block: the starting block of the animation, like 5 half beats or 3 measures
# pattern: an array of intervals between the start of the block and each instance of the animation, like [0, 4, 12] for wahs
def expand_animation_pattern(arbitrary_start_time_block: int, pattern: [int]):
    animation_time_blocks = list(
        map(lambda offset: offset + arbitrary_start_time_block, pattern)
    )
    return animation_time_blocks
