import glob
import shutil

# port_man = glob.glob('data/portuguese/manual_download_portuguese/*/*.pdf')
# for file in port_man:
#     shutil.copy(file, 'data/portuguese/total_portuguese')

# port_dnld = glob.glob('data/portuguese/Portuguese.Data/PDF/*/*.pdf')
# for file in port_dnld:
#     shutil.copy(file, 'data/portuguese/total_portuguese')

spn_man = glob.glob('data/spanish/manual_download_spanish/*/*.pdf')
for file in spn_man:
    shutil.copy(file, 'data/spanish/total_spanish')

span_dnld = glob.glob('data/spanish/Spanish.Data/PDF/*/*.pdf')
for file in span_dnld:
    shutil.copy(file, 'data/spanish/total_spanish')