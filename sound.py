from pydub import AudioSegment

# Load sounds
ping_small = AudioSegment.from_wav("sfx/bounce.wav")
ping_big = AudioSegment.from_wav("sfx/wall_break.wav")
win_sound = AudioSegment.from_wav("sfx/win.wav")

# Map event types to sounds
sound_map = {
    "bounce": ping_small,
    "wall_break": ping_big,
    "win": win_sound,
}

# Parse sound_logs.txt and convert frame number to milliseconds
events = []
with open("sound_logs.txt", "r") as f:
    for line in f:
        if not line.strip():
            continue
        event_type, frame_str = line.strip().split('\t')
        frame = int(frame_str)
        timestamp_ms = int(frame * 1000 / 60)  # convert to milliseconds
        if event_type in sound_map:
            events.append((timestamp_ms, event_type))

# Determine total length needed
last_timestamp = max(t for t, _ in events)
max_sound_duration = max(len(s) for s in sound_map.values())
total_duration = last_timestamp + max_sound_duration + 500

# Create silent base track
track = AudioSegment.silent(duration=total_duration)

# Overlay sounds
for timestamp, event_type in events:
    track = track.overlay(sound_map[event_type], position=timestamp)

# Export to file
track.export("final_audio.wav", format="wav")
