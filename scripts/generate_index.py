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
            
            # 使用正则匹配版本号：通常版本号是以数字开头的段落 (例如 -0.2026...)
            # 我们寻找最后一个出现的 "-数字" 结构
            match = re.search(r'-(?=\d)', base_name)
            
            if match:
                # 找到第一个数字出现的位置进行分割
                # 比如 natmapt-client-script-transmission-0.2026.01.24
                # 分割为 name="natmapt-client-script-transmission", ver="0.2026.01.24"
                pos = match.start()
                # 进一步细化：如果后面还有横杠（如带修订号 -r1），需要整体作为版本
                # 官方 APK 标准是：包名-版本-修订号.apk
                # 我们采用从右往左数，通常版本+修订号占后两段，或者版本占最后一段
                
                parts = base_name.split("-")
                # 识别常见的修订号格式 (r + 数字)
                if re.match(r'r\d+', parts[-1]) and len(parts) > 2:
                    name = "-".join(parts[:-2])
                    version = f"{parts[-2]}-{parts[-1]}"
                else:
                    # 如果最后一段不是 r1 这种，那么最后一段就是版本号
                    name = "-".join(parts[:-1])
                    version = parts[-1]
                
                packages[name] = version
            else:
                # 兜底方案
                parts = base_name.rsplit("-", 1)
                if len(parts) == 2:
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
