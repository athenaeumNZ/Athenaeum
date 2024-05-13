import librosa



def update_bpm_from_audio(instance):
    if instance.audio:
        audio_path = instance.audio.path
        try:
            # Load audio file
            y, sr = librosa.load(audio_path)
            
            # Calculate BPM
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Update instance's BPM field
            instance.bpm = int(tempo)
            instance.save()
        except Exception as e:
            # Handle any errors that may occur during the analysis
            print(f"Error analyzing BPM for {instance}: {e}")

def vinyl_releases_average_tracks_per_side_util(vinyl_releases):
    for i in vinyl_releases:
        plate_count = int(i.plate_count)  # Convert plate_count to integer
        from musicDatabase.models import VinylPlate, VinylTrack
        vinyl_plates = VinylPlate.objects.filter(related_release=i)
        vinyl_tracks_count = len(VinylTrack.objects.filter(related_vinyl_plate__in=vinyl_plates))
        average_tracks_per_side = round(vinyl_tracks_count / plate_count / 2, 1)
        if average_tracks_per_side <= 2:
            i.average_tracks_per_side_is_above_2 = False
        else:
            i.average_tracks_per_side_is_above_2 = True

        integer_part = int(average_tracks_per_side)
        decimal_part = average_tracks_per_side - integer_part
        if decimal_part == 0:
            i.average_tracks_per_side = str(integer_part)
        else:
            i.average_tracks_per_side = str(average_tracks_per_side)

        # Save changes outside of the if-else blocks
        i.save()
        
    return vinyl_releases

def vinyl_release_average_tracks_per_side_util(vinyl_release):
    plate_count = int(vinyl_release.plate_count)  # Convert plate_count to integer
    from musicDatabase.models import VinylPlate, VinylTrack
    vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
    vinyl_tracks_count = len(VinylTrack.objects.filter(related_vinyl_plate__in=vinyl_plates))
    average_tracks_per_side = round(vinyl_tracks_count / plate_count / 2, 1)
    if average_tracks_per_side <= 2:
        vinyl_release.average_tracks_per_side_is_above_2 = False
    else:
        vinyl_release.average_tracks_per_side_is_above_2 = True

    integer_part = int(average_tracks_per_side)
    decimal_part = average_tracks_per_side - integer_part
    if decimal_part == 0:
        vinyl_release.average_tracks_per_side = str(integer_part)
    else:
        vinyl_release.average_tracks_per_side = str(average_tracks_per_side)

    # Save changes
    vinyl_release.save()
    return vinyl_release
'''
test_bpm_creation_release = VinylRelease.objects.get(catalog_number__contains='117005')
test_bpm_creation_plates = VinylPlate.objects.filter(related_release=test_bpm_creation_release)
test_bpm_creation_tracks = VinylTrack.objects.filter(related_vinyl_plate__in=test_bpm_creation_plates)
for i in test_bpm_creation_tracks:
    i.analyze_bpm()
'''
