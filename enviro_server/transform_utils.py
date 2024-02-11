from .EnvironmentData import Units, CHANNELS, Limits

def transform_data(entries, amount):
    if(len(entries) < amount * CHANNELS):
        amount = int(len(entries) / CHANNELS)
    return [__add_datetime(
                {entry.field_name: \
                    __transform_entry({key: value for key, value in entry.to_dict().items() \
                                        if key != "field_name" and key != "ptime"}, entry.field_name) \
                for entry in entries[i*CHANNELS:i*CHANNELS + CHANNELS]}, entries[i*CHANNELS].ptime) \
            for i in range(0, amount)]

def __add_datetime(object, time):
    object['datetime'] = time
    return object

def __transform_entry(entry, key):
    entry['limits'] = Limits[key]
    entry['unit'] = Units[entry['unit'].upper()]
    return entry

def calculate_slices(args, entries_count):
    startSlice = args[0]* CHANNELS
    endSlice = args[1] * CHANNELS
    amount = args[1]
    if(endSlice - startSlice + 1 > entries_count):
        startSlice = 0
        endSlice = entries_count
        amount = int(entries_count / CHANNELS)
    return startSlice, endSlice, amount