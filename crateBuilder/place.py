if display_searched_releases == 'display_searched_releases_plates':
    #region display_searched_releases
        vinyl_releases = VinylRelease.objects.all()
        #region filter releases
        if request.POST['search_artist'] != None:
            search_artist = request.POST['search_artist']
            vinyl_releases = vinyl_releases.filter(artist=search_artist)
        if request.POST['search_title'] != None:
            search_title = request.POST['search_title']
            vinyl_releases = vinyl_releases.filter(release_title=search_title)
        if request.POST['search_label'] != None:
            search_label = request.POST['search_label']
            vinyl_releases = vinyl_releases.filter(label=search_label)
        if request.POST['search_catalog'] != None:
            search_catalog = request.POST['search_catalog']
            vinyl_releases = vinyl_releases.filter(catalog_number=search_catalog)
        #endregion
        #region vinyl_plates
        external_releases_ids = vinyl_releases.values_list('id')
        for i in external_releases_ids:
            vinyl_release = VinylRelease.objects.get(id=i)
            vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
            for j in vinyl_plates:
                #region member_plates
                if len(MemberPlate.objects.filter(member=member, vinyl_release=j.related_release)) >= 1:
                    member_plate = MemberPlate.objects.get(
                        member = member,
                        vinyl_release = j.related_release
                    )
                else:
                    member_plate = None
                vinyl_plate = j
                vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
                #region stock item
                if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                    stock_item = StockItem.objects.get(
                        library = library,
                        vinyl_release = vinyl_plate.related_release
                    )
                else:
                    stock_item = None
                #endregion
                #region release title long
                if vinyl_plate.related_release != None:
                    release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                    if len(release_title_long) >= 60:
                        release_title_long = release_title_long[:60] + '...'
                else:
                    release_title_long = ''
                #endregion
                #region plate crate ids
                vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
                vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
                vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
                vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
                #endregion
                all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
        #endregion
    #endregion