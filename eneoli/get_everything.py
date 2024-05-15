import config_private
from pyzotero import zotero
pyzot = zotero.Zotero(config_private.zotero_group_nr, 'group', config_private.zotero_api_key)

everything = pyzot.everything(pyzot.items(tag="processed_fulltext"))

print(str(len(everything)))