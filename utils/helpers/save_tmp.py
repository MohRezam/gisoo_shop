import uuid


def save_temp_file(file):
    path = f"/tmp/{uuid.uuid4()}_{file.name}"
    with open(path, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return path


def handle_uploaded_files(files):
    temp_files = {
        "image": save_temp_file(files["image"]),
        "detail_image": (
            save_temp_file(files["detail_image"]) if "detail_image" in files else None
        ),
        "list_images": [save_temp_file(f) for f in files.getlist("list_image")],
    }
    return temp_files
