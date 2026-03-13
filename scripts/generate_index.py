import json
import os
from collections import OrderedDict

def generate_index(target_dir, architecture):
    packages = {}
    
    pkg_file_path = os.path.join(target_dir, "Packages")
    if os.path.exists(pkg_file_path):
        with open(pkg_file_path, "r", encoding="utf-8") as f:
            current_name = None
            for line in f:
                if line.startswith("Package: "):
                    current_name = line.split(":", 1)[1].strip()
                elif line.startswith("Version: ") and current_name:
                    version = line.split(":", 1)[1].strip()
                    packages[current_name] = version
                    current_name = None

    apk_files = [f for f in os.listdir(target_dir) if f.endswith(".apk")]
    if apk_files:
        for f in apk_files:
            base_name = f.rsplit(".apk", 1)[0]
            parts = base_name.split("-")
            if len(parts) >= 3:
                revision = parts[-1]
                version_num = parts[-2]
                name = "-".join(parts[:-2])
                full_version = f"{version_num}-{revision}"
                packages[name] = full_version
            elif len(parts) == 2:
                packages[parts[0]] = parts[1]

    if packages:
        data = OrderedDict()
        data["version"] = 2
        data["architecture"] = architecture
        sorted_packages = dict(sorted(packages.items()))
        data["packages"] = sorted_packages
        
        output_path = os.path.join(target_dir, "index.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Generated index.json for {architecture} ({len(packages)} pkgs)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        generate_index(sys.argv[1], sys.argv[2])
