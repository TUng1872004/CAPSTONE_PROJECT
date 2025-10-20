from datetime import timedelta
import io

class Minio():
    def __init__(self, minio_client=None):
        self.minio_client = minio_client

    def add_user_avatar(self, idinfo, response) -> str:
        picture_data = response.content
        picture_stream = io.BytesIO(picture_data)
        # ko có thì fallback image/jpeg
        content_type = response.headers.get("Content-Type", "image/jpeg")

        # save to minio
        self.minio_client.put_object(
            bucket_name="avatars",
            object_name=f"{idinfo['sub']}.jpg",
            data=picture_stream,
            length=len(picture_data),
            content_type=content_type,
        )
        url = self.minio_client.presigned_get_object(
            bucket_name="avatars",
            object_name=f"{idinfo['sub']}.jpg",
            expires=timedelta(days=7)  # 7 days
        )

        return url
