import os
import tarfile
import tempfile
import glob

APK_DIR = "./"            # folder containing your .apk files
OUTPUT_DIR = "./db" # where the apk db will be generated

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_pkginfo(pkginfo_path):
    pkg = {}
    with open(pkginfo_path, "r") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                pkg[k.strip()] = v.strip()
    return pkg

installed_path = os.path.join(OUTPUT_DIR, "installed")
with open(installed_path, "w") as installed_file:
    for apk_path in glob.glob(os.path.join(APK_DIR, "**/*.apk"), recursive=True):
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with tarfile.open(apk_path, "r:*") as tar:
                    tar.extract(".PKGINFO", path=tmpdir)
            except KeyError:
                print(f"[!] .PKGINFO not found in {apk_path}, skipping.")
                continue
            except Exception as e:
                print(f"[!] Error extracting {apk_path}: {e}")
                continue

            pkginfo_path = os.path.join(tmpdir, ".PKGINFO")
            if not os.path.exists(pkginfo_path):
                print(f"[!] .PKGINFO missing after extraction for {apk_path}, skipping.")
                continue

            pkg = parse_pkginfo(pkginfo_path)

            installed_file.write("C:Q1\n")
            installed_file.write(f"P:{pkg.get('pkgname')}\n")
            installed_file.write(f"V:{pkg.get('pkgver')}\n")
            installed_file.write(f"A:{pkg.get('arch','x86_64')}\n")
            installed_file.write(f"S:{pkg.get('size','0')}\n")
            installed_file.write(f"I:{pkg.get('installed_size','0')}\n")
            installed_file.write(f"T:{pkg.get('pkgdesc','')}\n")
            installed_file.write(f"U:{pkg.get('url','')}\n")
            installed_file.write(f"L:{pkg.get('license','')}\n")
            installed_file.write(f"o:{pkg.get('origin',pkg.get('pkgname'))}\n")
            installed_file.write(f"m:{pkg.get('maintainer','')}\n")
            installed_file.write(f"t:{pkg.get('builddate','1722123456')}\n")
            # Fake checksum
            installed_file.write(f"c:cafebabe1234567890deadbeef1234567890abcd\n")
            installed_file.write("\n")

            print(f"[+] Processed {apk_path}")

# Create empty triggers and lock files
open(os.path.join(OUTPUT_DIR, "triggers"), "w").close()
open(os.path.join(OUTPUT_DIR, "lock"), "w").close()

print(f"[✅] APK DB generation complete at {OUTPUT_DIR}")

