
#LArSoft Channels name: 1010 = C1_1, 1011 = C1_2, 2010 = M1_1, 2011 = M1_2
ALL_CHANNELS = [ 1010, 1011, 1020, 1021, 1030, 1031, 1040, 1041, 1050, 1051, 1060, 1061, 1070, 1071, 1080, 1081, 2010, 2011, 2020, 2021, 2030, 2031, 2040, 2041, 2050, 2051, 2060, 2061, 2070, 2071, 2080, 2081 ]

CAT_CHANNELS = ["C1_1", "C1_2", "C2_1", "C2_2", "C3_1", "C3_2", "C4_1", "C4_2", "C5_1", "C5_2", "C6_1", "C6_2", "C7_1", "C7_2", "C8_1", "C8_2"]  
MEM_CHANNELS = ["M1_1", "M1_2", "M2_1", "M2_2", "M3_1", "M3_2", "M4_1", "M4_2", "M5_1", "M5_2", "M6_1", "M6_2", "M7_1", "M7_2", "M8_1", "M8_2"]
CHANNELS = CAT_CHANNELS + MEM_CHANNELS

CAT_MODULES = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]  
#MEM_MODULES = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"]  
MEM_MODULES = ["M5", "M6", "M7", "M8"]  
MODULES = CAT_MODULES + MEM_MODULES
INVALID_MODULES = ["M1", "M2", "M3", "M4"]

def GetValidModules():
    return [m for m in MODULES if m not in INVALID_MODULES]

CHANNEL_TYPES = {
    1: "C",  
    2: "M",  
}


def channel_label(opchannel):
    opchannel = int(opchannel)
    dettype = opchannel // 1000
    modulo = opchannel % 1000
    group = modulo // 10
    ch = modulo % 10

    prefix = CHANNEL_TYPES.get(dettype, f"T{dettype}")
    return f"{prefix}{group}_{ch + 1}"


"""Mapping of module names to their coordinates inside NP02 using LArSoft geometry. The coordinates are given as (x, y, z) tuples."""
def module_mapping():
    coord = {"C1": (0, 285, 180), 
             "C2": (0, 120, 255), 
             "C3": (0, 45, 110),
             "C4": (0, 210, 30), 
             "C5": (0, -45, 180), 
             "C6": (0, -215, 255), 
             "C7": (0, -215, 110), 
             "C8": (0, -125, 30),
             "M1": (305, 420, 150), 
             "M2": (230, 420, 150), 
             "M3": (305, -420, 150), 
             "M4": (230, -420, 150), 
             "M5": (-200, 420, 150), 
             "M6": (-280, 420, 150), 
             "M7": (-200, -420, 150), 
             "M8": (-280, -420, 150), 
             } 
    return coord
