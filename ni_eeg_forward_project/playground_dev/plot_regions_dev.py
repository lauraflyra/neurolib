import mne
from ni_eeg_forward_project.util import plot_glassbrain_projections, get_labels_of_points
import matplotlib.pyplot as plt
import numpy as np

fname = "../../neurolib/data/datasets/eeg_fsaverage/fsaverage_fwd_sol/fsaverage_default-fwd.fif"
fwd = mne.read_forward_solution(fname)

hem = fwd['src'][0]
dip_pos = hem['rr'][hem['vertno']]*1e3  # The position of the dipoles.

points_found, label_codes, label_strings = get_labels_of_points(dip_pos, atlas="aal2")
print("valid points: ", sum(points_found))

#region_label = 6202
#region_name = "Parietal_Inf_R"
region_label = 4112#np.max(label_codes)
region_name = ""


fig = plot_glassbrain_projections(fwd, label_codes, region_label, region_name)
plt.show()
