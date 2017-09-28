#apply patches from the patches folder
from patches import extfile_patch

extfile_patch.patch_fs_paths_and_pack()
extfile_patch.patch_extfile_extension()
