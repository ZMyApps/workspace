import plistlib
import zipfile


def extract_ipa_metadata(ipa_path: str) -> dict:
    with zipfile.ZipFile(ipa_path, "r") as zf:
        plist_paths = [
            name
            for name in zf.namelist()
            if name.startswith("Payload/")
            and name.endswith(".app/Info.plist")
            and name.count("/") == 2
        ]
        plist_data = zf.read(plist_paths[0])
    info = plistlib.loads(plist_data)
    return {
        "bundleIdentifier": info["CFBundleIdentifier"],
        "version": info["CFBundleShortVersionString"],
    }
