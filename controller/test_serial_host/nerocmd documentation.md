Usage:
  _______________
 | List available| --listdrives
 | drives        |
 |_______________|
 | Obtain drive  | --driveinfo --drivename <name>
 | info          |
 |_______________|
 | Obtain disc   | --discinfo --drivename <name> [--extended] [--read_isrc] [--cd_text]
 | info          |
 |_______________|
 | Write         | --write --drivename <name> [--real] [--tao]
 | ISO/Audio Disc| [--artist <artist>] [--title <title>] [--speed <speed>]
 |               | [--audio] <audio files> [--cdextra] [--iso <volumename>]
 |               | [--iso-no-joliet] [--iso-mode2] [--speedtest]
 |               | [--enable_abort] [--close_session] [--detect_non_empty_disc]
 |               | [--cd_text] [--underrun_prot]
 |               | [--import_udf] [--import_vms_session]
 |               | [--use_rockridge] [--create_iso_fs] [--create_udf_fs]
 |               | [--disable_eject] [--verify] [--dvd] [--use_allspace]
 |               | <disk file> ...
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--output_image <filename>]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |               | [--booktype_dvdrom] [--layerbreak <sectornumber>]
 |               | [--udf_revision <value>] [--udf_partition_type <type>]
 |               | [--allowunicodelabel] [--spare_area <option>]
 |               |
 |               | NOTE: At least one audio file or one disk file needs to be
 |               | specified!
 |_______________|
 | Write         | --write --drivename <name> [--real] [--tao]
 | Video CD      | --videocd [--speed <speed>] [--speedtest] [--enable_abort]
 |               | [--close_session] <video files> [--iso <volumename>]
 |               | [--iso-no-joliet] [--iso-mode2] [--speedtest]
 |               | [--enable_abort] [--close_session] [--detect_non_empty_disc]
 |               | [--underrun_prot] [--disable_eject] <disk file>...
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--temp_path <path>] [--output_image <filename>]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |_______________|
 | Write Super   | --write --drivename <name> [--real] [--tao]
 | Video CD      | --svideocd [--speed <speed>] [--speedtest] [--enable_abort]
 |               | [--close_session] <video files> [--iso <volumename>]
 |               | [--iso-no-joliet] [--iso-mode2] [--speedtest]
 |               | [--enable_abort] [--close_session] [--detect_non_empty_disc]
 |               | [--underrun_prot] [--disable_eject] <disk file>...
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--temp_path <path>] [--output_image <filename>]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |_______________|
 | Write image   | --write --drivename <name> [--real] [--tao] [--dvd]
 |               | --image <image filename> [--speed <speed>] [--speedtest]
 |               | [--enable_abort] [--close_session] [--detect_non_empty_disc]
 |               | [--underrun_prot] [--disable_eject]
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--output_image <filename>]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |               | [--booktype_dvdrom] [--layerbreak <sectornumber>]
 |               | [--spare_area <option>]
 |_______________|
 | Write         | --write --drivename <name> [--real] [--tao]
 | freestyle disc| [--artist <artist>] [--title <title>] [--speed <speed>]
 |               | [--cdextra] [--iso <volumename>]
 |               | [--freestyle_mode1 <filename>]
 |               | [--freestyle_mode2 <filename>]
 |               | [--freestyle_audio <filename>]
 |               | [--iso-no-joliet] [--iso-mode2] [--speedtest]
 |               | [--enable_abort] [--close_session] [--detect_non_empty_disc]
 |               | [--cd_text] [--underrun_prot]
 |               | [--import_udf] [--import_vms_session]
 |               | [--use_rockridge] [--create_iso_fs] [--create_udf_fs]
 |               | [--disable_eject] [--verify] [--use_allspace] <disk file>...
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--output_image <filename>]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |               | [--booktype_dvdrom] [--layerbreak <sectornumber>]
 |               | [--udf_revision <value>] [--udf_partition_type <type>]
 |               | [--spare_area <option>]
 |               |
 |               | NOTE: Any number of freestyle tracks can be specified up to
 |               | a maximum of 99 tracks.!
 |_______________|
 | Copy disc     | --write --drivename <name> --disccopy <source drivename>
 |               | [--real] [--tao][--enable_abort] [--detect_non_empty_disc]
 |               | [--underrun_prot] [--disable_eject] [--verify]
 |               | [--force_erase_disc] [--nero_log_timestamp]
 |               | [--output_image <filename>]
 |               | [--copy_temp_image_path <path>] [--copy_keep_temp_image]
 |               | [--copy_retries <num>] [--copy_read_speed <speed>] [--dvd]
 |               | [--copy_continue_on_data_read_errors] [--copy_raw_read_mode]
 |               | [--copy_abort_on_audio_read_errors] [--copy_read_isrc]
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>] [--spare_area <option>]
 |_______________|
 | Estimate      | --estimate --drivename <name> [--tao]
 | track size    | [--iso <volumename>] [--iso-no-joliet] [--iso-mode2]
 |               | [--close_session] [--import_udf] [--import_vms_session]
 |               | [--use_rockridge] [--create_iso_fs] [--create_udf_fs]
 |               | [--disable_eject] [--dvd] [--use_allspace]
 |               | [--estimate_no_fs_overhead] [--estimate_no_data]
 |               | [--estimate_no_exact_size] <disk file> ...
 |               | [--udf_revision <value>] [--udf_partition_type <type>]
 |_______________|
 | Read audio    | --read --drivename <name> [--read_speed <speed>]
 | track(s)      | --XY <filename> [-XY <filename> ...]
 |_______________|
 | List audio    | --listformats
 | formats       |
 |_______________|
 | Erase disc    | --erase [--entire] --drivename <name>
 |               | [--userobot <robotname>] [--robot_port_type <type>]
 |               | [--robot_port_num <num>] [--set_robot_flag <flagtype>]
 |               | [--robot_flag_value <value>]
 |_______________|
 | Eject disc    | --eject --drivename <name>
 |_______________|
 | Load disc     | --load --drivename <name>
 |_______________|
 | Obtain image  | --imageinfo <filename>
 | file disc info|
 |_______________|
 | Version info  | --version
 |_______________|
 | List available| --listrobot_port_types
 | robot port    |
 | types         |
 |_______________|
 | List available| --listrobots
 | robot drivers |
 |_______________|
 | List available| --listrobotflags
 | robot options |
 |_______________|
 | Set device    | --deviceoption --drivename <name>
 | option        | [--layerbreak <sectornumber>]
 |_______________|

 Each command supports the following switches: [--no_error_log],
 [--error_log <log filename>], [--no_user_interaction] and [@parameter_file]

  _______________
 | --write       | Burn disc.
 |_______________|
 | --drivename   | <name> is either the "full name" of the drive or the
 | <name>        | drive letter.
 |_______________|
 | --real        | Forces the disc to be actually burned. If --real is not
 |               | specified the process is only simulated.
 |_______________|
 | --tao         | Disc is burned in TAO mode (DAO is default).
 |_______________|
 | --dao96       | Disc is burned in DAO/96 mode (DAO is default).
 |_______________|
 | --burnproof   | Obsolete option, use --underrun_prot instead.
 |_______________|
 | --artist      | <artist> is the artist name as to be written on disc.
 | <artist>      |
 |_______________|
 | --title       | <title> is the title to be written on disc.
 | <title>       |
 |_______________|
 | --read_speed  | <speed> is the speed at which the audio tracks will be read
 | <speed>       | (in x150KB/s).
 |_______________|
 | --speed       | <speed> is the speed at which the disc will be burned
 | <speed>       | (for CD in x150 KB/s and for DVD in x1,385 KB/s).
 |_______________|
 | --speed_in_   | <speed> is the speed at which the disc will be burned
 |  kbps <speed> | (in KB/s).
 |_______________|
 | --audio       | The disc is burned with audio information.
 |_______________|
 | <audio files> | <audio files> is a list of audio files (wav, mp3, wma, pcm).
 |_______________|
 | --cdextra     | Use the CDExtra feature.
 |_______________|
 | --iso         | <volume name> is the volume name to be stored on the disc.
 | <volume name> |
 |_______________|
 |--iso-no-joliet| Do not use Joliet format.
 |_______________|
 | --iso-mode2   | Burn the disc using mode 2.
 |_______________|
 | --speedtest   | Perform speed test before burning.
 |_______________|
 | --enable_abort| Notify which operations can and which cannot be aborted.
 |_______________|
 |--close_session| Close the session, not the whole disc.
 |_______________|
 |--detect_non_  | Detect if the disc for burning is a non empty
 | empty_disc    | RW media and offer to take certain actions.
 |_______________|
 | --cd_text     | Write or read CD text (if supported by device).
 |_______________|
 | --videocd     | Burn a Video CD.
 |_______________|
 | --svideocd    | Burn a Super Video CD.
 |_______________|
 | <video files> | <video files> represents a list of video files (mpeg, jpeg).
 |_______________|
 | --image       | <filename> is the filename to the image file.
 | <filename>    |
 |_______________|
 | --read        | Read audio track(s).
 |_______________|
 | --XY          | XY is the number of the audio track that is to be saved to
 | <filename>    | <filename>.
 |_______________|
 | --erase       | Erase an RW media.
 |_______________|
 | --entire      | Erase the entire disc (the default is quick erase).
 |_______________|
 | --eject       | Eject disc.
 |_______________|
 | --load        | Load disc.
 |_______________|
 | --version     | Print NeroAPI version information.
 |_______________|
 | --underrun_   | Protect from underrun condition.
 |   prot        |
 |_______________|
 | --stream_     | Set stream recording mode for real time recording.
 |   recording   |
 |_______________|
 | --use_        | Use rockridge format.
 |   rockridge   |
 |_______________|
 | --create      | Create ISO filesystem.
 |   _iso_fs     |
 |_______________|
 | --create      | Create UDF filesystem.
 |   _udf_fs     |
 |_______________|
 | --dvdvideo    | Perform reallocation of files in VIDEO_TS
 |   _realloc    | directory.
 |_______________|
 | --dvdvideo    | Create DVD-Video compatible disc.
 |   _cmpt       | --create_iso_fs --create_udf_fs and
 |               | --iso-no-joliet also need to be specified.
 |_______________|
 | --import      | Obsolete option; will be ignored.
 |   rockridge   |
 |_______________|
 | --import_udf  | Import UDF format.
 |_______________|
 | --import_vms  | Import Virtual Multisession (VMS) session
 |   _session    | (session number treated as VMS session).
 |_______________|
 | --import      | Obsolete option; will be ignored.
 |   _iso_only   |
 |_______________|
 | --import      | Import session number (if omitted, the last
 |  <session #>  | session is imported).
 |_______________|
 | --prefer      | Obsolete option; will be ignored.
 |   _rockridge  |
 |_______________|
 | --freestyle_  | Burn the file in mode 1.
 |  mode1        |
 |_______________|
 | --freestyle_  | Burn the file in mode 2.
 |  mode2        |
 |_______________|
 | --freestyle_  | Burn the file in audio mode.
 |  audio        |
 |_______________|
 | --disable_    | Disables disc ejection after burn completion.
 |   eject       |
 |_______________|
 | --verify      | Verify ISO filesystem after writing.
 |_______________|
 | --dvd_high_   | Used for better compatibility of burned DVDs.
 |  compatibility| At least 1GB will be written.
 |_______________|
 | --dvd         | Select DVD as media type.
 |_______________|
 | --recursive   | Do a recursive file search.
 |_______________|
 | --force_erase_| Delete disc without user interaction
 |   disc        | (requires --detect_non_empty_disc).
 |_______________|
 | --nero_log_   | Add a timestamp to the log's file name.
 |   timestamp   |
 |_______________|
 | --temp_path   | Specify a temporary path for Video CD files.
 |_______________|
 | --media_type  | Specify a media type (combine with +)
 |   <type>      |  media_cd, media_ddcd, media_dvd_m, media_dvd_p,
 |               |  media_dvd_any, media_dvd_ram, media_ml, media_mrw,
 |               |  media_no_cdr, media_no_cdrw, media_cdrw, media_cdr
 |               |  media_dvd_rom, media_cdrom, media_no_dvd_m_rw,
 |               |  media_no_dvd_m_r, media_no_dvd_p_rw,
 |               |  media_no_dvd_p_r, media_dvd_m_r, media_dvd_m_rw,
 |               |  media_dvd_p_r, media_dvd_p_rw, media_fpacket,
 |               |  media_vpacket, media_packetw, media_hdb or
 |               |  media_dvd_p_r9, media_dvd_m_r9, media_dvd_any_r9,
 |               |  media_dvd_p_rw9, media_dvd_m_rw9, media_dvd_any_rw9,
 |               |  media_bd_rom, media_bd_r, media_bd_re, media_bd,
 |               |  media_bd_r_dl, media_bd_re_dl, media_bd_any,
 |               |  media_hd_dvd_rom, media_hd_dvd_r, media_hd_dvd_rw,
 |               |  media_hd_dvd, media_hd_dvd_ram, media_hd_dvd_r_dl,
 |               |  media_hd_dvd_any_r, media_hd_dvd_any.
 |_______________|
 | --no_user_    | Allow the whole process to take place with no user
 |  interaction  | interaction (no questions asked).
 |_______________|
 | --output_image| Specify output image file name if image recorder is used
 |               | to avoid prompting for filename.
 |_______________|
 | --use_allspace| Use all space on the media.
 |_______________|
 | --relax_joliet| Relax Joliet file name length limitations.
 |_______________|
 | --japanese_   | CD Text is treated as Japanese CD Text (must include
 |  cd_text      | --cd_text as well).
 |_______________|
 |--disable_eject| Do not eject the RW media after erasing it.
 | _after_erase  |
 |_______________|
 | --force_eject | Force disc ejection after erasing the RW media.
 |  _after_erase |
 |_______________|
 | --system_     | <text> is the "system identifier" of an ISO track.
 |  identifier   |
 |  <text>       |
 |_______________|
 | --volume_set  | <text> is the "volume set" of an ISO track.
 |  <text>       |
 |_______________|
 | --publisher   | <text> is the "publisher" of an ISO track.
 |  <text>       |
 |_______________|
 | --data_       | <text> is the "data preparer" of an ISO track.
 |preparer <text>|
 |_______________|
 | --application | <text> is the "application" of an ISO track.
 |  <text>       |
 |_______________|
 | --copyright   | <text> is the "copyright" of an ISO track.
 |  <text>       |
 |_______________|
 | --abstract    | <text> is the "abstract" of an ISO track.
 |  <text>       |
 |_______________|
 |--bibliographic| <text> is the "bibliographic" of an ISO track.
 |  <text>       |
 |_______________|
 | --backup      | Replace imported files only if newer are found.
 |_______________|
 | --booktype    | The book type of a burned DVD will be set to
 |   _dvdrom     | DVD-ROM.
 |_______________|
 | --no_booktype | Do not change the book type of a DVD even if the default
 |   _change     | setting is to change the book type to DVD-ROM.
 |_______________|
 | --estimate_no | Do not include the file system overhead in calculation.
 |   fs_overhead |
 |_______________|
 | --estimate_no | Do not include data in calculation.
 |   data        |
 |_______________|
 | --estimate_no | Do not calculate the exact size (quicker).
 |   exact_size  |
 |_______________|
 | --cd_overburn | Specify CD overburn size in blocks.
 |   <size>      |
 |_______________|
 | --dvd_overburn| Specify DVD overburn size in blocks.
 |   <size>      |
 |_______________|
 | --relative_ov | Specify relative CD overburn size in blocks.
 | erburn <size> |
 |_______________|
 | --copy_temp_  | Specify temporary image path for a disc copy operation.
 |   image_path  | Omitting it causes on-the-fly copy.
 |_______________|
 | --copy_keep_  | Do not delete temporary image path after disc copy
 |   temp_image  | operation.
 |_______________|
 | --copy_retries| Specify retry count on read errors.
 |   <num>       |
 |_______________|
 | --copy_read_  | Specify disc copy read speed in kb/s.
 |   speed <spd> |
 |_______________|
 | --copy_       | Ignore data errors during disc copy.
 |  continue_on_ | Default is to abort.
 |  data_read_   |
 |  errors       |
 |_______________|
 | --copy_       | Abort on audio errors during disc copy.
 | abort_on_audio| Default is to ignore.
 | read_errors   |
 |_______________|
 | --copy_raw_   | Use raw read mode for disc copy.
 |   read_mode   |
 |_______________|
 | --copy_read_  | Read ISRC and media catalog number during disc copy.
 |   isrc        |
 |_______________|
 | --userobot    | Use robot to move the disc to and from recorder.
 |   <robotname> |
 |_______________|
 | --robot_port_ | Specify the port type the robo is connected to: COM, LPT,
 |   type <type> | USB. Default is COM.
 |_______________|
 | --robot_port_ | Specify the port number the robo is connected to: 1, 2, 3...
 |   num <num>   | Default is 1.
 |_______________|
 | --set_robot_  | Set special robot flag before burning: robo_cleanup,
 |   flag        |  robo_insertcd_retries.
 |   <flagtype>  |
 |_______________|
 | --robot_flag_ | Set value for flag specified above.
 |   value       |
 |   <value>     |
 |_______________|
 | --layerbreak  | Set layer break at specified sector position of layer 0.
 | <sectornumber>| <sectornumber> must be a multiple of 16.
 |_______________|
 | --booktype_   | Set the book type of burnt DVD to DVD-ROM.
 |   dvdrom      |
 |_______________|
 | --udf_revision| Set one of following values for UDF revision:
 |   <value>     | udf_102, udf_150, udf_200, udf_201, udf_250, udf_260.
 |_______________|
 | --udf_parti   | Set one of following values for UDF partition type:
 |   tion_type   | physical, virtual, sparable.
 |   <type>      |
 |_______________|
 |--allowunicode | Burning 16 bit unicode volume labels for DVD-Video
 |  label        |  compatible compilations
 |_______________|
 | --spare_area  | Define if spare area on BD should be allocated or not.
 |     <option>  | The option values: no_action, allocate, no_allocate.
 |_______________|
 | --extended    | Get extended CD info like file system type of
 |               |  particular track
 |_______________|
 | --read_isrc   | Also read ISRC if disc info requested
 |_______________|
 | --boot_image  | Provide a boot image for the bootable disc.
 | <filename>    | <filename> path to the boot image.
 |_______________|
 |--boot_platform| Target platform of the boot image.
 | <plattform>   | <plattform> possible platform parameter are:
 |               | x86, ppc, mac, efi
 |_______________|
 |--boot_message | Optional boot message.
 | <message>     | <message> message to be shown.
 |_______________|
 | --boot_type   | Declares the type of the boot image
 |    <type>     | <type> possible types are:
 |               | noemulation, 1_22MB, 1_44MB, 2_88MB, hdd
 |_______________|
 |--boot_loadsize| Declares the size of the boot image
 |    <size>     | <size>
 |_______________|
 | @param_file   | param_file contains the command line arguments.
 |_______________|