import itertools
import struct
import datetime
import collections

def read_byte(f):
    data=f.read(1)
    return int.from_bytes(data,'little')

def read_short(f):
    data=f.read(2)
    return int.from_bytes(data,'little')

def read_int(f):
    data=f.read(4)
    return int.from_bytes(data,'little')

def read_long(f):
    data=f.read(8)
    return int.from_bytes(data,'little')

def read_single(f):
    data=f.read(4)
    return struct.unpack('<f',data)[0]

def read_double(f):
    data=f.read(8)
    return struct.unpack('<d',data)[0]

def read_boolean(f):
    return bool(read_byte(f))

def read_uleb128(f):
    ret=0
    for shift in itertools.count(step=7):
        b=f.read(1)[0]
        ret |= (b & 0x7f) << shift
        if (b & 0x80)==0:
            break
    return ret
    
def read_string(f):
    b=read_byte(f)
    if b==0:
        return None
    
    length=read_uleb128(f)
    return f.read(length).decode()

def read_int_double_pair(f):
    assert read_byte(f)==0x08
    i=read_int(f)
    assert read_byte(f)==0x0d
    d=read_double(f)
    return i,d

def read_int_double_pairs(f):
    ret=[]
    n=read_int(f)
    for _ in range(n):
        ret.append(read_int_double_pair(f))
    return ret

def read_timing_point(f):
    bpm=read_double(f)
    offset=read_double(f)
    regular=read_boolean(f)
    return bpm,offset,regular

def read_timing_points(f):
    ret=[]
    n=read_int(f)
    for _ in range(n):
        ret.append(read_timing_point(f))
    return ret

def read_datetime(f):
    ticks=read_long(f)
    return datetime.datetime(year=1,month=1,day=1,tzinfo=datetime.timezone.utc)\
        + datetime.timedelta(microseconds=ticks*0.1)

Beatmap=collections.namedtuple('Beatmap',
    'artist_name,artist_name_unicode,song_title,song_title_unicode,'
    'creater_name,difficulty,audio_file_name,md5,osu_file_name,'
    'ranked_status,n_hitcircles,n_sliders,n_spinners,last_modification_time,'
    'approach_rate,circle_size,hp_drain,overall_difficulty,slider_velocity,'
    'star_rating_standard,star_rating_taiko,star_rating_ctb,star_rating_mania,'
    'drain_time,total_time,preview_offset,timing_points,'
    'beatmap_id,beatmapset_id,thread_id,'
    'grade_standard,grade_taiko,grade_ctb,grade_mania,local_beatmap_offset,'
    'stack_leniency,mode,song_source,song_tags,online_offset,title_font,'
    'unplayed,last_played,osz2,folder_name,last_checked_against_repository,'
    'ignore_sound,ignore_skin,disable_storyboard,disable_video,'
    'visual_override,mania_scroll_speed')
def read_beatmap(f,version):
    ret={}
    #size=read_int(f)
    ret['artist_name']=read_string(f)
    ret['artist_name_unicode']=read_string(f)
    ret['song_title']=read_string(f)
    ret['song_title_unicode']=read_string(f)
    ret['creater_name']=read_string(f)
    ret['difficulty']=read_string(f)
    ret['audio_file_name']=read_string(f)
    ret['md5']=read_string(f)
    ret['osu_file_name']=read_string(f)
    ret['ranked_status']=read_byte(f)
    ret['n_hitcircles']=read_short(f)
    ret['n_sliders']=read_short(f)
    ret['n_spinners']=read_short(f)
    ret['last_modification_time']=read_datetime(f)
    if version<20140609:
        ret['approach_rate']=read_byte(f)
        ret['circle_size']=read_byte(f)
        ret['hp_drain']=read_byte(f)
        ret['overall_difficulty']=read_byte(f)
    else:
        ret['approach_rate']=read_single(f)
        ret['circle_size']=read_single(f)
        ret['hp_drain']=read_single(f)
        ret['overall_difficulty']=read_single(f)
    ret['slider_velocity']=read_double(f)
    if version>=20140609:
        ret['star_rating_standard']=read_int_double_pairs(f)
        ret['star_rating_taiko']=read_int_double_pairs(f)
        ret['star_rating_ctb']=read_int_double_pairs(f)
        ret['star_rating_mania']=read_int_double_pairs(f)
    ret['drain_time']=datetime.timedelta(seconds=read_int(f))
    ret['total_time']=datetime.timedelta(milliseconds=read_int(f))
    ret['preview_offset']=datetime.timedelta(milliseconds=read_int(f))
    ret['timing_points']=read_timing_points(f)
    ret['beatmap_id']=read_int(f)
    ret['beatmapset_id']=read_int(f)
    ret['thread_id']=read_int(f)
    ret['grade_standard']=read_byte(f)
    ret['grade_taiko']=read_byte(f)
    ret['grade_ctb']=read_byte(f)
    ret['grade_mania']=read_byte(f)
    ret['local_beatmap_offset']=read_short(f)
    ret['stack_leniency']=read_single(f)
    ret['mode']=read_byte(f)
    ret['song_source']=read_string(f)
    ret['song_tags']=read_string(f)
    ret['online_offset']=read_short(f)
    ret['title_font']=read_string(f)
    ret['unplayed']=read_boolean(f)
    ret['last_played']=read_datetime(f)
    ret['osz2']=read_boolean(f)
    ret['folder_name']=read_string(f)
    ret['last_checked_against_repository']=read_datetime(f)
    ret['ignore_sound']=read_boolean(f)
    ret['ignore_skin']=read_boolean(f)
    ret['disable_storyboard']=read_boolean(f)
    ret['disable_video']=read_boolean(f)
    ret['visual_override']=read_boolean(f)
    if version<20140609:
        read_short(f)
    read_int(f)
    ret['mania_scroll_speed']=read_byte(f)

    print(ret['beatmapset_id'])

    return Beatmap(**ret)

OsuDb=collections.namedtuple('OsuDb',
    'version,foler_count,account_unlocked,date_unlocked,player_name,beatmaps')
def read_osudb(f):
    version=read_int(f)
    folder_count=read_int(f)
    account_unlocked=read_boolean(f)
    date_unlocked=read_datetime(f)
    player_name=read_string(f)
    n_beatmaps=read_int(f)
    beatmaps=[]
    for _ in range(n_beatmaps):
        beatmaps.append(read_beatmap(f,version))
    unkown=read_int(f)

    return OsuDb(version,folder_count,account_unlocked,
        date_unlocked,player_name,beatmaps)

# For debugging
if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as f:
        read_osudb(f)
