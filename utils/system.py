import shutil
import sys


def check_dependencies():
    required_apps = ["mkvmerge"]
    missing_apps = [app for app in required_apps if not shutil.which(app)]

    if missing_apps:
        print("Следующие приложения не найдены:")
        for app in missing_apps:
            print(f"- {app}")
        print("Пожалуйста, установите их и попробуйте снова.")
        sys.exit(1)
