import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


def subir_archivo(file, carpeta: str, public_id: str) -> str:
    """Sube un archivo a Cloudinary y devuelve la URL pública."""
    resultado = cloudinary.uploader.upload(
        file,
        folder=carpeta,
        public_id=public_id,
        overwrite=True,
        resource_type="auto",  # acepta imágenes y PDFs
    )
    return resultado["secure_url"]
